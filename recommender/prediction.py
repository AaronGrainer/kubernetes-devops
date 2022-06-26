import numpy as np
import pandas as pd
import torch

import mlflow
from common import config
from common.config import logger
from recommender.utils import map_column


class RecommenderPredictor:
    def __init__(self):
        self.run_id = "c30e120a9d4947c5a641cbceaa989d8e"

        model, movie_to_idx, idx_to_movie = self.load()
        self.model = model
        self.movie_to_idx = movie_to_idx
        self.idx_to_movie = idx_to_movie

    def load(self):
        logger.info("Loading recommender predictor")
        data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
        data = data.head(100000)
        movies = pd.read_csv(config.MOVIELENS_MOVIE_DATA_DIR)

        data.sort_values(by="timestamp", inplace=True)
        data, mapping, _ = map_column(data, col_name="movieId")

        model = mlflow.pytorch.load_model(config.MODEL_URI.format(self.run_id))
        model.eval()

        movie_to_idx = {
            a: mapping[b]
            for a, b in zip(movies.title.tolist(), movies.movieId.tolist())
            if b in mapping
        }
        idx_to_movie = {v: k for k, v in movie_to_idx.items()}

        return model, movie_to_idx, idx_to_movie

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
