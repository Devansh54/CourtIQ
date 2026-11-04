"""CourtIQ Structured Logging Configuration.

Configures consistent logging formatting and levels across modules.
"""

import logging
import sys
from typing import Optional


_CONFIGURED = False


def setup_logging(log_level: Optional[str] = "INFO") -> None:
    """Initialize structured application-wide logging.

    Args:
        log_level: String log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, (log_level or "INFO").upper(), logging.INFO)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger("courtiq")
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
    root_logger.propagate = False

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Retrieve a namespaced logger under the 'courtiq' hierarchy.

    Args:
        name: Name of the module or subcomponent.

    Returns:
        logging.Logger instance.
    """
    if not _CONFIGURED:
        setup_logging()
    if name.startswith("courtiq."):
        return logging.getLogger(name)
    return logging.getLogger(f"courtiq.{name}")
