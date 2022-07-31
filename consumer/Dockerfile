# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY consumer/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY common common/
COPY consumer consumer/

# Export ports
EXPOSE 3000

# Start app
ENTRYPOINT python -m consumer.app
