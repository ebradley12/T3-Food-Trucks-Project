# pylint: disable=redefined-outer-name, broad-exception-caught

"""ETL Pipeline for Processing and Uploading Truck Data"""
import os
import logging
from datetime import datetime, timedelta, timezone
import pandas as pd
from dotenv import load_dotenv
from extract import connect_to_s3, list_files_by_date_and_hour, download_files
from transform import load_data_from_directory, clean_data, save_clean_data
from load import upload_transaction_data

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
load_dotenv()

BUCKET = os.getenv("BUCKET")
DOWNLOAD_DIR = "data"


def get_recent_datetime_strs(hours=3) -> list[str]:
    """Get a list of datetime strings for each of the last three hours."""
    now = datetime.now(timezone.utc)
    return [(now - timedelta(hours=i)).strftime("%Y-%m-%d-%H") for i in range(hours)]


def extract_data(s3_client, bucket: str, datetime_str: str) -> list[str]:
    """Extract and download files from S3 based on datetime."""
    files_to_download = list_files_by_date_and_hour(
        s3_client, bucket, datetime_str)
    if files_to_download:
        for file in os.listdir(DOWNLOAD_DIR):
            os.remove(os.path.join(DOWNLOAD_DIR, file))
        return download_files(s3_client, bucket, files_to_download, DOWNLOAD_DIR)
    logging.info("No data files found for datetime %s.", datetime_str)
    return []


def transform_data(input_dir: str, output_file: str) -> pd.DataFrame:
    """Transform the raw data by loading, cleaning, and saving it."""
    raw_data = load_data_from_directory(input_dir)
    if not raw_data.empty:
        cleaned_data = clean_data(raw_data)
        save_clean_data(cleaned_data, output_file)
        logging.info("Data transformation complete.")
        return cleaned_data
    return pd.DataFrame()


def load_data_to_database(cleaned_data_file: str) -> None:
    """Load the cleaned data into the database."""
    upload_transaction_data(cleaned_data_file)
    logging.info("Data loaded into the database successfully.")


def run_pipeline():
    """Main function to run the ETL pipeline."""
    datetime_strs = get_recent_datetime_strs()
    s3_client = connect_to_s3()

    for datetime_str in datetime_strs:
        extracted_files = extract_data(s3_client, BUCKET, datetime_str)

        cleaned_data_file = os.path.join(DOWNLOAD_DIR, "cleaned_data.csv")
        transformed_data = transform_data(DOWNLOAD_DIR, cleaned_data_file)

        if not transformed_data.empty:
            logging.info("Loading transformed data to database.")
            load_data_to_database(cleaned_data_file)

            for file in extracted_files:
                os.remove(file)
        else:
            logging.warning(
                "No valid data to load for datetime %s.", datetime_str)


if __name__ == "__main__":
    run_pipeline()
