import logging
import sys
from pathlib import Path
from loguru import logger

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def _log_filter(record):
    # Allow all log levels from the application
    if "the_captains_log" in str(record["file"].path):
        return True
    
    # Allow uvicorn access logs (INFO level and above)
    if "uvicorn" in record["name"] and record["level"].no >= 20:  # INFO=20, WARNING=30, ERROR=40
        return True
    
    # Allow logs from logging module if they are INFO or above (for uvicorn access logs)
    if record["name"] == "logging" and record["level"].no >= 20:
        return True

    return False

def setup_logging():
    logger.remove()

    # Create logs directory if it doesn't exist
    log_dir = Path("/home/lisq/the_captains_log/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "app.log"
    logger.add(
        log_file, 
        rotation="1 day", 
        retention="7 days", 
        level="DEBUG",  
        filter=_log_filter,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # Configure standard logging to use InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Configure uvicorn loggers to use InterceptHandler
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False
    
    return logger

logger = setup_logging()

if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")