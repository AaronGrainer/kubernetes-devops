from typing import Dict

import config
import requests
import streamlit as st
from config import logger


def send_request(method: str, endpoint: str, payload: Dict = {}):
    """Send request to backend.

    Args:
        method (str): Method type (GET, POST, PUT, DELETE)
        endpoint (str): The url endpoint to hit
        payload (str): Request payload
    """
    url = f"{config.BACKEND_URL}/{endpoint}"
    logger.info(f"Sending {method} request to {url} with {payload}")
    try:
        if method == "GET":
            response = requests.get(url, json=payload)

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


def main():
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    response = send_request("GET", "")
    st.write(response)


if __name__ == "__main__":
    main()
