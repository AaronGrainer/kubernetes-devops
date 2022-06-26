import numpy as np
import pandas as pd
import torch

import mlflow
from common import config
from recommender2.models import Recommender
from recommender2.utils import map_column

model_path = "C:/Users/Grainer/Projects/recommender-devops/model/recommender.ckpt"

run_id = "aa050e4814e84183a9618e763c008a2a"
model_uri = f"runs:/{run_id}/model"


def load():
    data = pd.read_csv(config.MOVIELENS_RATING_DATA_DIR)
    data = data.head(100000)
    movies = pd.read_csv(config.MOVIELENS_MOVIE_DATA_DIR)

    data.sort_values(by="timestamp", inplace=True)

    data, mapping, inverse_mapping = map_column(data, col_name="movieId")
    group_by_train = data.groupby(by="userId")

    model = mlflow.pytorch.load_model(model_uri)
    model.eval()

    movie_to_idx = {
        a: mapping[b]
        for a, b in zip(movies.title.tolist(), movies.movieId.tolist())
        if b in mapping
    }
    idx_to_movie = {v: k for k, v in movie_to_idx.items()}

    return model, movie_to_idx, idx_to_movie


def predict(list_movies):
    model, movie_to_idx, idx_to_movie = load()

    ids = (
        [config.PAD] * (120 - len(list_movies) - 1)
        + [movie_to_idx[a] for a in list_movies]
        + [config.MASK]
    )

    source = torch.tensor(ids, dtype=torch.long).unsqueeze(0)

    with torch.no_grad():
        prediction = model(source)

    masked_pred = prediction[0, -1].numpy()

    sorted_predicted_ids = np.argsort(masked_pred).tolist()[::-1]

    sorted_predicted_ids = [a for a in sorted_predicted_ids if a not in ids]

    return [idx_to_movie[a] for a in sorted_predicted_ids[:30] if a in idx_to_movie]
