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


def db_get_locations():
    """Retrieve the full list of location details."""
    try:
        collection = get_mongo_collection(constant.LOCATION)
        locations = list(collection.find({}))
    except Exception as e:
        locations = []
        logger.error(f"DB Error retrieving location. {e}")

    return locations
