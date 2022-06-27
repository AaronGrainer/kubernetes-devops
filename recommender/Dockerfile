# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY recommender/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY recommender recommender/
