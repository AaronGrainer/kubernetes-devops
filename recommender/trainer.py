import pandas as pd
import pytorch_lightning as pl
import typer
from torch.utils.data import DataLoader

import mlflow
from common import config
from common.config import logger
from recommender.data import Dataset
from recommender.models import Recommender
from recommender.utils import cleanup, map_column

app = typer.Typer()


@app.command()
def train():
    logger.info("Starting Recommender Trainer")

    logger.info("Loading Dataset")
    data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
    data = data.head(100000)
    data.sort_values(by="timestamp", inplace=True)

    data, mapping, _ = map_column(data, col_name="movieId")

    group_by_train = data.groupby(by="userId")

    groups = list(group_by_train.groups)

    train_data = Dataset(groups=groups, group_by=group_by_train, split="train")
    val_data = Dataset(groups=groups, group_by=group_by_train, split="val")

    train_loader = DataLoader(train_data, batch_size=config.TRAIN_BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=config.VAL_BATCH_SIZE, shuffle=False)
    logger.info("Dataset loaded")

    logger.info("Initializing trainer")
    model = Recommender(vocab_size=len(mapping) + 2)

    trainer = pl.Trainer(
        default_root_dir=config.MODEL_DIR,
        max_epochs=config.NUM_EPOCHS,
        log_every_n_steps=10,
        # accelerator="gpu",
        # devices=1,
        logger=False,
    )

    # Initialize MLflow and auto log all MLflow entities
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment("/recommender_bert4rec")
    mlflow.pytorch.autolog()

    # Start training
    with mlflow.start_run() as run:
        trainer.fit(model, train_loader, val_loader)
        trainer.test(dataloaders=val_loader)
        mlflow.pytorch.log_model(model, "model")

    mlflow_run_id = run.info.run_id
    logger.info(f"Successfully trained a new recommender model with run_id: {mlflow_run_id}")

    # Cleanup
    logger.info("Cleaning up after training")
    cleanup()


@app.command()
def main():
    return "Recommender Trainer"


if __name__ == "__main__":
    app()
