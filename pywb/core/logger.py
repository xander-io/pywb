import logging
from os import environ, makedirs, path

from pywb import ENVIRON_DEBUG_KEY, ENVIRON_LOG_DIR_KEY

# Log dir changes if environment var is set
LOG_DIR = "logs" if ENVIRON_LOG_DIR_KEY not in environ else environ[ENVIRON_LOG_DIR_KEY]
DEFAULT_LOG_PATH = path.join(LOG_DIR, "pywb.out")


def _init_logging(output_path=DEFAULT_LOG_PATH) -> None:
    makedirs(path.dirname(output_path), exist_ok=True)
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s")

    f_logger = logging.getLogger(__name__)
    for hdlr in f_logger.handlers[:]:  # remove all old handlers
        f_logger.removeHandler(hdlr)

    if f_logger.getEffectiveLevel() != logging.DEBUG:
        f_logger.setLevel(logging.DEBUG
                          if ENVIRON_DEBUG_KEY in environ else logging.INFO)

    f_handler = logging.FileHandler(output_path, "w")
    f_handler.setFormatter(formatter)
    f_logger.addHandler(f_handler)
    f_logger.propagate = False


def set_logger_output_path(output_path):
    _init_logging(output_path=output_path)


logger = logging.getLogger(__name__)
