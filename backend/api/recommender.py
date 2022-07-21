import re
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder

from backend import schemas
from backend.utils.helper import (
    construct_response,
    filter_document,
    send_request,
)
from common import config, constant, database

router = APIRouter()


@router.get("/")
@construct_response
def get_recommenders(request: Request, payload: schemas.Recommender) -> Any:
    payload = jsonable_encoder(payload)

    search_regex = re.compile(payload["search"], re.IGNORECASE)
    search_dict = {"title": search_regex}
    limit = payload["limit"]

    recommenders = database.db_get_documents(constant.MOVIE, search_dict, limit)

    recommenders = [filter_document(recommender) for recommender in recommenders]
    response = {"data": recommenders, "status_code": HTTPStatus.OK}

    return response


@router.get("/prediction")
@construct_response
def get_prediction_recommenders(request: Request) -> Any:
    payload = {
        "user_movies": [
            "Harry Potter and the Sorcerer's Stone (a.k.a. Harry Potter and the Philosopher's Stone) (2001)",
            "Harry Potter and the Chamber of Secrets (2002)",
            "Harry Potter and the Prisoner of Azkaban (2004)",
            "Harry Potter and the Goblet of Fire (2005)",
        ]
    }
    movie_recommendations = send_request(
        config.RECOMMENDER_ENGINE_URL, "recommend", "POST", payload
    )
    print("movie_recommendations: ", movie_recommendations)

    # landmarks = database.db_get_documents()
    # landmarks = [filter_document(landmark) for landmark in landmarks]
    response = {"data": movie_recommendations, "status_code": HTTPStatus.OK}
    return response
