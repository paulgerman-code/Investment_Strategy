"""
Entry script that reads Data Curator configuration from an Excel file, registers custom
calculation modules, and outputs enriched datasets to csv and parquet files.

This variant parallelizes the per-identifier downloads across a thread pool.
The configuration is read once on the main thread to get the full identifier list,
then that list is split into chunks and each chunk is processed by a worker thread
with its own independent provider instances (providers keep per-instance state after
.initialize(), so sharing one instance across threads is not safe).

The number of worker threads defaults to min(len(identifiers), cpu_count × 2) but
can be overridden by setting the KNDC_MAX_THREADS environment variable.

Environment Variables
---------------------
KNDC_API_KEY_FMP
    API key for the Financial Modeling Prep data provider.
KNDC_API_KEY_LSEG
    API key for the LSEG Workspace data provider.
KNDC_MAX_THREADS
    Optional. Max worker threads for parallel downloads.
    Defaults to min(len(identifiers), cpu_count × 2).
"""

import dataclasses
import os
import pathlib
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import kaxanuk.data_curator
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# Load the user's environment variables from Config/.env, including data provider API keys
kaxanuk.data_curator.load_config_env()

# Load user's custom calculations modules if they exist in the src directory
if (pathlib.Path('src/data_curator/alpha_signals/simple_moving_average_alpha_signal.py').is_file()
    and pathlib.Path('src/data_curator/market/missing_market_data.py').is_file()
    and pathlib.Path('src/data_curator/outlier_adjusted_data/shares_outstanding_outlier_adjusted.py').is_file()
):
    # noinspection PyUnresolvedReferences
    from src.data_curator.alpha_signals import simple_moving_average_alpha_signal
    from src.data_curator.market import missing_market_data
    from src.data_curator.outlier_adjusted_data import shares_outstanding_outlier_adjusted

    custom_calculation_modules = [
        simple_moving_average_alpha_signal,
        missing_market_data,
        shares_outstanding_outlier_adjusted,
    ]
else:
    custom_calculation_modules = []

output_base_dir = 'Data_Curator'
failed_tickers_log_path = pathlib.Path(output_base_dir) / '_failed_tickers.log'
_failure_lock = threading.Lock()


def _log_failure(identifier, error):
    msg = f"{identifier}\t{type(error).__name__}: {error}"
    print(f"[FAILED] {msg}")
    with _failure_lock:
        with open(failed_tickers_log_path, 'a', encoding='utf-8') as f:
            f.write(msg + "\n")


def _build_configurator():
    # Build a fresh ExcelConfigurator with its own provider instances.
    # Each worker thread calls this so it gets independent provider state —
    # providers are not safe to share across threads after .initialize().
    return kaxanuk.data_curator.config_handlers.ExcelConfigurator(
        file_path='Config/data_curator_parameters.xlsx',
        data_providers={
            'financial_modeling_prep': {
                'class': kaxanuk.data_curator.data_providers.FinancialModelingPrep,
                'api_key': os.getenv('KNDC_API_KEY_FMP'),   # set this up in Config/.env
            },
            'lseg_workspace': {
                'class': kaxanuk.data_curator.data_providers.LsegWorkspace,
                'api_key': os.getenv('KNDC_API_KEY_LSEG'),  # set this up in Config/.env
            },
            'yahoo_finance': {
                'class': kaxanuk.data_curator.load_data_provider_extension(
                    extension_name='yahoo_finance',
                    extension_class_name='YahooFinance',
                ),
                'api_key': None     # this provider doesn't use an API key
            },
        },
        output_handlers={
            'csv': kaxanuk.data_curator.output_handlers.CsvOutput(
                output_base_dir=output_base_dir,
            ),
            'parquet': kaxanuk.data_curator.output_handlers.ParquetOutput(
                output_base_dir=output_base_dir,
            ),
        },
    )


def _chunk(seq, n_chunks):
    # Split `seq` into `n_chunks` roughly-equal contiguous tuples.
    n = len(seq)
    n_chunks = max(1, min(n_chunks, n))
    size, rem = divmod(n, n_chunks)
    out = []
    i = 0
    for c in range(n_chunks):
        step = size + (1 if c < rem else 0)
        out.append(tuple(seq[i:i + step]))
        i += step
    return out


def _run_chunk(identifiers_subset):
    # Worker function: process each identifier individually so a single failing
    # ticker doesn't kill the rest of the chunk. Failures are recorded to
    # `Data_Curator/_failed_tickers.log` with the ticker name and error.
    for identifier in identifiers_subset:
        try:
            local_configurator = _build_configurator()
            base_config = local_configurator.get_configuration()
            sub_config = dataclasses.replace(base_config, identifiers=(identifier,))

            kaxanuk.data_curator.main(
                configuration=sub_config,
                market_data_provider=local_configurator.get_market_data_provider(),
                fundamental_data_provider=local_configurator.get_fundamental_data_provider(),
                output_handlers=[local_configurator.get_output_handler()],
                custom_calculation_modules=custom_calculation_modules,
                logger_level=local_configurator.get_logger_level(),
            )
        except Exception as exc:
            _log_failure(identifier, exc)
            traceback.print_exc()


if __name__ == '__main__':
    # Reset the failures log so it only reflects this run.
    failed_tickers_log_path.parent.mkdir(parents=True, exist_ok=True)
    failed_tickers_log_path.write_text('', encoding='utf-8')

    # Read the full identifier list from the config on the main thread
    main_configurator = _build_configurator()
    all_identifiers = main_configurator.get_configuration().identifiers

    # Determine how many worker threads to use
    max_threads_env = os.environ.get('KNDC_MAX_THREADS')
    if max_threads_env is not None:
        max_threads = int(max_threads_env)
    else:
        max_threads = min(len(all_identifiers), (os.cpu_count() or 1) * 2)

    if max_threads <= 1 or len(all_identifiers) <= 1:
        # Single-threaded path — no overhead, useful for small universes or debugging
        _run_chunk(tuple(all_identifiers))
    else:
        # Split identifiers across threads and run all chunks in parallel.
        # Any exception raised in a worker is re-raised on the main thread.
        chunks = _chunk(all_identifiers, max_threads)
        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            futures = [executor.submit(_run_chunk, chunk) for chunk in chunks]
            for future in as_completed(futures):
                future.result()

    failed_lines = failed_tickers_log_path.read_text(encoding='utf-8').splitlines()
    if failed_lines:
        print(f"\n{len(failed_lines)} ticker(s) failed — see {failed_tickers_log_path}:")
        for line in failed_lines:
            print(f"  {line}")
    else:
        print("\nAll tickers processed successfully.")
