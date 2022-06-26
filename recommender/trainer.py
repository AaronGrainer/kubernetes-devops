import pandas as pd
import pytorch_lightning as pl
from torch.utils.data import DataLoader

import mlflow
from common import config
from recommender.data import Dataset
from recommender.models import Recommender
from recommender.utils import cleanup, map_column


def train():
    data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
    data = data.head(100000)
    data.sort_values(by="timestamp", inplace=True)

    data, mapping, inverse_mapping = map_column(data, col_name="movieId")

    group_by_train = data.groupby(by="userId")

    groups = list(group_by_train.groups)

    train_data = Dataset(groups=groups, group_by=group_by_train, split="train")
    val_data = Dataset(groups=groups, group_by=group_by_train, split="val")

    train_loader = DataLoader(train_data, batch_size=config.TRAIN_BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=config.VAL_BATCH_SIZE, shuffle=False)

    model = Recommender(vocab_size=len(mapping) + 2)

    trainer = pl.Trainer(
        default_root_dir=config.MODEL_DIR,
        max_epochs=config.NUM_EPOCHS,
        log_every_n_steps=10,
        accelerator="gpu",
        devices=1,
        logger=False,
    )

    # Initialize MLflow and auto log all MLflow entities
    mlflow.set_experiment("recommender_bert4rec")
    # mlflow.set_tracking_uri("file:./ml_logs")
    mlflow.pytorch.autolog()

    # Start training
    with mlflow.start_run() as run:
        trainer.fit(model, train_loader, val_loader)
        trainer.test(dataloaders=val_loader)
        mlflow.pytorch.log_model(model, "model")

    mlflow_run_id = run.info.run_id

    # Cleanup
    cleanup()
