from datetime import datetime
from functools import wraps
from typing import Dict

import requests
from fastapi import Request

from common.config import logger


def construct_response(f):
    """Construct a JSON response for an endpoint's results."""

    @wraps(f)
    def wrap(request: Request, *args, **kwargs):
        results = f(request, *args, **kwargs)

        # Construct response
        response = {
            "method": request.method,
            "message": results["status_code"].phrase,
            "status_code": results["status_code"],
            "timestamp": datetime.now().isoformat(),
            "url": request.url._url,
        }

        # Add data
        if "data" in results:
            response["data"] = results["data"]

        return response

    return wrap


def send_request(base_url: str, endpoint: str, method: str, payload: Dict = {}):
    """Send request to backend.

    Args:
        base_url (str): Base URL
        endpoint (str): The url endpoint to hit
        method (str): Method type (GET, POST, PUT, DELETE)
        payload (str): Request payload
    """
    url = f"{base_url}/{endpoint}"
    logger.info(f"Sending {method} request to {url} with payload: {payload}")
    try:
        if method == "GET":
            response = requests.get(url, json=payload, headers={"x-token": "super-secret"})
        elif method == "POST":
            response = requests.post(url, json=payload, headers={"x-token": "super-secret"})

        if response.status_code < 200 or response.status_code >= 300:
            logger.error(
                f"Request to {url} with {payload}\n"
                f"Comment status_code: {response.status_code}, "
                f"response text: {response.text}"
            )
            return {}

        response_json = response.json()
        logger.info(f"Received response: {response_json}")
        return response_json
    except Exception as e:
        logger.error(f"Error sending request to {url}. {e}")
        return {}


def filter_document(document):
    document.pop("_id", None)
    document.pop("created_at", None)
    document.pop("updated_at", None)

    return document
