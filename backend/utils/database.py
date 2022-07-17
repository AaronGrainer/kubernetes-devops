import re
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


def db_get_recommenders(search: str = None) -> List:
    """Retrieve the full list of recommender details.

    Args:
        search (str): Recommender search

    Returns:
        List: List of recommenders
    """
    try:
        collection = get_mongo_collection(constant.RECOMMENDER)

        search_regex = re.compile(search, re.IGNORECASE)
        recommenders = list(collection.find({"name": search_regex}))
    except Exception as e:
        recommenders = []
        logger.error(f"DB Error retrieving recommender. {e}")

    return recommenders


# def db_insert_landmarks(details: Dict):
#     """Insert a new landmark.

#     Args:
#         details (Dict): Landmark details
#     """
#     try:
#         dt = datetime.utcnow()
#         details.update({"created_at": dt, "created_at": dt})
#         collection = get_mongo_collection(constant.LANDMARK)
#         collection.insert_one(details)
#         return HTTPStatus.OK
#     except Exception as e:
#         logger.error(f"DB Error inserting landmark: {details}. {e}")
#         return HTTPStatus.INTERNAL_SERVER_ERROR
