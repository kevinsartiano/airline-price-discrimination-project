"""Logger tool."""
import logging
import sys
from logging import Logger


def get_logger(filename: str) -> Logger:
    """Get logger with stream and file handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename=filename)

    stream_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)

    stream_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s')
    file_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s')

    stream_handler.setFormatter(stream_formatter)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
