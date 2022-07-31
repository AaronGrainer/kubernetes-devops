import json

import streamlit as st
from kafka import KafkaProducer

from common import config
from frontend.authentication import check_password
from frontend.utils import send_request


def main():
    st.title(config.TITLE)
    st.write(config.DESCRIPTION)

    st.write(config.KAFKA_URL)

    producer = KafkaProducer(
        bootstrap_servers=config.KAFKA_URL, value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    producer.send("fizzbuzz", {"foo": "bar"})


if __name__ == "__main__":
    if check_password():
        main()
