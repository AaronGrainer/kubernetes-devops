import torch.nn as nn

from common import config
from recommender.model.embedding import BERTEmbedding
from recommender.model.transformer import TransformerBlock
from recommender.utils import set_seed


class Bert4RecModel(nn.Module):
    def __init__(self):
        super().__init__()

        set_seed(config.RANDOM_SEED)

        # Embedding for BERT, sum of positional, segment & token embeddings
        vocab_size = config.NUM_ITEMS + 2
        self.embedding = BERTEmbedding(
            vocab_size=vocab_size,
            embed_size=config.BERT_HIDDEN_UNITS,
            max_len=config.BERT_MAX_LEN,
            dropout=config.BERT_DROPOUT,
        )

        # Multi-layer transformer blocks
        self.transformer_blocks = nn.ModuleList(
            [
                TransformerBlock(
                    config.BERT_HIDDEN_UNITS,
                    config.BERT_NUM_HEADS,
                    config.BERT_HIDDEN_UNITS * 4,
                    config.BERT_DROPOUT,
                )
                for _ in range(config.BERT_NUM_BLOCKS)
            ]
        )

    def forward(self, x):
        mask = (x > 0).unsqueeze(1).repeat(1, x.size(1), 1).unsqueeze(1)

        x = self.embedding(x)

        for transformer in self.transformer_blocks:
            x = transformer.forward(x, mask)

        return x
