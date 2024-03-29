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


def db_find_document(document_name: str, value: str, limit: int = None) -> List:
    """Perform index search over specified field

    Args:
        document_name (str): Document name
        field (str): Field to search over
        value (str): Search value

    Returns:
        List: Search results
    """
    try:
        collection = get_mongo_collection(document_name)
        if limit:
            documents = list(collection.find({"$text": {"$search": value}}).limit(limit))
        else:
            documents = list(collection.find({"$text": {"$search": value}}))
    except Exception as e:
        documents = []
        logger.error(f"DB Error searching documents. {e}")

    return documents


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


def db_append_unique_document(document_name: str, key_dict: Dict, field: str, value: str):
    """Append to existing document field.

    Args:
        document_name (str): Document name
        documents (Dict): Document details
    """
    try:
        dt = datetime.utcnow()

        collection = get_mongo_collection(document_name)
        document = collection.find_one(key_dict)
        if not document:
            # Add new entry in DB
            document = {**key_dict, field: [value], "created_at": dt, "updated_at": dt}
            collection.insert_one(document)
        else:
            # Remove value from document if already exists
            if value in document[field]:
                document[field].remove(value)

            # Append value to end of list
            document[field].append(value)

            document["updated_at"] = dt

            # Update entry in DB
            collection.update_one(key_dict, {"$set": document})

        return HTTPStatus.OK
    except Exception as e:
        logger.error(f"DB Error inserting document. Error: {e}")
        return HTTPStatus.INTERNAL_SERVER_ERROR
