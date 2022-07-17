import logging
import logging.config
import os
import sys
from pathlib import Path

import pretty_errors  # NOQA: F401
from rich.logging import RichHandler  # NOQA: F401

# Settings
TITLE = "Recommender"
DESCRIPTION = "Recommender app."
VERSION = "1.0"
BACKEND_CORS_ORIGINS = []

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")
LOGS_DIR = Path(BASE_DIR, "logs")
DATA_DIR = Path(BASE_DIR, "data")

# Create dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database
MONGODB_ROOT_USERNAME = os.getenv("MONGODB_ROOT_USERNAME")
MONGODB_ROOT_PASSWORD = os.getenv("MONGODB_ROOT_PASSWORD")
MONGODB_ROOT_HOST = os.getenv("MONGODB_ROOT_HOST")
MONGO_CLIENT = (
    f"mongodb://{MONGODB_ROOT_USERNAME}:{MONGODB_ROOT_PASSWORD}@{MONGODB_ROOT_HOST}:27017"
)

# Logger
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "minimal": {"format": "%(message)s"},
        "detailed": {
            "format": "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d]\n%(message)s\n"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "minimal",
            "level": logging.DEBUG,
        },
        "info": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "info.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.INFO,
        },
        "error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Path(LOGS_DIR, "error.log"),
            "maxBytes": 10485760,  # 1 MB
            "backupCount": 10,
            "formatter": "detailed",
            "level": logging.ERROR,
        },
    },
    "loggers": {
        "root": {
            "handlers": ["console", "info", "error"],
            "level": logging.INFO,
            "propagate": True,
        }
    },
}
logging.config.dictConfig(logging_config)
logger = logging.getLogger("root")
# logger.handlers[0] = RichHandler(markup=True)
