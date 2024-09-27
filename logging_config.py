import logging
import os
from logging.handlers import BaseRotatingHandler
from datetime import datetime
from config import LOG_LEVEL


class CustomRotatingFileHandler(BaseRotatingHandler):
    """
    A custom rotating file handler that generates log files like 'app_date_1.log',
    'app_date_2.log', etc., with rotation based on file size.
    """

    def __init__(self, base_filename, maxBytes=10000, backupCount=10, encoding=None):
        self.base_filename = base_filename
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.current_index = 0
        self.encoding = encoding

        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_filename = (
            f"{self.base_filename}_{current_date}_{self.current_index}.log"
        )
        super().__init__(self.log_filename, "a", encoding)

    def shouldRollover(self, record):
        """
        Check if rollover should occur by comparing the file size to the maxBytes.
        """
        if self.maxBytes > 0:
            self.stream.seek(0, os.SEEK_END)
            if self.stream.tell() >= self.maxBytes:
                return True
        return False

    def doRollover(self):
        """
        Perform the rollover by creating a new file with an incremented index.
        """
        if self.stream:
            self.stream.close()

        self.current_index += 1
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.log_filename = (
            f"{self.base_filename}_{current_date}_{self.current_index}.log"
        )

        self.stream = self._open()

        if self.backupCount > 0:
            log_dir, log_basename = os.path.split(self.base_filename)
            log_files = sorted(
                [
                    f
                    for f in os.listdir(log_dir)
                    if f.startswith(log_basename) and f.endswith(".log")
                ],
                key=lambda f: os.path.getmtime(os.path.join(log_dir, f)),
            )
            excess_files = len(log_files) - self.backupCount
            for i in range(excess_files):
                os.remove(os.path.join(log_dir, log_files[i]))


def setup_logging(name="app"):
    """
    Configures a logger with a custom rotating file handler.
    The log file will include the current date and an index for rotated files.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    base_log_filename = os.path.join(log_dir, name)

    try:
        handler = CustomRotatingFileHandler(
            base_filename=base_log_filename,
            maxBytes=10000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
            logger.propagate = False

    except Exception as e:
        print(f"Error during logging setup: {e}")
        raise e


def get_logger(name="app"):
    """
    Returns a logger with the specified name.
    """
    setup_logging(name)
    return logging.getLogger(name)
