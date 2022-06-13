import pickle
from abc import ABCMeta, abstractmethod
from collections import Counter
from pathlib import Path

import numpy as np
from tqdm import trange

from common import config
from common.config import logger


class NegativeSamplerBase(metaclass=ABCMeta):
    def __init__(self, train, val, test, user_count, item_count, sample_size, seed):
        self.train = train
        self.val = val
        self.test = test
        self.user_count = user_count
        self.item_count = item_count
        self.sample_size = sample_size
        self.seed = seed
        self.save_filepath = Path(
            config.DATA_DIR,
            "preprocessed",
            "ml-1m",
            f"{config.TRAIN_NEGATIVE_SAMPLER_CODE}-sample_size.pkl",
        )

    @abstractmethod
    def generate_negative_samples(self):
        pass

    @classmethod
    def dataset_name(cls):
        return "Movielens 1M"

    def get_negative_samples(self):
        if self.save_filepath.is_file():
            logger.info(f"{self.dataset_name()} Negative samples exist. Loading...")
            negative_samples = pickle.load(self.save_filepath.open("rb"))
            return negative_samples

        logger.info(f"{self.dataset_name()} Negative samples doesn't exist. Generating...")
        negative_samples = self.generate_negative_samples()
        with self.save_filepath.open("wb") as f:
            pickle.dump(negative_samples, f)

        return negative_samples


class RandomNegativeSampler(NegativeSamplerBase):
    def generate_negative_samples(self):
        assert self.seed is not None, "Specify seed for random sampling"

        np.random.seed(self.seed)
        negative_samples = {}
        logger.info("Sampling negative items")

        for user in trange(self.user_count):
            if isinstance(self.train[user][1], tuple):
                seen = {x[0] for x in self.train[user]}
                seen.update(x[0] for x in self.val[user])
                seen.update(x[0] for x in self.test[user])
            else:
                seen = set(self.train[user])
                seen.update(self.val[user])
                seen.update(self.test[user])

            samples = []
            for _ in range(self.sample_size):
                item = np.random.choice(self.item_count) + 1
                while item in seen or item in samples:
                    item = np.random.choice(self.item_count) + 1
                samples.append(item)

            negative_samples[user] = samples

        return negative_samples


class PopularNegativeSampler(NegativeSamplerBase):
    def generate_negative_samples(self):
        popular_items = self.items_by_popularity()

        negative_samplers = {}
        logger.info("Sampling negative items")

        for user in trange(self.user_count):
            seen = set(self.train[user])
            seen.update(self.val[user])
            seen.update(self.test[user])

            samples = []
            for item in popular_items:
                if len(samples) == self.sample_size:
                    break
                if item in seen:
                    continue
                samples.append(item)

            negative_samplers[user] = samples

        return negative_samplers

    def items_by_popularity(self):
        popularity = Counter()
        for user in range(self.user_count):
            popularity.update(self.train[user])
            popularity.update(self.val[user])
            popularity.update(self.test[user])
        popular_items = sorted(popularity, key=popularity.get, reverse=True)
        return popular_items
