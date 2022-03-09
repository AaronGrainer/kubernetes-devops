import json
from http import HTTPStatus
from typing import Any

import schemas
from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder
from utils import database
from utils.cache import set_cache
from utils.helper import construct_response, filter_document

router = APIRouter()


@router.get("/")
@construct_response
def get_landmarks(request: Request) -> Any:
    landmarks = database.db_get_landmarks()
    landmarks = [filter_document(landmark) for landmark in landmarks]
    set_cache("landmarks", json.dumps(landmarks))
    response = {"data": landmarks, "status_code": HTTPStatus.OK}
    return response


@router.post("/")
@construct_response
def insert_landmarks(request: Request, payload: schemas.Landmark) -> Any:
    payload = jsonable_encoder(payload)
    status_code = database.db_insert_landmarks(payload)
    response = {"status_code": status_code}
    return response
