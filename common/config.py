import logging
import logging.config
import sys
from pathlib import Path

# import pretty_errors  # NOQA: F401
from rich.logging import RichHandler

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
LOGS_DIR = Path(BASE_DIR, "logs")
MODEL_DIR = Path(BASE_DIR, "model")
DATA_DIR = Path(BASE_DIR, "data")
MOVIELENS_RATING_DATA_DIR = Path(BASE_DIR, "data", "ml-20m", "ratings.csv")
MOVIELENS_MOVIE_DATA_DIR = Path(BASE_DIR, "data", "ml-20m", "movies.csv")

# Data
MOVIE_DATASET_DIR = Path(DATA_DIR, "movie")

# Create Dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Recommender
TRAIN_BATCH_SIZE = 64
VAL_BATCH_SIZE = 64

MASK = 1
PAD = 0
CAP = 0
MASK_PROBABILITY = 0.5
VAL_CONTEXT_SIZE = 5
HISTORY_SIZE = 120
DEFAULT_CONTEXT_SIZE = 120
CHANNELS = 128
DROPOUT = 0.4
LEARNING_RATE = 1e-4
NUM_EPOCHS = 1
MODEL_URI = "runs:/{}/model"

# mlflow.set_experiment("recommender_bert4rec")
# mlflow.set_tracking_uri("file:./ml_logs")

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
