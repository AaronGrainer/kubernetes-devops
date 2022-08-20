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
    payload = {"uid": str(uid), "limit": 6}
    response = send_request("movie/recommend", "GET", payload)

    movies = [movie for movie in response.get("data", [])]
    return movies


def get_movie_summary(movie):
    payload = {"movie_title": movie}
    response = send_request("movie/summary", "GET", payload)

    movie_summary = response.get("data", {}).get("movie_summary")
    return movie_summary


def send_broker_message(movie):
    if movie:
        logger.info(f"Sending message to broker: {movie}")
        uid = st.session_state["uid"]
        producer.send("user_selection", {"uid": str(uid), "movie": movie})


def movie_selection_action(movie):
    # Get the selected movie summary and set ST session for downstream display
    movie_summary = get_movie_summary(movie)
    st.session_state["movie_title"] = movie
    st.session_state["movie_summary"] = movie_summary

    # Record user selection movie for future recommendations
    send_broker_message(movie)


def main():
    if "uid" not in st.session_state:
        st.session_state["uid"] = ObjectId()

    st.title("Movie Groovy")
    st.write("What's your movie flavor of the day?")

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

    # Display the movie titles in 2 columns
    if movies and isinstance(movies, list):
        st_column_1, st_column_2 = st.columns(2)
        middle_movie_index = int(len(movies) / 2)
        with st_column_1:
            for movie in movies[:middle_movie_index]:
                year_bracket_regex = r"\(.*\)$"
                title = re.sub(year_bracket_regex, "", movie)
                title = title.strip()

                st.button(title, on_click=movie_selection_action, args=[movie])

        with st_column_2:
            for movie in movies[middle_movie_index:]:
                year_bracket_regex = r"\(.*\)$"
                title = re.sub(year_bracket_regex, "", movie)
                title = title.strip()

                st.button(title, on_click=movie_selection_action, args=[movie])

    # If user has selected and movie, display the Movie Title and Movie Summary
    if "movie_title" in st.session_state and "movie_summary" in st.session_state:
        st.subheader(st.session_state["movie_title"])
        st.write(st.session_state["movie_summary"])


if __name__ == "__main__":
    if check_password():
        main()
