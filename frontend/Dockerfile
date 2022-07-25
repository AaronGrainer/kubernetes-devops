# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY frontend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY common common
COPY frontend frontend

# Install dependencies

# Export ports
EXPOSE 3000

# Start app
ENTRYPOINT python -m streamlit run frontend/app.py \
    --server.port 8501 \
    --theme.base light
