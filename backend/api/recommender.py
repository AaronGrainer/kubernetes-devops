import re
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder

from backend import schemas
from backend.utils.helper import construct_response, filter_document
from common import constant, database

router = APIRouter()


@router.get("/")
@construct_response
def get_recommenders(request: Request, payload: schemas.Recommender) -> Any:
    payload = jsonable_encoder(payload)

    search_regex = re.compile(payload["search"], re.IGNORECASE)
    search_dict = {"name": search_regex}

    recommenders = database.db_get_documents(constant.RATING, search_dict)

    recommenders = [filter_document(recommender) for recommender in recommenders]
    response = {"data": recommenders, "status_code": HTTPStatus.OK}

    return response


@router.get("/prediction")
@construct_response
def get_prediction_recommenders(request: Request) -> Any:
    # landmarks = database.db_get_documents()
    # landmarks = [filter_document(landmark) for landmark in landmarks]
    # response = {"data": landmarks, "status_code": HTTPStatus.OK}
    # return response
    pass
