import pytorch_lightning as pl
import torch
import torch.nn as nn
from model.model import Bert4RecModel
from torch.utils.data import DataLoader

from common import config


class Bert4RecTrainer(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.model = Bert4RecModel()
        self.out = nn.Linear(config.BERT_HIDDEN_UNITS, config.NUM_ITEMS + 1)
