"""Application logging setup."""

import logging
from pathlib import Path


def setup_logger(log_path):
    """Create a file logger for converter actions and errors."""
    logger = logging.getLogger("currency_converter")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    path = Path(log_path)
    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )

    logger.addHandler(file_handler)
    return logger
