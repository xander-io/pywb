from os import environ
from pyww import ENVIRON_DEBUG_KEY
import logging


def _init_logging():
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG
                    if ENVIRON_DEBUG_KEY in environ else logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logger = _init_logging()
