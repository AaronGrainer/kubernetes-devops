import json

from bson import ObjectId
from kafka import KafkaConsumer

from common import config, database
from common.config import logger


def main():
    consumer = KafkaConsumer(
        "user_selection",
        bootstrap_servers=[config.KAFKA_CONSUMER_URL],
        enable_auto_commit=True,
        group_id=None,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    for message in consumer:
        logger.info(f"Received message from broker: {message}")
        value = message.value

        database.db_append_unique_document(
            "user", {"uid": ObjectId(value["uid"])}, "selected_movies", value["movie"]
        )


if __name__ == "__main__":
    main()
