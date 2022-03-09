from datetime import datetime
from http import HTTPStatus
from typing import Dict, List

import config
from config import logger
from pymongo import MongoClient
from utils import constant

MCLIENT = MongoClient(config.MONGO_CLIENT)


def get_mongo_collection(collection_name: str):
    """Format a mongo client collection.

    Args:
        collection_name (str): Collection name
    """
    return MCLIENT[constant.DATABASE][collection_name]


def db_get_landmarks() -> List:
    """Retrieve the full list of landmark details.

    Returns:
        List: List of landmarks
    """
    try:
        collection = get_mongo_collection(constant.LANDMARK)
        landmarks = list(collection.find({}))
    except Exception as e:
        landmarks = []
        logger.error(f"DB Error retrieving landmark. {e}")

    return landmarks


def db_insert_landmarks(details: Dict):
    """Insert a new landmark.

    Args:
        details (Dict): Landmark details
    """
    try:
        dt = datetime.utcnow()
        details.update({"created_at": dt, "created_at": dt})
        collection = get_mongo_collection(constant.LANDMARK)
        collection.insert_one(details)
        return HTTPStatus.OK
    except Exception as e:
        logger.error(f"DB Error inserting landmark: {details}. {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR
