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

# Data
MOVIE_DATASET_DIR = Path(DATA_DIR, "movie")

# Create Dirs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Recommender
RANDOM_SEED = 42
BERT_HIDDEN_UNITS = 256
BERT_MAX_LEN = 100
BERT_DROPOUT = 0.1
BERT_NUM_HEADS = 4
BERT_NUM_BLOCKS = 2
NUM_ITEMS = 0
LEARNING_RATE = 0.001
WEIGHT_DECAY = 0
MIN_RATING = 0
MIN_SC = 0
MIN_UC = 5
BERT_MASK_PROB = 0.15
DATALOADER_RANDOM_SEED = 0.0
TRAIN_NEGATIVE_SAMPLER_CODE = "random"  # random / popular
TRAIN_NEGATIVE_SAMPLE_SIZE = 0
TRAIN_NEGATIVE_SAMPLING_SEED = 0
TEST_NEGATIVE_SAMPLER_CODE = "random"  # random / popular
TEST_NEGATIVE_SAMPLE_SIZE = 100
TEST_NEGATIVE_SAMPLING_SEED = 98765
METRIC_KS = [1, 5, 10, 20, 50, 100]
TRAIN_BATCH_SIZE = 128
VAL_BATCH_SIZE = 128
TEST_BATCH_SIZE = 128
NUM_EPOCHS = 50

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
