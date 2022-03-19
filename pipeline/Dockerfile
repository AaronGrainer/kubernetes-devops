# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY pipeline/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY pipeline .

# Start app
ENTRYPOINT ["python", "-m", "extract_data"]
