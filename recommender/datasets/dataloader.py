from abc import ABCMeta, abstractmethod

from common import config
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
