FROM python:3.7
RUN apt update && apt install -y python3-venv gcc
RUN apt-get install -y python3-dev build-essential

ENV VENV=/.venv/myenv
RUN python3 -m venv ${VENV}
RUN mkdir -p $VENV/src
ENV PATH=$VENV/bin:$PATH
RUN pip install -U pip
RUN pip install psycopg2 mlflow google-cloud google-cloud-storage

# Mount the credentials json file under the following directory
RUN mkdir -p /workdir/gcloud-credentials/
WORKDIR /workdir/
RUN curl https://sdk.cloud.google.com > install.sh
RUN bash install.sh --disable-prompts --install-dir=/workdir/

# Make sure your credentials file is named gcloud-credentials.json too
ENV GOOGLE_APPLICATION_CREDENTIALS=/workdir/gcloud-credentials/gcloud-credentials.json
ENV PATH=/workdir/google-cloud-sdk/bin:$PATH

# Expose the port that the MLFlow tracking server runs on
EXPOSE 5000

# Copy GCP service account credentials
COPY secrets/gcloud-credentials.json /workdir/gcloud-credentials/gcloud-credentials.json

ENTRYPOINT gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS && \
	gcloud config set project $GCP_PROJECT_ID && \
	mlflow server \
	--default-artifact-root $ARTIFACT_URI \
	--backend-store-uri postgresql://$DB_USERNAME:$DB_PASSWORD@$DB_URL/$DB_NAME --host 0.0.0.0 --port 5000