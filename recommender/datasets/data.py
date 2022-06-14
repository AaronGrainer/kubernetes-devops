import os
import pickle
import shutil
import tempfile
from abc import ABCMeta, abstractmethod
from pathlib import Path

import pandas as pd
from tqdm import tqdm

tqdm.pandas()

from common import config
from common.config import logger
from recommender.datasets.utils import download, unzip


class DatasetBase(metaclass=ABCMeta):
    def __init__(self):

        self.dataset_path = Path(config.DATA_DIR, "preprocessed", "ml-1m", "dataset.pkl")
        self.raw_dataset_path = Path(config.DATA_DIR, "ml-1m")

        assert config.MIN_UC >= 2, "Need at least 2 ratings per user for validation and test"

    @classmethod
    def dataset_name(cls):
        return "Movielens 1M"

    @classmethod
    @abstractmethod
    def url(cls):
        pass

    @classmethod
    def zip_file_content_is_folder(cls):
        return True

    @classmethod
    def all_raw_file_names(cls):
        return []

    @classmethod
    def load_ratings_df(cls):
        pass

    def load_dataset(self):
        self.preprocess()
        dataset = pickle.load(self.dataset_path.open("rb"))
        return dataset

    def preprocess(self):
        if self.dataset_path.is_file():
            logger.info(f"{self.dataset_name()} is already preprocessed. Skipping preprocessing...")
            return
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        self.download_raw_dataset()
        df = self.load_ratings_df()
        df = self.make_implicit(df)
        df = self.filter_triplets(df)
        df, umap, smap = self.densify_index(df)
        train, val, test = self.split_df(df, len(umap))
        dataset = {"train": train, "val": val, "test": test, "umap": umap, "smap": smap}
        with self.dataset_path.open("wb") as f:
            pickle.dump(dataset, f)

    def download_raw_dataset(self):
        if self.raw_dataset_path.is_dir() and all(
            Path(self.raw_dataset_path, filename).is_file()
            for filename in self.all_raw_file_names()
        ):
            logger.info(
                f"{self.dataset_name()} raw dataset already exists. Skipping downloading..."
            )
            return

        logger.info(f"{self.dataset_name()} raw datasaet doesn't exist. Downloading...")

        temp_root = Path(tempfile.mkdtemp())
        temp_zip = Path(temp_root, "file.zip")
        temp_folder = Path(temp_root, "folder")

        download(self.url(), temp_zip)
        unzip(temp_zip, temp_folder)

        if self.zip_file_content_is_folder():
            temp_folder = Path(temp_folder, os.listdir(temp_folder)[0])

        shutil.move(temp_folder, self.raw_dataset_path)
        shutil.rmtree(temp_root)

    def make_implicit(self, df):
        logger.info(f"Turning {self.dataset_name()} into implicit ratings")
        df = df[df["rating"] >= config.MIN_RATING]
        return df

    def filter_triplets(self, df):
        logger.info(f"Filtering triplets in {self.dataset_name()}")
        if config.MIN_SC > 0:
            item_sizes = df.groupby("sid").size()
            good_items = item_sizes.index[item_sizes >= config.MIN_SC]
            df = df[df["sid"].isin(good_items)]

        if config.MIN_UC > 0:
            user_sizes = df.groupby("uid").size()
            good_users = user_sizes.index[user_sizes >= config.MIN_UC]
            df = df[df["uid"].isin(good_users)]

        return df

    def densify_index(self, df):
        logger.info(f"Densifying indexes in {self.dataset_name()}")
        umap = {u: i for i, u in enumerate(set(df["uid"]))}
        smap = {s: i for i, s in enumerate(set(df["sid"]))}
        df["uid"] = df["uid"].map(umap)
        df["sid"] = df["sid"].map(smap)
        return df, umap, smap

    def split_df(self, df, user_count):
        logger.info(f"Splitting {self.dataset_name()} into train, val and test sets")
        user_group = df.groupby("uid")
        user2items = user_group.progress_apply(lambda d: list(d.sort_values(by="timestamp")["sid"]))
        train, val, test = {}, {}, {}
        for user in range(user_count):
            items = user2items[user]
            train[user], val[user], test[user] = items[:-2], items[-2:-1], items[-1:]
        return train, val, test


class ML1MDataset(DatasetBase):
    @classmethod
    def url(cls):
        return "http://files.grouplens.org/datasets/movielens/ml-1m.zip"

    @classmethod
    def all_raw_file_names(cls):
        return ["README", "movies.dat", "ratings.dat", "users.dat"]

    def load_ratings_df(self):
        filepath = Path(self.raw_dataset_path, "ratings.dat")
        df = pd.read_csv(filepath, sep="::", header=None)
        df.columns = ["uid", "sid", "rating", "timestamp"]
        return df
