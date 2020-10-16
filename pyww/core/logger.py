from os import environ
import logging


def _init_logging():
    formatter = logging.Formatter(
        "[%(asctime)s - %(levelname)s] %(message)s")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if "PYWW_DEBUG" in environ else logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


logger = _init_logging()
