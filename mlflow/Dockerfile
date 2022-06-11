FROM python:3.8

RUN pip install mlflow==1.14.1 boto3 gcsfs psycopg2-binary google-cloud-storage

COPY mlflow/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
