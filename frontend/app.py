from typing import Dict

import config
import folium
import requests
import streamlit as st
from config import logger
from streamlit_folium import folium_static


def send_request(method: str, endpoint: str, payload: Dict = {}):
    """Send request to backend.

    Args:
        method (str): Method type (GET, POST, PUT, DELETE)
        endpoint (str): The url endpoint to hit
        payload (str): Request payload
    """
    url = f"{config.BACKEND_URL}/{endpoint}"
    logger.info(f"Sending {method} request to {url} with payload: {payload}")
    try:
        if method == "GET":
            response = requests.get(url, json=payload, headers={"x-token": "evelyn"})

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


def display_map():
    # Initialize folium
    m = folium.Map(location=config.SINGPORE_LONG_LAT, zoom_start=config.FOLIUM_ZOOM)

    # Retrive landmarks
    response = send_request("GET", "landmarks")
    landmarks = response.get("data")

    # Add markers for Landmarks
    for landmark in landmarks:
        coordinate = landmark.get("coordinate")
        if coordinate:
            name = landmark.get("name", "")
            description = landmark.get("description", "")
            type = landmark.get("type", "Place Of Interest")

            iframe = folium.IFrame(f"<b>{name}</b><br><br>{description}")
            popup = folium.Popup(iframe, min_width=300, max_width=300)
            icon = folium.Icon(color=config.FOLIUM_LANDMARK_COLOR.get(type, "blue"))
            folium.Marker(coordinate, popup=popup, tooltip=name, icon=icon).add_to(m)

    # Render Folium map in Streamlit
    folium_static(m)


def main():
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    display_map()


if __name__ == "__main__":
    main()
