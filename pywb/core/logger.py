import logging
from os import environ

from pywb import ENVIRON_DEBUG_KEY


def _init_logging():
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s")

    console_logger = logging.getLogger(__name__)
    console_logger.setLevel(logging.DEBUG
                            if ENVIRON_DEBUG_KEY in environ else logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    console_logger.addHandler(stream_handler)
    return console_logger


logger = _init_logging()
