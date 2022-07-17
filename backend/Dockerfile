# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY backend .

# Export ports
EXPOSE 3001

# Start app
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
