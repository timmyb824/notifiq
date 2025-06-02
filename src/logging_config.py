import logging
import os
from pythonjsonlogger import jsonlogger

def setup_logging():
    log_level = os.environ.get("VERBOSE", "0")
    level = logging.DEBUG if log_level in ("1", "true", "True") else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(level)
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.handlers = [logHandler]
