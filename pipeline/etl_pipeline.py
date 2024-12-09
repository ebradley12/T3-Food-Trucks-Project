# pylint: disable=redefined-outer-name

"""ETL Pipeline for Loading Transaction Data from S3 to Redshift."""
import os
import logging
from dotenv import load_dotenv
from extract import initialise_s3_client, download_files
from transform import combine_transaction_data_files
from load import upload_transaction_data


def etl_pipeline():
    """Run the full ETL pipeline."""

    load_dotenv()

    config = {
        "ACCESS_KEY_ID": os.getenv("ACCESS_KEY_ID"),
        "SECRET_ACCESS_KEY": os.getenv("SECRET_ACCESS_KEY")
    }

    try:
        s3 = initialise_s3_client(config)
        historical_files = download_files(
            s3, os.getenv("BUCKET"), "historical/", file_extension='.parquet')

        if not historical_files:
            logging.warning("No historical files downloaded.")
            return

        combine_transaction_data_files(
            "data/historical", "data/historical/combined_transactions.csv")

        upload_transaction_data("data/historical/combined_transactions.csv")

        logging.info("ETL pipeline completed successfully.")

    except Exception as e:
        logging.error("ETL pipeline failed: %s", str(e))


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    etl_pipeline()
