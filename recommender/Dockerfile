# Base image
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

# Install dependencies
COPY recommender/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY common common/
COPY recommender recommender/
COPY data/ml-20m/ratings.csv data/ml-20m/ratings.csv
COPY data/ml-20m/movies.csv data/ml-20m/movies.csv

ENTRYPOINT uvicorn recommender.app:app --port 4000
