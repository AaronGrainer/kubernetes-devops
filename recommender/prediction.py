import numpy as np
import pandas as pd
import torch

import mlflow
from common import config
from common.config import logger
from recommender.db import get_latest_mlflow_run_id
from recommender.utils import map_column


class RecommenderPredictor:
    def __init__(self):
        self.run_id = get_latest_mlflow_run_id()

        self.load()

    def load(self):
        logger.info("Loading recommender predictor")

        logger.info("Loading the dataset")
        data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
        data = data.head(100000)
        movies = pd.read_csv(config.MOVIELENS_MOVIE_DATA_DIR)

        data.sort_values(by="timestamp", inplace=True)
        data, mapping, _ = map_column(data, col_name="movieId")

        logger.info(f"Loading the recommender model: {self.run_id}")
        self.model = mlflow.pytorch.load_model(config.MODEL_URI.format(self.run_id))
        self.model.eval()

        self.movie_to_idx = {
            a: mapping[b]
            for a, b in zip(movies.title.tolist(), movies.movieId.tolist())
            if b in mapping
        }
        self.idx_to_movie = {v: k for k, v in self.movie_to_idx.items()}

    def hot_reload(self):
        logger.info("Checking for new recommender model")
        temp_run_id = get_latest_mlflow_run_id()

        if temp_run_id != self.run_id:
            self.run_id = temp_run_id
            logger.info(f"Found a newer recommender model: {self.run_id}. Hot reloading now")

            self.model = mlflow.pytorch.load_model(config.MODEL_URI.format(self.run_id))
            self.model.eval()
            logger.info("Successfully reloaded the new recommender model")

    def predict(self, user_movies):
        logger.info(f"Recommender predicting with User Movie: {user_movies}")
        ids = (
            [config.PAD] * (120 - len(user_movies) - 1)
            + [self.movie_to_idx[a] for a in user_movies]
            + [config.MASK]
        )
        source = torch.tensor(ids, dtype=torch.long).unsqueeze(0)

        with torch.no_grad():
            prediction = self.model(source)

        masked_pred = prediction[0, -1].numpy()
        sorted_predicted_ids = np.argsort(masked_pred).tolist()[::-1]
        sorted_predicted_ids = [a for a in sorted_predicted_ids if a not in ids]
        predicted_movies = [
            self.idx_to_movie[a] for a in sorted_predicted_ids[:30] if a in self.idx_to_movie
        ]
        logger.info(f"Predicted movides: {predicted_movies}")

        return predicted_movies
