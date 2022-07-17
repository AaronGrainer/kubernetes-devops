import json
from http import HTTPStatus
from typing import Any

import schemas
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from utils import database
from utils.helper import construct_response, filter_document

router = APIRouter()


@router.get("/")
@construct_response
def get_recommenders(request: Request, payload: schemas.Recommender) -> Any:
    payload = jsonable_encoder(payload)
    recommenders = database.db_get_recommenders(payload["search"])
    recommenders = [filter_document(recommender) for recommender in recommenders]
    response = {"data": recommenders, "status_code": HTTPStatus.OK}
    return response


@router.get("/prediction")
@construct_response
def get_prediction_recommenders(request: Request) -> Any:
    # landmarks = database.db_get_recommenders()
    # landmarks = [filter_document(landmark) for landmark in landmarks]
    # response = {"data": landmarks, "status_code": HTTPStatus.OK}
    # return response
    pass
