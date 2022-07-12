from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from recommender.db import get_latest_mlflow_run_id
from recommender.prediction import RecommenderPredictor

app = FastAPI()

mlflow_run_id = get_latest_mlflow_run_id()
recommender = RecommenderPredictor(mlflow_run_id)


class RecommendItem(BaseModel):
    user_movies: List


@app.post("/recommend")
async def recommend(recommender_item: RecommendItem):
    predicted_movies = recommender.predict(recommender_item.user_movies)
    return predicted_movies


@app.get("/")
async def main():
    return {"message": "Recommender Predictor"}
