# pylint: disable=broad-exception-caught

"""Import modules"""
import os
import logging
import pandas as pd
import redshift_connector
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
load_dotenv()


def get_redshift_connection():
    """Establish and return a connection to the Redshift database."""
    try:
        conn = redshift_connector.connect(
            host=os.environ["HOST"],
            port=int(os.environ.get("PORT", 5439)),
            user=os.environ["USERNAME"],
            password=os.environ["PASSWORD"],
            database=os.environ["DATABASE_NAME"]
        )
        conn.autocommit = True
        logging.info("Connected to Redshift.")
        return conn
    except Exception as e:
        logging.error("Error connecting to Redshift: %s", str(e))
        raise


def upload_transaction_data(data_file: str):
    """Uploads transaction data to Redshift database."""
    df = pd.read_csv(data_file)
    conn = get_redshift_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"SET search_path TO {os.environ['SCHEMA']};")
            insert_query = """
            INSERT INTO FACT_Transaction (truck_id, payment_method_id, total, at)
            VALUES (%s, %s, %s, %s);
            """
            for _, row in df.iterrows():
                cursor.execute(insert_query, (
                    row['truck_id'],
                    row['payment_method_id'],
                    row['total'],
                    row['timestamp']
                ))

            logging.info("Data uploaded to Redshift.")

    except Exception as e:
        logging.error("Error uploading data: %s", str(e))

    finally:
        conn.close()


if __name__ == "__main__":

    data = os.getenv(
        "DATA_FILE", "data/cleaned_data.csv")

    logging.info("Starting data upload for file: %s", data)
    upload_transaction_data(data)
