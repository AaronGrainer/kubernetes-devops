# Base image
FROM python:3.9-slim

RUN apt-get update

# Install dependencies
COPY frontend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy
COPY frontend .

# Install dependencies

# Export ports
EXPOSE 3000

# Start app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port", "3000", "--theme.base", "light"]
