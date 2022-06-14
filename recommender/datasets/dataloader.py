from abc import ABCMeta, abstractmethod

import pytorch_lightning as pl
import torch

from common import config
from recommender.datasets.data import ML1MDataset
from recommender.datasets.negative_sampler import (
    PopularNegativeSampler,
    RandomNegativeSampler,
)


class DataloaderBase(metaclass=ABCMeta):
    def __init__(self, dataset):
        dataset = dataset.load_dataset()

        self.train = dataset["train"]
        self.val = dataset["val"]
        self.test = dataset["test"]
        self.umap = dataset["umap"]
        self.smap = dataset["smap"]

        self.user_count = len(self.umap)
        self.item_count = len(self.smap)

    @abstractmethod
    def get_pytorch_dataloaders(self):
        pass


class BertDataloader(DataloaderBase):
    def __init__(self, dataset):
        super().__init__(dataset)

        config.NUM_ITEMS = len(self.smap)
        self.CLOZE_MASK_TOKEN = self.item_count + 1

        if config.TRAIN_NEGATIVE_SAMPLER_CODE == "popular":
            negative_sampler = PopularNegativeSampler
        elif config.TRAIN_NEGATIVE_SAMPLER_CODE == "random":
            negative_sampler = RandomNegativeSampler
        else:
            raise ValueError

        train_negative_sampler = negative_sampler(
            self.train,
            self.val,
            self.test,
            self.user_count,
            self.item_count,
            config.TRAIN_NEGATIVE_SAMPLE_SIZE,
            config.TRAIN_NEGATIVE_SAMPLING_SEED,
        )
        test_negative_sampler = negative_sampler(
            self.train,
            self.val,
            self.test,
            self.user_count,
            self.item_count,
            config.TEST_NEGATIVE_SAMPLE_SIZE,
            config.TEST_NEGATIVE_SAMPLING_SEED,
        )

        self.train_negative_samples = train_negative_sampler.get_negative_samples()
        self.test_negative_samples = test_negative_sampler.get_negative_samples()

    def get_pytorch_dataloaders(self):
        pass


class BertDataModule(pl.LightningDataModule):
    def __init__(self):
        super().__init__()

        dataset = ML1MDataset()


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
