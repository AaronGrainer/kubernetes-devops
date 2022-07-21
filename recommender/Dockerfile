# Base image
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

# Install dependencies
COPY recommender/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY data/ml-20m/ratings.csv data/ml-20m/ratings.csv
COPY data/ml-20m/movies.csv data/ml-20m/movies.csv

COPY common common/
COPY recommender recommender/

ENTRYPOINT uvicorn recommender.app:app --host 0.0.0.0 --port 4000
