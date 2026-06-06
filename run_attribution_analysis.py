import logging
from pathlib import Path

from kaxanuk.attribution_analysis.config_handlers.excel_configurator import ExcelConfigurator
from kaxanuk.attribution_analysis.performance_attribution import main
from kaxanuk.attribution_analysis.services.configuration_logger import configure_logger
from kaxanuk.attribution_analysis.services.env_loader import load_config_env

# Load configuration variables (e.g. KNAA_API_KEY_KAXANUK) from Config/.env
load_config_env()

configure_logger(
    logger_name="kaxanuk.attribution_analysis",
    logger_level=logging.INFO,
    logger_format="[%(levelname)s] %(message)s",
    logger_file=None,
)

CONFIGURATION_ROUTE = Path('Config')
CONFIGURATION_FILE_NAME = 'attribution_analysis_parameters.xlsx'
configurator = ExcelConfigurator(CONFIGURATION_ROUTE / CONFIGURATION_FILE_NAME)
configuration = configurator.get_configuration()

main(
    configuration,
    launch_dashboard=True,
    dashboard_port=configurator.get_dashboard_port(),
)
