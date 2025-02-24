from palworld_pal_editor.config import PROGRAM_PATH
from palworld_pal_editor.utils.logger import Logger

LOGGER = Logger(name="Palworld-Pal-Editor", log_directory=PROGRAM_PATH / "logs")
LOGGER.info(f"Logs written to {PROGRAM_PATH / 'logs'}")

from palworld_pal_editor.utils.util import alphanumeric_key, clamp
from palworld_pal_editor.utils.data_provider import DataProvider