# utils/logger.py

import logging
import sys

def setup_logger(name=__name__, level=logging.INFO):
    """
    Sets up a logger with a custom format.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding multiple handlers if already present
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
