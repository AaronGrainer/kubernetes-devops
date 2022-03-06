# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY backend .

# Export ports
EXPOSE 8502

# Start app
# ENTRYPOINT ["gunicorn", "-w 1", "--bind=0.0.0.0:8502", "-k", "uvicorn.workers.UvicornWorker", "main:app"]
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8502"]
