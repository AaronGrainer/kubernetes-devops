import json
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Request
from utils.cache import set_cache
from utils.database import db_get_locations
from utils.helper import construct_response

router = APIRouter()


@router.get("/", status_code=HTTPStatus.OK)
@construct_response
def get_locations(request: Request) -> Any:
    locations = db_get_locations()
    locations = [{"coordinate": loc["coordinate"]} for loc in locations]
    set_cache("locations", json.dumps(locations))
    return {"data": locations}
