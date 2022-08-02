import json

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


def send_broker_message(movie):
    logger.info(f"Sending message to broker: {movie}")
    uid = st.session_state["uid"]
    producer.send("user_selection", {"uid": str(uid), "movie": movie})


def main():
    if "uid" not in st.session_state:
        st.session_state["uid"] = ObjectId()

    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    movie = "Harry Potter and the Deathly Hallows: Part 2 (2011)"
    st.button("Harry Potter", on_click=send_broker_message, args=[movie])

    movie = "Apollo 13 (1995)"
    st.button("Apollo 13", on_click=send_broker_message, args=[movie])

    movie = "Batman Begins (2005)"
    st.button("Batman Begins", on_click=send_broker_message, args=[movie])


if __name__ == "__main__":
    if check_password():
        main()
