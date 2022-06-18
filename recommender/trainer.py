import mlflow.pytorch
import pytorch_lightning as pl
import torch.nn as nn
import torch.optim as optim
from pytorch_lightning import Trainer

from common import config
from recommender.datasets.dataloader import BertDataModule
from recommender.datasets.utils import (
    print_auto_logged_info,
    recalls_and_ndcgs_for_ks,
)
from recommender.model.model import Bert4RecModel


class Bert4RecTrainer(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.model = Bert4RecModel()

        self.ce = nn.CrossEntropyLoss(ignore_index=0)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        seqs, labels = batch
        logits = self(seqs)  # B x T x V

        logits = logits.view(-1, logits.size(-1))  # (B * T) x V
        labels = labels.view(-1)
        loss = self.ce(logits, labels)
        self.log("train_loss", loss, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        seqs, candidates, labels = batch
        scores = self(seqs)  # B x T x V

        scores = scores[:, -1, :]  # B x V
        scores = scores.gather(1, candidates)

        metrics = recalls_and_ndcgs_for_ks(scores, labels, config.METRIC_KS)
        self.log_dict(metrics, on_epoch=True)

    def test_step(self, batch, batch_idx):
        seqs, candidates, labels = batch
        scores = self(seqs)  # B x T x V

        scores = scores[:, -1, :]  # B x V
        scores = scores.gather(1, candidates)

        metrics = recalls_and_ndcgs_for_ks(scores, labels, config.METRIC_KS)
        self.log_dict(metrics, on_epoch=True)

    def predict_step(self, batch, batch_idx, dataloader_idx=None):
        seqs, candidates, labels = batch
        return self(seqs)

    def configure_optimizers(self):
        return optim.Adam(
            self.model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY
        )


def train_model():
    data_module = BertDataModule()
    model = Bert4RecTrainer()

    trainer = Trainer(
        default_root_dir=config.MODEL_DIR,
        max_epochs=config.NUM_EPOCHS,
        log_every_n_steps=10,
        accelerator="gpu",
        devices=1,
        checkpoint_callback=False,
        logger=False,
    )

    # Initialize MLflow and auto log all MLflow entities
    mlflow.set_experiment("recommender_bert4rec")
    # mlflow.set_tracking_uri("file:./ml_logs")

    mlflow.pytorch.autolog()

    with mlflow.start_run() as run:
        trainer.fit(model, data_module)
        mlflow.pytorch.log_model(model, "model")

    print_auto_logged_info(mlflow.get_run(run_id=run.info.run_id))

    trainer.test(model, data_module)
