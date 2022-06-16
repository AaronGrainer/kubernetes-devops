import pytorch_lightning as pl
import torch.nn as nn
import torch.optim as optim
from pytorch_lightning import Trainer

from common import config
from recommender.datasets.dataloader import BertDataModule
from recommender.datasets.utils import recalls_and_ndcgs_for_ks
from recommender.model.model import Bert4RecModel


class Bert4RecTrainer(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.model = Bert4RecModel()
        self.out = nn.Linear(config.BERT_HIDDEN_UNITS, config.NUM_ITEMS + 1)

        self.ce = nn.CrossEntropyLoss(ignore_index=0)

    def forward(self, x):
        x = self.model(x)
        return self.out(x)

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
        self.log("val_metrics", metrics, on_epoch=True)

    def test_step(self, batch, batch_idx):
        seqs, candidates, labels = batch
        scores = self(seqs)  # B x T x V

        scores = scores[:, -1, :]  # B x V
        scores = scores.gather(1, candidates)

        metrics = recalls_and_ndcgs_for_ks(scores, labels, config.METRIC_KS)
        self.log("test_metrics", metrics, on_epoch=True)

    def predict_step(self, batch, batch_idx, dataloader_idx=None):
        seqs, candidates, labels = batch
        return self(seqs)

    def configure_optimizers(self):
        return optim.Adam(
            self.model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY
        )


def train_model():
    model = Bert4RecTrainer()
    data_module = BertDataModule()

    trainer = Trainer()
    trainer.fit(model, data_module)
