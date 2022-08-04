from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request
from fastapi.encoders import jsonable_encoder

from backend import schemas
from backend.utils.helper import construct_response, filter_document
from common import constant, database

router = APIRouter()


@router.get("/search")
@construct_response
def search(request: Request, text: str, limit: int) -> Any:
    movies = database.db_find_document(constant.MOVIE, text, limit)

    movies = [filter_document(movie) for movie in movies]
    response = {"data": movies, "status_code": HTTPStatus.OK}

    return response
