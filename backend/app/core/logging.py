"""
logging.py
==========
Structured logger configuration.
"""

import logging
import sys

def setup_logging():
    logger = logging.getLogger("backend")
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = setup_logging()
