import random

import pytorch_lightning as pl
import torch

from common import config
from recommender.datasets.data import ML1MDataset
from recommender.datasets.negative_sampler import (
    PopularNegativeSampler,
    RandomNegativeSampler,
)


class BertDataModule(pl.LightningDataModule):
    def __init__(self):
        super().__init__()

        movie_lens_dataset = ML1MDataset()
        dataset = movie_lens_dataset.load_dataset()

        smap = dataset["smap"]
        umap = dataset["umap"]

        user_count = len(smap)
        item_count = len(umap)

        item_count = len(smap)
        cloze_mask_token = item_count + 1
        rng = random.Random(config.DATALOADER_RANDOM_SEED)

        if config.TRAIN_NEGATIVE_SAMPLER_CODE == "popular":
            negative_sampler = PopularNegativeSampler
        elif config.TRAIN_NEGATIVE_SAMPLER_CODE == "random":
            negative_sampler = RandomNegativeSampler
        else:
            raise ValueError

        # train_negative_sampler = negative_sampler(
        #     dataset["train"],
        #     dataset["val"],
        #     dataset["test"],
        #     user_count,
        #     item_count,
        #     config.TRAIN_NEGATIVE_SAMPLE_SIZE,
        #     config.TRAIN_NEGATIVE_SAMPLING_SEED,
        # )
        test_negative_sampler = negative_sampler(
            dataset["train"],
            dataset["val"],
            dataset["test"],
            user_count,
            item_count,
            config.TEST_NEGATIVE_SAMPLE_SIZE,
            config.TEST_NEGATIVE_SAMPLING_SEED,
        )

        # train_negative_samples = train_negative_sampler.get_negative_samples()
        test_negative_samples = test_negative_sampler.get_negative_samples()

        self.bert_train_dataset = BertTrainDataset(
            dataset["train"],
            config.BERT_MAX_LEN,
            config.BERT_MASK_PROB,
            cloze_mask_token,
            item_count,
            rng,
        )

        self.bert_eval_dataset = BertEvalDataset(
            dataset["train"],
            dataset["val"],
            config.BERT_MAX_LEN,
            cloze_mask_token,
            test_negative_samples,
        )

    def train_dataloader(self):
        return torch.utils.data.DataLoader(
            self.bert_train_dataset,
            batch_size=config.TRAIN_BATCH_SIZE,
        )

    def val_dataloader(self):
        return torch.utils.data.DataLoader(
            self.bert_eval_dataset,
            batch_size=config.VAL_BATCH_SIZE,
        )

    def test_dataloader(self):
        return torch.utils.data.DataLoader(
            self.bert_eval_dataset,
            batch_size=config.TEST_BATCH_SIZE,
        )

    def predict_dataloader(self):
        return torch.utils.data.DataLoader(
            self.bert_eval_dataset,
            batch_size=config.TEST_BATCH_SIZE,
        )


class BertTrainDataset(torch.utils.data.Dataset):
    def __init__(self, u2seq, max_len, mask_prob, mask_token, num_items, rng):
        self.u2seq = u2seq
        self.users = sorted(self.u2seq.keys())
        self.max_len = max_len
        self.mask_prob = mask_prob
        self.mask_token = mask_token
        self.num_items = num_items
        self.rng = rng

    def __len__(self):
        return len(self.users)

    def __getitem__(self, index):
        user = self.users[index]
        seq = self._get_seq(user)

        tokens = []
        labels = []
        for s in seq:
            prob = self.rng.random()
            if prob < self.mask_prob:
                prob /= self.mask_prob

                if prob < 0.8:
                    tokens.append(self.mask_token)
                elif prob < 0.9:
                    tokens.append(self.rng.randint(1, self.num_items))
                else:
                    tokens.append(s)
            else:
                tokens.append(s)
                labels.append(0)

        tokens = tokens[-self.max_len :]
        labels = labels[-self.max_len :]

        mask_len = self.max_len - len(tokens)

        tokens = [0] * mask_len + tokens
        labels = [0] * mask_len + labels

        return torch.LongTensor(tokens), torch.LongTensor(labels)

    def _get_seq(self, user):
        return self.u2seq[user]


class BertEvalDataset(torch.utils.data.Dataset):
    def __init__(self, u2seq, u2answer, max_len, mask_token, negative_samples):
        self.u2seq = u2seq
        self.users = sorted(self.u2seq.keys())
        self.u2answer = u2answer
        self.max_len = max_len
        self.mask_token = mask_token
        self.negative_samples = negative_samples

    def __len__(self):
        return len(self.users)

    def __getitem__(self, index):
        user = self.users[index]
        seq = self.u2seq[user]
        answer = self.u2answer[user]
        negs = self.negative_samples[user]

        candidates = answer + negs
        labels = [1] * len(answer) + [0] * len[negs]

        seq = seq + [self.mask_token]
        seq = seq[-self.max_len :]
        padding_len = self.max_len - len(seq)
        seq = [0] * padding_len + seq

        return torch.LongTensor(seq), torch.LongTensor(candidates), torch.LongTensor(labels)
