import json
import re

import streamlit as st
from bson.objectid import ObjectId
from kafka import KafkaProducer

from common import config
from common.config import logger
from frontend.authentication import check_password
from frontend.utils import send_request

producer = KafkaProducer(
    bootstrap_servers=[config.KAFKA_PRODUCER_URL],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def search(search_text):
    payload = {"text": search_text, "limit": 10}
    response = send_request("search", "GET", payload)

    movies = [movie["title"] for movie in response.get("data", [])]
    return movies


def recommend():
    uid = st.session_state["uid"]
    payload = {"uid": str(uid), "limit": 5}
    response = send_request("recommender/predict", "GET", payload)

    movies = [movie for movie in response.get("data", [])]
    return movies


def send_broker_message(movie):
    if movie:
        logger.info(f"Sending message to broker: {movie}")
        uid = st.session_state["uid"]
        producer.send("user_selection", {"uid": str(uid), "movie": movie})


def movie_selection_action(movie):
    # TODO: Display movie details

    # Record user selection movie for future recommendations
    send_broker_message(movie)


def main():
    if "uid" not in st.session_state:
        st.session_state["uid"] = ObjectId()

    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    search_text = st.text_input("Movie Search")

    if search_text:
        # If searching, display the movie search results
        movies = search(search_text)
        if movies:
            st.write("Here's what I've found")
    else:
        # If not searching, recommend some movies
        movies = recommend()
        if movies:
            st.write("Here are some movie recommendations!")

    if movies and isinstance(movies, list):
        for movie in movies:
            year_bracket_regex = r"\(.*\)$"
            title = re.sub(year_bracket_regex, "", movie)
            title = title.strip()

            st.button(title, on_click=movie_selection_action, args=[movie])


if __name__ == "__main__":
    if check_password():
        main()
