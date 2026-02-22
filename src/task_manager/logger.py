# logger.py
import logging
import sys

def get_logger(
    name: str|None = None,
    level: int = logging.INFO,
    fmt: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
) -> logging.Logger:
    """
    Configure and return a logger.

    Args:
        name: Optional logger name. If None, root logger is used.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        fmt: Log message format string.
        datefmt: Date format string.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

