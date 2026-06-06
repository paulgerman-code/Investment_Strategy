"""
Entry script that builds a historical portfolio-weights file from the enriched
data produced by the Data Curator step.

Strategy summary
----------------
Selection
    On each trading day T, stocks are eligible if:
      - the 50/200-day SMA crossover signal (c_sma_50d_200d_signal) equals 1
        on T-1 (bullish trend);
      - single-day traded value (c_daily_traded_value_1d) >= $10 M on T-1;
      - adjusted close is valid and positive on T (tradability guard);
      - the ticker is not in the excluded set (delisted or being force-removed).
    The top MAX_POSITIONS stocks are then selected by 63-day average traded
    value (c_daily_traded_value_63d), descending.

Market-regime handling
    When fewer than MIN_ELIGIBLE_STOCKS (20) stocks pass the filters, the
    portfolio switches to 100 % SPY (bear-market / low-signal regime). It
    exits back to stocks only when eligible stocks >= REENTRY_THRESHOLD (25),
    providing hysteresis to avoid excessive whipsawing at the boundary.

Sizing
    Weights are proportional to 63-day average traded value among the selected
    stocks, then capped at MAX_WEIGHT (20 %) per position, with the excess
    redistributed proportionally until all weights are within the cap.

Timing
    A new portfolio is recorded whenever:
      - the set of selected top-N stocks changes;
      - the portfolio transitions into or out of the SPY regime;
      - a currently held stock must be force-sold due to delisting / becoming
        untradable (sold on T-1, the last healthy day before data disappears).

Portfolio construction
    All selection inputs (signal, traded value, benchmark membership) are read
    from T-1 close so that no future information is used. The adjusted close is
    read from T only as a tradability guard. Each rebalance is recorded under
    its signal date (T-1) and then shifted by one NYSE trading day to produce
    the implementation date T in the output file.

Output
    Portfolio_Construction/portfolio_weights.csv
        Rows  = tickers (alphabetical), always including SPY.
        Columns = implementation dates of rebalance events (YYYY-MM-DD).
        Values  = portfolio weights rounded to 9 decimal places.
        Dates with no rebalance are omitted.
"""

import pathlib

import numpy
import pandas
import QuantLib as ql


# -------------------------------------------------------------------
# PATHS
# -------------------------------------------------------------------
DATA_DIR = pathlib.Path(r"Data_Curator")        # enriched CSVs from the Data Curator step
CONFIG_DIR = pathlib.Path(r"Config")             # Excel config and .env files
OUTPUT_DIR = pathlib.Path(r"Portfolio_Construction")   # weights CSV written here
BENCHMARK_DIR = pathlib.Path(r"Benchmark_Portfolios")  # optional benchmark holdings CSV

# -------------------------------------------------------------------
# STRATEGY PARAMETERS
# -------------------------------------------------------------------
MAX_POSITIONS = 20          # maximum number of stocks held at any time
MAX_WEIGHT = 0.20           # maximum weight per position (20 %)
MIN_DAILY_TRADED_VALUE = 10_000_000   # minimum single-day traded value for eligibility ($10 M)
SPY_TICKER = "SPY"          # fallback ETF used during bear-market / low-signal regime

# Hysteresis thresholds for the SPY regime:
#   enter SPY when eligible stocks < MIN_ELIGIBLE_STOCKS
#   exit  SPY when eligible stocks >= REENTRY_THRESHOLD
MIN_ELIGIBLE_STOCKS = 20
REENTRY_THRESHOLD = 25

# Column names as they appear in the Data Curator output CSVs
COL_DATE = "m_date"
COL_TICKER = "Ticker"
COL_SIGNAL = "c_sma_50d_200d_signal"           # 1 = bullish crossover, 0 = otherwise
COL_TRADED_VALUE_1D = "c_daily_traded_value_1d"   # single-day traded value (liquidity floor)
COL_TRADED_VALUE_63D = "c_daily_traded_value_63d" # 63-day avg traded value (ranking & sizing)
COL_CLOSE = "m_close_dividend_and_split_adjusted" # adjusted close (tradability guard)
COL_CLOSE_RAW = "m_close_split_adjusted"          # split-adjusted close (delisting detection)
COL_VOLUME = "m_volume_split_adjusted"            # split-adjusted volume (delisting detection)

# Only these columns are needed from each CSV. Passing this list to
# `read_csv(usecols=...)` avoids loading the ~200 unused columns per ticker
# and keeps peak memory proportional to what the strategy actually consumes.
FEATURE_COLUMNS: list[tuple[str, str]] = [
    (COL_SIGNAL, "Signal"),
    (COL_TRADED_VALUE_1D, "Traded-value (1-day)"),
    (COL_TRADED_VALUE_63D, "Traded-value (63-day)"),
    (COL_CLOSE, "Close price (adjusted)"),
    (COL_CLOSE_RAW, "Close price (raw)"),
    (COL_VOLUME, "Volume"),
]
REQUIRED_LOAD_COLUMNS: list[str] = [COL_DATE] + [col for col, _ in FEATURE_COLUMNS]

# Delisting / untradable detection: flag a ticker when more than
# DELIST_MISSING_THRESHOLD of the last DELIST_LOOKBACK_DAYS days
# have missing raw close or zero volume.
DELIST_LOOKBACK_DAYS = 21
DELIST_MISSING_THRESHOLD = 0.05

# Backtest window — PORTFOLIO_END is the last signal date (not the last trade date).
# The last output column will be the next NYSE trading day after PORTFOLIO_END.
PORTFOLIO_START = pandas.Timestamp("2015-01-01")
PORTFOLIO_END = pandas.Timestamp("2026-04-17")


# -------------------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------------------

def _read_config_tickers() -> list[str]:
    # Read the ordered ticker universe from the Excel config so we only
    # load CSVs for tickers the strategy is configured to trade.
    config_path = CONFIG_DIR / "data_curator_parameters.xlsx"
    if not config_path.exists():
        return []
    try:
        frame = pandas.read_excel(config_path, sheet_name="Identifiers")
        tickers = (
            frame["main_identifier"]
            .dropna()
            .astype(str)
            .str.strip()
            .loc[lambda s: s != ""]
            .tolist()
        )
        print(f"  Config tickers: {len(tickers)}")
        return tickers
    except Exception:
        return []


def load_benchmark_holdings() -> pandas.DataFrame | None:
    # Load the optional benchmark holdings matrix (date × ticker).
    # When present, only tickers held in the benchmark on T-1 are eligible
    # for selection, which constrains the strategy to the benchmark universe.
    csv_path = BENCHMARK_DIR / "benchmark_portfolio_holdings.csv"
    if not csv_path.exists():
        print(f"  Benchmark file not found: {csv_path} — benchmark filter disabled.")
        return None
    try:
        df = pandas.read_csv(csv_path, index_col=0, low_memory=False)
        df.index = pandas.to_datetime(df.index, format="mixed", dayfirst=False)
        df.index.name = COL_DATE
        df = df.sort_index()
        print(f"  Benchmark: {df.shape[1]} tickers × {len(df):,} dates")
        print(f"  Benchmark range: {df.index[0].date()} → {df.index[-1].date()}")
        return df
    except Exception as exc:
        print(f"  WARNING: Could not load benchmark file: {exc} — benchmark filter disabled.")
        return None


def load_data() -> tuple[dict[str, pandas.DataFrame], list[str], list[str]]:
    # Scan DATA_DIR for per-ticker CSVs produced by the Data Curator, then load
    # only the tickers listed in the config (or all CSVs if no config).  Only
    # the columns in REQUIRED_LOAD_COLUMNS are read — the raw CSVs carry ~200
    # fields, and loading them all would balloon peak memory during matrix
    # assembly even though the strategy only consumes six.
    #
    # Returns a dict {ticker: DataFrame indexed by date, columns = features}
    # plus the lists of loaded / missing tickers.  The dict form lets
    # build_matrices() assemble each feature matrix directly via one pandas
    # concat per feature, skipping the long-format concat + pivot_table
    # roundtrip used previously.
    csv_paths = {csv_file.stem: csv_file for csv_file in sorted(DATA_DIR.glob("*.csv"))}
    print(f"  CSV files found: {len(csv_paths)}")

    config_tickers = _read_config_tickers()
    if config_tickers:
        tickers_to_load = [tkr for tkr in config_tickers if tkr in csv_paths]
        missing = [tkr for tkr in config_tickers if tkr not in csv_paths]
        if not tickers_to_load:
            print("  WARNING: No config tickers matched — loading all CSVs.")
            tickers_to_load = list(csv_paths.keys())
            missing = []
    else:
        tickers_to_load = list(csv_paths.keys())
        missing = []

    ticker_frames: dict[str, pandas.DataFrame] = {}
    loaded: list[str] = []
    total_rows = 0
    min_date: pandas.Timestamp | None = None
    max_date: pandas.Timestamp | None = None

    for load_idx, tkr in enumerate(sorted(tickers_to_load)):
        try:
            frame = pandas.read_csv(
                csv_paths[tkr],
                usecols=REQUIRED_LOAD_COLUMNS,
                low_memory=False,
            )
            if load_idx == 0:
                print(
                    f"  Sample: {tkr}.csv | Cols: {len(frame.columns)} "
                    f"(of required {len(REQUIRED_LOAD_COLUMNS)}) | Rows: {len(frame)}"
                )
            frame[COL_DATE] = pandas.to_datetime(
                frame[COL_DATE], format="mixed", dayfirst=False
            )
            frame = frame.set_index(COL_DATE).sort_index()

            # Preserve the pivot_table(aggfunc="last") dedup semantics of the
            # original implementation — CSVs shouldn't have duplicate dates,
            # but guard against it explicitly to keep behavior identical.
            if frame.index.has_duplicates:
                frame = frame.groupby(level=0).last()

            ticker_frames[tkr] = frame
            loaded.append(tkr)

            total_rows += len(frame)
            if not frame.empty:
                frame_min = frame.index.min()
                frame_max = frame.index.max()
                min_date = frame_min if min_date is None else min(min_date, frame_min)
                max_date = frame_max if max_date is None else max(max_date, frame_max)
        except Exception as exc:
            print(f"  ERROR {tkr}.csv: {exc}")
            missing.append(tkr)

    if not ticker_frames:
        raise RuntimeError("No data loaded.")

    print(f"  Loaded: {len(loaded)} tickers | Missing: {len(missing)}")
    print(f"  Total rows: {total_rows:,}")
    if min_date is not None and max_date is not None:
        print(f"  Date range: {min_date.date()} → {max_date.date()}")

    return ticker_frames, loaded, missing


def validate_features(ticker_frames: dict[str, pandas.DataFrame]) -> None:
    # Abort early if any required signal or price column is absent or all-null,
    # so the error is clear rather than surfacing as a silent NaN downstream.
    # Operates on the per-ticker frames produced by load_data() so no
    # long-format concat is needed just to count non-nulls.
    if not ticker_frames:
        raise ValueError("No ticker data provided to validate.")

    sample_columns = next(iter(ticker_frames.values())).columns
    for col, label in FEATURE_COLUMNS:
        if col not in sample_columns:
            raise ValueError(
                f"{label} column '{col}' not found.  Available: {sorted(sample_columns)}"
            )
        non_null_count = sum(
            int(frame[col].notna().sum()) for frame in ticker_frames.values()
        )
        if non_null_count == 0:
            raise ValueError(f"{label} column '{col}' has no valid data.")
        print(f"  {label}: '{col}' ({non_null_count:,} non-null)")


# -------------------------------------------------------------------
# MATRIX BUILDING
# -------------------------------------------------------------------

def build_matrices(
    ticker_frames: dict[str, pandas.DataFrame],
) -> tuple[
    pandas.DataFrame,
    pandas.DataFrame,
    pandas.DataFrame,
    pandas.DataFrame,
    pandas.DataFrame,
    pandas.DataFrame,
]:
    # Assemble six aligned date × ticker matrices, one per feature.
    #
    # Each ticker's frame is already indexed by date and has exactly the six
    # feature columns loaded, so a per-feature `pandas.concat(dict, axis=1)`
    # with `join='outer'` produces the date × ticker matrix directly and
    # avoids the memory blow-up of `pd.concat(long_frames)` followed by
    # `pivot_table`.  All six matrices end up sharing the same (sorted) index
    # and columns so row[i]/col[j] stay aligned across them — required by the
    # numpy-level row slicing in construct_portfolios().
    print("  Building matrices …")

    pivot_specs = [
        (COL_SIGNAL, "signal"),
        (COL_TRADED_VALUE_1D, "traded_value_1d"),
        (COL_TRADED_VALUE_63D, "traded_value_63d"),
        (COL_CLOSE, "close_adj"),
        (COL_CLOSE_RAW, "close_raw"),
        (COL_VOLUME, "volume"),
    ]

    sorted_tickers = sorted(ticker_frames.keys())
    pivots: dict[str, pandas.DataFrame] = {}
    for col, key in pivot_specs:
        pivots[key] = pandas.concat(
            {tkr: ticker_frames[tkr][col] for tkr in sorted_tickers},
            axis=1,
        ).sort_index()

    # All six matrices are built from the same ticker_frames dict so they
    # already share an identical index (union of ticker dates) and columns
    # (sorted tickers).  Normalise the axes once for safety and to match the
    # sorted ordering guaranteed by the original implementation.
    all_dates = pivots["signal"].index.sort_values()
    all_tickers = pivots["signal"].columns.sort_values()
    for key in pivots:
        pivots[key] = pivots[key].reindex(index=all_dates, columns=all_tickers)

    print(f"  Shape: {len(all_dates):,} dates × {len(all_tickers)} tickers")
    print(f"  Range: {all_dates[0].date()} → {all_dates[-1].date()}")

    return (
        pivots["signal"],
        pivots["traded_value_1d"],
        pivots["traded_value_63d"],
        pivots["close_adj"],
        pivots["close_raw"],
        pivots["volume"],
    )


# -------------------------------------------------------------------
# SELECTION HELPERS
# -------------------------------------------------------------------

def _select_eligible_stocks(
    sig_row: numpy.ndarray,
    tv_1d_row: numpy.ndarray,
    tv_63d_row: numpy.ndarray,
    close_row: numpy.ndarray,
    excluded: set[str],
    tickers: numpy.ndarray,
    benchmark_tickers: set[str] | None = None,
) -> tuple[numpy.ndarray, numpy.ndarray, int]:
    # Build a boolean mask that keeps only stocks meeting all selection criteria:
    #   1. SMA 50/200 crossover signal == 1  (bullish trend)
    #   2. Single-day traded value >= $10 M  (liquidity floor)
    #   3. 63-day average traded value is finite and positive  (ranking input)
    #   4. Adjusted close is finite and positive on trade date  (tradability guard)
    #   5. Not SPY and not in the excluded (delisted / force-removed) set
    #   6. If a benchmark is loaded, must be in the benchmark on T-1
    eligible_mask = (
        (sig_row == 1)
        & (tv_1d_row >= MIN_DAILY_TRADED_VALUE)
        & numpy.isfinite(tv_63d_row)
        & (tv_63d_row > 0)
        & numpy.isfinite(close_row)
        & (close_row > 0)
        & (tickers != SPY_TICKER)
    )
    if excluded:
        exclude_mask = numpy.isin(tickers, list(excluded))
        eligible_mask = eligible_mask & ~exclude_mask
    if benchmark_tickers is not None:
        benchmark_mask = numpy.isin(tickers, list(benchmark_tickers))
        eligible_mask = eligible_mask & benchmark_mask

    eligible_tkrs = tickers[eligible_mask]
    eligible_tv_63d = tv_63d_row[eligible_mask]
    return eligible_tkrs, eligible_tv_63d, len(eligible_tkrs)


def _pick_top_n(
    eligible_tkrs: numpy.ndarray,
    eligible_tv_63d: numpy.ndarray,
) -> frozenset:
    # Rank eligible stocks by 63-day average traded value and keep the top MAX_POSITIONS.
    # Higher traded value → more liquid → higher rank.
    if len(eligible_tkrs) <= MAX_POSITIONS:
        return frozenset(eligible_tkrs)
    top_idx = numpy.argsort(-eligible_tv_63d)[:MAX_POSITIONS]
    return frozenset(eligible_tkrs[top_idx])


# -------------------------------------------------------------------
# REGIME HELPERS
# -------------------------------------------------------------------

def _determine_regime(n_eligible: int, in_spy_regime: bool) -> bool:
    # Use hysteresis to avoid whipsawing at the boundary:
    #   once in SPY regime, stay until n_eligible >= REENTRY_THRESHOLD (higher bar to exit)
    #   once in stock regime, only enter SPY when n_eligible < MIN_ELIGIBLE_STOCKS
    if in_spy_regime:
        return n_eligible < REENTRY_THRESHOLD
    return n_eligible < MIN_ELIGIBLE_STOCKS


def _needs_rebalance(
    prev_selected: frozenset | None,
    current_selected: frozenset,
    should_spy: bool,
    in_spy_regime: bool,
) -> bool:
    # Trigger a rebalance when:
    #   - it is the very first day (prev_selected is None)
    #   - the regime has changed (stock ↔ SPY)
    #   - the composition of the top-N selection has changed
    if prev_selected is None:
        return True
    if should_spy != in_spy_regime:
        return True
    if not should_spy and current_selected != prev_selected:
        return True
    return False


# -------------------------------------------------------------------
# SIZING HELPERS
# -------------------------------------------------------------------

def _cap_and_redistribute(weights: pandas.Series, cap: float) -> pandas.Series:
    # Iteratively enforce the per-position weight cap.
    # Any weight exceeding `cap` is trimmed and the excess is redistributed
    # proportionally to the remaining under-cap positions.
    capped = weights.copy()
    for _ in range(100):
        over = capped > cap
        if not over.any():
            break
        excess = (capped[over] - cap).sum()
        capped[over] = cap
        under = (capped > 0) & (~over)
        if under.sum() == 0 or capped[under].sum() == 0:
            break
        capped[under] += excess * capped[under] / capped[under].sum()
    return capped.clip(upper=cap)


def _compute_stock_weights(
    eligible_tkrs: numpy.ndarray,
    eligible_tv_63d: numpy.ndarray,
) -> pandas.Series:
    # Size positions proportional to 63-day average traded value
    # (more liquid stocks get a larger allocation), then apply the MAX_WEIGHT cap
    # and renormalize so weights sum to 1.0.
    tv_series = pandas.Series(eligible_tv_63d, index=eligible_tkrs)
    tv_positive = tv_series[tv_series > 0].sort_values(ascending=False)

    if tv_positive.empty:
        return pandas.Series(dtype=float)

    selected = tv_positive.head(MAX_POSITIONS)
    raw_weights = selected / selected.sum()
    capped_weights = _cap_and_redistribute(raw_weights, MAX_WEIGHT)
    normalized = capped_weights / capped_weights.sum()
    return normalized[normalized > 1e-10]


# -------------------------------------------------------------------
# DELISTING / UNTRADABLE DETECTION
# -------------------------------------------------------------------

def detect_untradable_tickers(
    close_adj_df: pandas.DataFrame,
    close_raw_df: pandas.DataFrame,
    volume_df: pandas.DataFrame,
    trading_dates: pandas.DatetimeIndex,
) -> tuple[dict[str, pandas.Timestamp], dict[pandas.Timestamp, set[str]]]:
    # Scan every ticker across the full backtest window and flag those that
    # become untradable (delisted, suspended, acquired, etc.).
    #
    # A ticker is flagged on the first date where either:
    #   a) its adjusted close is missing / zero, OR
    #   b) in the trailing DELIST_LOOKBACK_DAYS window, the fraction of days
    #      with missing raw close or zero volume >= DELIST_MISSING_THRESHOLD.
    #
    # Result:
    #   ticker_exclude_from  — first date the ticker must be excluded from selection
    #   force_remove_on      — the trading day before that date, when we must sell
    #                          (last day with a valid price to execute the exit)
    raw_arr = close_raw_df.reindex(index=trading_dates).values
    vol_arr = volume_df.reindex(index=trading_dates).values
    adj_arr = close_adj_df.reindex(index=trading_dates).values
    tickers = close_raw_df.columns.values
    n_dates = len(trading_dates)

    good_day = (
        numpy.isfinite(raw_arr) & (raw_arr > 0)
        & numpy.isfinite(vol_arr) & (vol_arr > 0)
    )
    has_adj = numpy.isfinite(adj_arr) & (adj_arr > 0)

    ticker_exclude_from: dict[str, pandas.Timestamp] = {}
    force_remove_on: dict[pandas.Timestamp, set[str]] = {}

    for col_idx, tkr in enumerate(tickers):
        if tkr == SPY_TICKER:
            continue
        if not has_adj[:, col_idx].any():
            continue   # ticker never had valid data in the window — skip entirely

        first_bad_idx = None
        for row_idx in range(n_dates):
            if not has_adj[row_idx, col_idx]:
                # Adjusted close disappeared — immediate flag
                first_bad_idx = row_idx
                break
            if row_idx >= DELIST_LOOKBACK_DAYS - 1:
                window = good_day[row_idx - DELIST_LOOKBACK_DAYS + 1: row_idx + 1, col_idx]
                missing_frac = 1.0 - window.mean()
                if missing_frac >= DELIST_MISSING_THRESHOLD:
                    # Too many bad days in the trailing window — flag as untradable
                    first_bad_idx = row_idx
                    break

        if first_bad_idx is None:
            continue   # ticker is healthy throughout — nothing to do

        exclude_date = trading_dates[first_bad_idx]

        if first_bad_idx == 0:
            # Bad from the very first day in the window — exclude with no prior sell
            ticker_exclude_from[tkr] = exclude_date
            continue

        # Schedule a forced sell on the last healthy day (one day before bad date)
        remove_date = trading_dates[first_bad_idx - 1]
        ticker_exclude_from[tkr] = exclude_date
        force_remove_on.setdefault(remove_date, set()).add(tkr)

    if ticker_exclude_from:
        print(f"  Untradable tickers detected: {len(ticker_exclude_from)}")
        for tkr in sorted(ticker_exclude_from):
            exc_date_str = ticker_exclude_from[tkr].date()
            remove_date_str = "N/A"
            for report_date, tks in force_remove_on.items():
                if tkr in tks:
                    remove_date_str = report_date.date()
                    break
            print(f"    {tkr}: exclude from {exc_date_str}, force-remove on {remove_date_str}")
    else:
        print("  Untradable tickers detected: 0")

    if force_remove_on:
        print(f"  Force-remove rebalance dates: {len(force_remove_on)}")
        for report_date in sorted(force_remove_on):
            print(f"    {report_date.date()}: remove {sorted(force_remove_on[report_date])}")

    return ticker_exclude_from, force_remove_on


# -------------------------------------------------------------------
# NYSE CALENDAR (QuantLib) — used to advance signal dates to trade dates
# -------------------------------------------------------------------

_NYSE_CALENDAR = ql.UnitedStates(ql.UnitedStates.NYSE)


def _next_trading_date(date: pandas.Timestamp) -> pandas.Timestamp:
    # Return the next NYSE business day after `date`.
    # Used to convert a signal date (T) into its implementation date (T+1).
    ql_date = ql.Date(date.day, date.month, date.year)
    next_ql = _NYSE_CALENDAR.advance(ql_date, 1, ql.Days)
    return pandas.Timestamp(next_ql.year(), next_ql.month(), next_ql.dayOfMonth())


# -------------------------------------------------------------------
# MAIN LOOP — event-driven portfolio construction
# -------------------------------------------------------------------

def construct_portfolios(
    signal_df: pandas.DataFrame,
    tv_1d_df: pandas.DataFrame,
    tv_63d_df: pandas.DataFrame,
    close_adj_df: pandas.DataFrame,
    close_raw_df: pandas.DataFrame,
    volume_df: pandas.DataFrame,
    benchmark_df: pandas.DataFrame | None = None,
) -> dict[pandas.Timestamp, pandas.Series]:
    # Walk every trading day T in [PORTFOLIO_START, PORTFOLIO_END + 1 day].
    # On each day we read T-1 signals and T close prices, then decide whether
    # to rebalance.  The loop runs one extra day past PORTFOLIO_END so that the
    # signal at PORTFOLIO_END close is captured and produces an output column
    # for the next trading day after PORTFOLIO_END.
    loop_end = _next_trading_date(PORTFOLIO_END)
    date_mask = (signal_df.index >= PORTFOLIO_START) & (signal_df.index <= loop_end)
    trading_dates = signal_df.index[date_mask]
    if trading_dates.empty:
        raise RuntimeError(
            f"No trading dates in [{PORTFOLIO_START.date()}, {PORTFOLIO_END.date()}]"
        )

    print(f"  Trading days: {len(trading_dates):,}")
    print(f"  Range:        {trading_dates[0].date()} → {trading_dates[-1].date()}")
    print(f"  SPY entry:    n_eligible < {MIN_ELIGIBLE_STOCKS}")
    print(f"  SPY exit:     n_eligible >= {REENTRY_THRESHOLD}")
    print(f"  Benchmark filter: {'enabled' if benchmark_df is not None else 'disabled'}")

    # Pre-compute the full list of untradable tickers and the dates on which
    # they must be force-sold, so the main loop can handle them efficiently.
    ticker_exclude_from, force_remove_on = detect_untradable_tickers(
        close_adj_df, close_raw_df, volume_df, trading_dates
    )

    # Convert DataFrames to numpy arrays for fast row-level access inside the loop
    sig_arr = signal_df.values
    tv_1d_arr = tv_1d_df.values
    tv_63d_arr = tv_63d_df.values
    close_arr = close_adj_df.values
    tickers = signal_df.columns.values
    date_idx = {trade_date: pos for pos, trade_date in enumerate(signal_df.index)}

    # Pre-align the benchmark matrix to the same index/columns as signal_df
    benchmark_arr: numpy.ndarray | None = None
    benchmark_date_idx: dict[pandas.Timestamp, int] | None = None
    if benchmark_df is not None:
        aligned_bm = benchmark_df.reindex(index=signal_df.index, columns=signal_df.columns).fillna(0)
        benchmark_arr = aligned_bm.values.astype(float)
        benchmark_date_idx = {bm_date: pos for pos, bm_date in enumerate(signal_df.index)}

    in_spy_regime = False
    prev_selected: frozenset | None = None
    prev_weights: pandas.Series | None = None
    portfolios: dict[pandas.Timestamp, pandas.Series] = {}
    spy_entries = 0
    n_delisting_rebals = 0

    for trade_date in trading_dates:
        row_pos = date_idx[trade_date]

        if row_pos == 0:
            # No prior row available on the very first data date — skip
            prev_selected = frozenset()
            continue

        # Read T-1 signals and liquidity data (decisions based on yesterday's close)
        sig_row = sig_arr[row_pos - 1]
        tv_1d_row = tv_1d_arr[row_pos - 1]
        tv_63d_row = tv_63d_arr[row_pos - 1]
        close_row = close_arr[row_pos]   # T close — used only as a tradability guard

        # Collect tickers scheduled for forced removal today (last healthy day before delisting)
        force_removing_today = force_remove_on.get(trade_date, set())

        # Build the full exclusion set: force-removes today + permanently excluded from before
        excluded: set[str] = set(force_removing_today)
        for tkr, exc_date in ticker_exclude_from.items():
            if trade_date >= exc_date:
                excluded.add(tkr)

        # Resolve T-1 benchmark membership (which tickers the benchmark held yesterday)
        benchmark_tickers: set[str] | None = None
        if benchmark_arr is not None and benchmark_date_idx is not None:
            bm_row = benchmark_arr[row_pos - 1]
            benchmark_tickers = set(tickers[bm_row != 0])

        # Apply all selection filters and rank by 63-day traded value
        eligible_tkrs, eligible_tv_63d, n_eligible = _select_eligible_stocks(
            sig_row, tv_1d_row, tv_63d_row, close_row, excluded, tickers,
            benchmark_tickers=benchmark_tickers,
        )
        current_selected = _pick_top_n(eligible_tkrs, eligible_tv_63d)

        # Determine whether to be in SPY regime or stock-picking regime
        should_spy = _determine_regime(n_eligible, in_spy_regime)
        if should_spy:
            current_selected = frozenset()  # no stocks selected in SPY regime

        # Check if anything has changed since the last rebalance
        need_rebalance = _needs_rebalance(
            prev_selected, current_selected, should_spy, in_spy_regime
        )

        # Also force a rebalance if a currently held ticker needs to be sold today
        if force_removing_today and not need_rebalance and prev_weights is not None:
            held_tickers = set(prev_weights.index)
            if force_removing_today & held_tickers:
                need_rebalance = True
                n_delisting_rebals += 1

        # Compute and record the new portfolio weights on rebalance dates
        if need_rebalance:
            if should_spy:
                # SPY regime: 100 % allocation to SPY
                weights = pandas.Series({SPY_TICKER: 1.0})
                if not in_spy_regime:
                    spy_entries += 1
            else:
                # Stock regime: liquidity-weighted, capped at MAX_WEIGHT per position
                weights = _compute_stock_weights(eligible_tkrs, eligible_tv_63d)
                if weights.empty:
                    # No eligible stocks with positive traded value — fall back to SPY
                    weights = pandas.Series({SPY_TICKER: 1.0})
                    should_spy = True
                    if not in_spy_regime:
                        spy_entries += 1

            # Key by signal date (T-1): after T+1 shift, output column = trade_date.
            signal_date = signal_df.index[row_pos - 1]
            portfolios[signal_date] = weights
            prev_weights = weights

        prev_selected = current_selected
        in_spy_regime = should_spy

    print(f"  Rebalance events:          {len(portfolios):,}")
    print(f"  Delisting-forced rebal.:   {n_delisting_rebals:,}")
    print(f"  SPY regime entries:        {spy_entries:,}")

    return portfolios


# -------------------------------------------------------------------
# DATE SHIFTING — signal date → implementation date
# -------------------------------------------------------------------

def shift_to_implementation_dates(
    portfolios: dict[pandas.Timestamp, pandas.Series],
) -> dict[pandas.Timestamp, pandas.Series]:
    # Portfolios are keyed by the signal date (T-1 close).
    # Advance each key by one NYSE trading day to get the implementation date T,
    # i.e. the first day the portfolio can actually be traded.
    # Example: signal at close of Friday 2026-04-17 → implement Monday 2026-04-20.
    result: dict[pandas.Timestamp, pandas.Series] = {}
    for signal_date, weights in portfolios.items():
        impl_date = _next_trading_date(signal_date)
        result[impl_date] = weights
    return result


# -------------------------------------------------------------------
# OUTPUT BUILDING
# -------------------------------------------------------------------

def build_output(
    portfolios: dict[pandas.Timestamp, pandas.Series],
) -> pandas.DataFrame:
    # Reshape the portfolios dict into a tickers × dates matrix.
    # Rows = tickers (alphabetical), columns = rebalance dates (YYYY-MM-DD strings),
    # values = portfolio weights rounded to 9 decimal places.
    # Dates with no rebalance are omitted; SPY row is always present.
    all_tickers = sorted({tkr for weights in portfolios.values() for tkr in weights.index})
    sorted_dates = sorted(portfolios.keys())
    date_cols = [trade_date.strftime("%Y-%m-%d") for trade_date in sorted_dates]

    matrix = pandas.DataFrame(0.0, index=all_tickers, columns=date_cols)

    for trade_date, weights in portfolios.items():
        col = trade_date.strftime("%Y-%m-%d")
        for tkr, weight in weights.items():
            if tkr in matrix.index:
                matrix.loc[tkr, col] = weight

    if SPY_TICKER not in matrix.index:
        spy_row = pandas.DataFrame(0.0, index=[SPY_TICKER], columns=date_cols)
        matrix = pandas.concat([matrix, spy_row])
        matrix.sort_index(inplace=True)

    matrix = matrix.round(9)
    matrix.index.name = COL_TICKER
    return matrix.reset_index()


# -------------------------------------------------------------------
# DIAGNOSTICS
# -------------------------------------------------------------------

def print_summary(
    portfolios: dict[pandas.Timestamp, pandas.Series],
    output_df: pandas.DataFrame,
    loaded: list[str],
    missing: list[str],
) -> None:
    spy_only = [
        weights for weights in portfolios.values()
        if SPY_TICKER in weights.index and abs(weights[SPY_TICKER] - 1.0) < 1e-6
    ]
    stock_only = [
        weights for weights in portfolios.values()
        if not (SPY_TICKER in weights.index and abs(weights[SPY_TICKER] - 1.0) < 1e-6)
    ]

    avg_positions = numpy.mean([len(weights) for weights in stock_only]) if stock_only else 0
    max_weight_observed = max((weights.max() for weights in stock_only), default=0)

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Period:                {PORTFOLIO_START.date()} → {PORTFOLIO_END.date()}")
    print(f"  Tickers loaded:        {len(loaded)}")
    print(f"  Tickers missing:       {len(missing)}")
    print(f"  Rebalance events:      {len(portfolios):,}")
    print(f"  Unique tickers output: {output_df.shape[0]}")
    print()
    print(f"  Parameters:")
    print(f"    Max positions:       {MAX_POSITIONS}")
    print(f"    Max weight:          {MAX_WEIGHT:.0%}")
    print(f"    Min traded value:    ${MIN_DAILY_TRADED_VALUE:,.0f}")
    print(f"    SPY entry:           < {MIN_ELIGIBLE_STOCKS} eligible")
    print(f"    SPY exit:            >= {REENTRY_THRESHOLD} eligible")
    print()
    print(f"  100 % SPY rebalances:  {len(spy_only)}")
    print(f"  Stock-regime rebal.:   {len(stock_only)}")
    print(f"  Avg positions (stock): {avg_positions:.1f}")
    print(f"  Max weight observed:   {max_weight_observed:.6f}  (limit {MAX_WEIGHT})")
    print()

    spy_leak = sum(1 for weights in stock_only if SPY_TICKER in weights.index)
    if spy_leak:
        print(f"  ⚠  SPY appears in {spy_leak} stock-regime portfolios (unexpected)")
    else:
        print(f"  ✓  SPY only present in SPY-regime rebalances")

    bad_sums = [
        (trade_date, weights.sum())
        for trade_date, weights in portfolios.items()
        if abs(weights.sum() - 1.0) > 1e-4
    ]
    if bad_sums:
        print(f"  ⚠  {len(bad_sums)} rebalance(s) with weight sum ≠ 1.0")
    else:
        print(f"  ✓  All rebalance weights sum to 1.0")

    cap_violations = [
        (trade_date, weights.max())
        for trade_date, weights in portfolios.items()
        if weights.max() > MAX_WEIGHT + 1e-6
    ]
    if cap_violations:
        print(f"  ⚠  {len(cap_violations)} rebalance(s) exceed {MAX_WEIGHT:.0%} cap")
    else:
        print(f"  ✓  All weights within {MAX_WEIGHT:.0%} cap")

    print()
    preview_cols = [COL_TICKER] + list(output_df.columns[1:6])
    print("  Preview (first 10 tickers × first 5 dates):\n")
    print(output_df[preview_cols].head(10).to_string(index=False))
    print("\n" + "=" * 70)


# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------

print("=" * 70)
print("  LIQUIDITY-WEIGHTED TREND STRATEGY — Portfolio Construction")
print(f"  Period: {PORTFOLIO_START.date()} → {PORTFOLIO_END.date()}")
print("=" * 70)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n[1] Loading data …")
ticker_frames, loaded, missing = load_data()

print("\n[2] Validating features …")
validate_features(ticker_frames)

print("\n[3] Building matrices …")
signal_df, tv_1d_df, tv_63d_df, close_adj_df, close_raw_df, volume_df = build_matrices(
    ticker_frames
)
# Release per-ticker frames now that the six aligned matrices own the data.
del ticker_frames

print("\n[4] Loading benchmark holdings …")
benchmark_df = load_benchmark_holdings()

print("\n[5] Constructing portfolios …")
portfolios = construct_portfolios(
    signal_df, tv_1d_df, tv_63d_df, close_adj_df, close_raw_df, volume_df,
    benchmark_df=benchmark_df,
)

print("\n[6] Shifting to implementation dates …")
portfolios = shift_to_implementation_dates(portfolios)

print("\n[7] Building output …")
output_df = build_output(portfolios)

out_path = OUTPUT_DIR / "portfolio_weights.csv"
output_df.to_csv(out_path, index=False)
print(f"  Saved: {out_path}")
print(f"  Shape: {output_df.shape[0]} tickers × {output_df.shape[1] - 1} dates")

if missing:
    pandas.DataFrame({"Ticker": missing, "status": "file_not_found"}).to_csv(
        OUTPUT_DIR / "missing_ticker_files.csv", index=False
    )
pandas.DataFrame({"Ticker": loaded, "status": "loaded"}).to_csv(
    OUTPUT_DIR / "loaded_ticker_files.csv", index=False
)

print_summary(portfolios, output_df, loaded, missing)
