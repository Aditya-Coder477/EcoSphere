"""
src/utils/logger.py
===================
Structured, colour-aware logger factory for the Carbon Footprint pipeline.
"""

import logging
import os
import sys
from datetime import date
from pathlib import Path

_COLOURS: dict = {
    "DEBUG": "\033[36m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
    "RESET": "\033[0m",
}
_USE_COLOUR: bool = sys.stdout.isatty()


class _ColouredFormatter(logging.Formatter):
    _FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    _DATE_FMT = "%Y-%m-%d %H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        formatted = super().format(record)
        if _USE_COLOUR:
            colour = _COLOURS.get(record.levelname, "")
            reset = _COLOURS["RESET"]
            formatted = f"{colour}{formatted}{reset}"
        return formatted


def get_logger(name: str, logs_dir: Path | None = None) -> logging.Logger:
    """
    Return a named logger with console and file handlers attached.

    Parameters
    ----------
    name : str
        Usually ``__name__`` of the calling module.
    logs_dir : Path | None
        Directory for the log file. Defaults to CFG.LOGS_DIR.

    Returns
    -------
    logging.Logger
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        _ColouredFormatter(
            fmt=_ColouredFormatter._FMT,
            datefmt=_ColouredFormatter._DATE_FMT,
        )
    )
    logger.addHandler(console_handler)

    if logs_dir is None:
        try:
            from config import CFG
            logs_dir = CFG.LOGS_DIR
        except ImportError:
            logs_dir = Path("logs")

    logs_dir = Path(logs_dir)
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_filename = logs_dir / f"pipeline_{date.today().isoformat()}.log"
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            fmt=_ColouredFormatter._FMT,
            datefmt=_ColouredFormatter._DATE_FMT,
        )
    )
    logger.addHandler(file_handler)
    logger.propagate = False
    return logger
