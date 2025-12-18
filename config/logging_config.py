import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def _rotating_handler(filename, level=logging.INFO):
    handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return handler


def setup_logging():
    # Root logger (app-wide)
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if root.handlers:
        return

    root.addHandler(_rotating_handler("app.log"))

    # Telegram logger
    telegram_logger = logging.getLogger("TELEGRAM_HANDLER")
    telegram_logger.addHandler(_rotating_handler("telegram_handler.log"))
    telegram_logger.propagate = False

    # Parser logger
    parser_logger = logging.getLogger("PARSER")
    parser_logger.addHandler(_rotating_handler("parser.log"))
    parser_logger.propagate = False

    # Executor logger
    executor_logger = logging.getLogger("EXECUTOR")
    executor_logger.addHandler(_rotating_handler("executor.log"))
    executor_logger.propagate = False
