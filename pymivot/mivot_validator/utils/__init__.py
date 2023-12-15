"""
This package contains utility functions and classes used by the validator.
"""
from pymivot.mivot_validator.utils.logger_setup import LoggerSetup

logger = LoggerSetup.get_logger()
LoggerSetup.set_debug_level()

logger.info("utils package initialized")
