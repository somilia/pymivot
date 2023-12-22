"""
This package contains utility functions and classes used by the pymivot.validator.
"""
from pymivot.validator.mivot_validator.utils.logger_setup import LoggerSetup

logger = LoggerSetup.get_logger()
LoggerSetup.set_debug_level()

logger.info("utils package initialized")
