import logging
import logging.config
import sys
from pathlib import Path

import pretty_errors  # NOQA: F401
from rich.logging import RichHandler

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
LOGS_DIR = Path(BASE_DIR, "logs")
MODEL_DIR = Path(BASE_DIR, "model")

# Data
MOVIE_DATASET_DIR = Path(BASE_DIR, "data", "movie")

# Create Dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Recommender
RANDOM_SEED = 42
BERT_HIDDEN_UNITS = 256
BERT_MAX_LEN = 100
BERT_DROPOUT = 0.1
BERT_NUM_HEADS = 4
BERT_NUM_BLOCKS = 2
NUM_ITEMS = None

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
logger.handlers[0] = RichHandler(markup=True)
