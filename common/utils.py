from typing import Dict

import requests

from common.config import logger


def send_request(
    base_url: str, endpoint: str, method: str, headers: Dict = None, payload: Dict = {}
):
    """Send REST API request.

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
            response = requests.get(url, data=payload, headers=headers)
        elif method == "POST":
            response = requests.post(url, data=payload, headers=headers)

        if response.status_code < 200 or response.status_code >= 300:
            logger.error(
                f"Request to {url} with {payload}\n"
                f"Comment status_code: {response.status_code}, "
                f"response text: {response.text}"
            )
            return response.status_code, {}

        response_json = response.json()
        logger.info(f"Received response: {response_json}")
        return response.status_code, response_json
    except Exception as e:
        logger.error(f"Error sending request to {url}. {e}")
        return response.status_code, {}
