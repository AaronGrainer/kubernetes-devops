import psycopg2

from common import config


def get_latest_mlflow_run_id():
    try:
        connection = psycopg2.connect(
            user=config.POSTGRESQL_USERNAME,
            password=config.POSTGRESQL_PASSWORD,
            host=config.POSTGRESQL_HOST,
            port=config.POSTGRESQL_PORT,
            database=config.POSTGRESQL_MLFLOW_DB,
        )
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM runs ORDER BY end_time desc")
        record = cursor.fetchone()

        mlflow_run_id = record[0]
        return mlflow_run_id
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
