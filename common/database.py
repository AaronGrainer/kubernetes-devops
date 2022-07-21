from datetime import datetime
from http import HTTPStatus
from typing import Dict, List

from pymongo import MongoClient

from common import config, constant
from common.config import logger

MCLIENT = MongoClient(config.MONGO_CLIENT)


def get_mongo_collection(collection_name: str):
    """Format a mongo client collection.

    Args:
        collection_name (str): Collection name
    """
    return MCLIENT[constant.DATABASE][collection_name]


def db_get_documents(document_name: str, search_dict: Dict, limit: int = None) -> List:
    """Retrieve the documents.

    Args:
        document_name (str): Document name
        search_dict (Dict): Query dictionary

    Returns:
        List: List of documents
    """
    try:
        collection = get_mongo_collection(document_name)
        if limit:
            documents = list(collection.find(search_dict).limit(limit))
        else:
            documents = list(collection.find(search_dict))
    except Exception as e:
        documents = []
        logger.error(f"DB Error retrieving documents. {e}")

    return documents


def db_insert_documents(document_name: str, documents: List[Dict]):
    """Insert documents.

    Args:
        document_name (str): Document name
        documents (Dict): Document details
    """
    try:
        dt = datetime.utcnow()

        for document in documents:
            document.update({"created_at": dt, "updated_at": dt})

        collection = get_mongo_collection(document_name)
        collection.insert_many(documents)

        return HTTPStatus.OK
    except Exception as e:
        logger.error(f"DB Error inserting document. Error: {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR
