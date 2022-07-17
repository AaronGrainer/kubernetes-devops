from typing import List

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from pydantic import BaseModel

from recommender.prediction import RecommenderPredictor

app = FastAPI()


recommender = None


class RecommendItem(BaseModel):
    user_movies: List


@app.on_event("startup")
async def startup_event():
    global recommender

    recommender = RecommenderPredictor()

    scheduler = BackgroundScheduler()

    scheduler.add_job(recommender.hot_reload, "interval", minutes=1)
    scheduler.start()


@app.post("/recommend")
async def recommend(recommender_item: RecommendItem):
    if recommender:
        predicted_movies = recommender.predict(recommender_item.user_movies)
        return predicted_movies
    else:
        return []


@app.get("/")
async def main():
    return {"message": "Recommender Predictor"}
