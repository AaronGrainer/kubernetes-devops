import pytorch_lightning as pl
import torch.nn as nn

from common import config
from recommender.model.model import Bert4RecModel


class Bert4RecTrainer(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.model = Bert4RecModel()
        self.out = nn.Linear(config.BERT_HIDDEN_UNITS, config.NUM_ITEMS + 1)

    def forward(self, x):
        x = self.model(x)
        return self.out(x)
