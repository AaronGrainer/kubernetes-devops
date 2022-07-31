from kafka import KafkaConsumer

from common import config


def main():
    print("config.KAFKA_URL: ", config.KAFKA_URL)
    consumer = KafkaConsumer(bootstrap_servers=config.KAFKA_URL)
    for message in consumer:
        print("message: ", message)


if __name__ == "__main__":
    main()
