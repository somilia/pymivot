import sys, os
from mivot_validator.logger_setup import LoggerSetup

logger = LoggerSetup.get_logger()
LoggerSetup.set_info_level()

logger.info("mivot_validator package intialized")
