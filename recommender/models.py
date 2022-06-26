import pytorch_lightning as pl
import torch

from common import config
from recommender.utils import masked_accuracy, masked_ce


class Recommender(pl.LightningModule):
    def __init__(self, vocab_size):
        super().__init__()

        self.cap = config.CAP
        self.mask = config.MASK

        self.learning_rate = config.LEARNING_RATE
        self.dropout = config.DROPOUT
        self.vocab_size = vocab_size

        self.item_embeddings = torch.nn.Embedding(self.vocab_size, embedding_dim=config.CHANNELS)
        self.input_pos_embedding = torch.nn.Embedding(512, embedding_dim=config.CHANNELS)

        encoder_layer = torch.nn.TransformerEncoderLayer(
            d_model=config.CHANNELS, nhead=4, dropout=self.dropout
        )
        self.encoder = torch.nn.TransformerEncoder(encoder_layer, num_layers=6)

        self.linear_out = torch.nn.Linear(config.CHANNELS, self.vocab_size)
        self.do = torch.nn.Dropout(p=self.dropout)

    def encode_source(self, source_items):
        source_items = self.item_embeddings(source_items)

        batch_size, in_sequence_len = source_items.size(0), source_items.size(1)
        pos_encoder = (
            torch.arange(0, in_sequence_len, device=source_items.device)
            .unsqueeze(0)
            .repeat(batch_size, 1)
        )
        pos_encoder = self.input_pos_embedding(pos_encoder)

        source_items += pos_encoder

        source = source_items.permute(1, 0, 2)
        source = self.encoder(source)

        return source.permute(1, 0, 2)

    def forward(self, source_items):
        source = self.encode_source(source_items)
        out = self.linear_out(source)
        return out

    def training_step(self, batch, batch_idx):
        source_items, y_true = batch

        y_pred = self(source_items)

        y_pred = y_pred.view(-1, y_pred.size(2))
        y_true = y_true.view(-1)

        source_items = source_items.view(-1)
        mask = source_items == self.mask

        loss = masked_ce(y_pred=y_pred, y_true=y_true, mask=mask)
        accuracy = masked_accuracy(y_pred=y_pred, y_true=y_true, mask=mask)

        self.log("train_loss", loss)
        self.log("train_accuracy", accuracy)

        return loss

    def validation_step(self, batch, batch_idx):
        source_items, y_true = batch

        y_pred = self(source_items)

        y_pred = y_pred.view(-1, y_pred.size(2))
        y_true = y_true.view(-1)

        source_items = source_items.view(-1)
        mask = source_items == self.mask

        loss = masked_ce(y_pred=y_pred, y_true=y_true, mask=mask)
        accuracy = masked_accuracy(y_pred=y_pred, y_true=y_true, mask=mask)

        self.log("val_loss", loss)
        self.log("val_accuracy", accuracy)

        return loss

    def test_step(self, batch, batch_idx):
        source_items, y_true = batch

        y_pred = self(source_items)

        y_pred = y_pred.view(-1, y_pred.size(2))
        y_true = y_true.view(-1)

        source_items = source_items.view(-1)
        mask = source_items == self.mask

        loss = masked_ce(y_pred=y_pred, y_true=y_true, mask=mask)
        accuracy = masked_accuracy(y_pred=y_pred, y_true=y_true, mask=mask)

        self.log("test_loss", loss)
        self.log("test_accuracy", accuracy)

        return loss

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.1)
        return {"optimizer": optimizer, "lr_scheduler": scheduler, "monitor": "val_loss"}
