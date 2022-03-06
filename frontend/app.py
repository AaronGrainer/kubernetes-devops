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
    try:
        if method == "GET":
            response = requests.get(url, json=payload)
            logger.info("response: ", response)

        if response.status_code < 200 or response.status_code >= 300:
            logger.error(
                f"Request to {url} with {payload}\n"
                f"Comment status_code: {response.status_code}, "
                f"response text: {response.text}"
            )
    except Exception as e:
        logger.error(f"Error sending request to {url}. {e}")


def main():
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    send_request("GET", "")


if __name__ == "__main__":
    main()
