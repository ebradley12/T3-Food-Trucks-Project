# pylint: disable=redefined-outer-name
# pylint: disable=broad-exception-caught

"""Extraction Script to Download Truck Data from S3."""
import os
import logging
import argparse
import boto3
from dotenv import load_dotenv

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

load_dotenv()

BUCKET = os.getenv("BUCKET")
TRUCKS_FOLDER = "trucks/"
DOWNLOAD_DIR = "data"


def connect_to_s3():
    """Connect to S3 using boto3 client."""
    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY")
        )
        logging.info("Successfully connected to S3.")
        return s3_client
    except Exception as e:
        logging.error("Error connecting to S3: %s", str(e))
        raise


def list_files_by_date_and_hour(s3_client, bucket_name: str, datetime_str: str) -> list[str]:
    """List files in S3 bucket for a given date and time."""
    year, month, day, hour = map(int, datetime_str.split("-"))
    date_prefix = f"{TRUCKS_FOLDER}{year}-{month}/{day}/{hour}/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=date_prefix)

        if 'Contents' not in response:
            return []

        matched_files = [obj['Key']
                         for obj in response['Contents'] if obj['Key'].endswith('.csv')]

        if not matched_files:
            logging.warning(
                "No .csv files found for the specified date: %s", date_prefix)

        return matched_files
    except Exception as e:
        logging.error("Error listing files: %s", str(e))
        return []


def download_files(s3_client, bucket_name: str, files: list[str], download_dir: str) -> list[str]:
    """Download specified files from S3 to the local directory."""
    os.makedirs(download_dir, exist_ok=True)

    downloaded_files = []

    for file_key in files:
        file_name = os.path.basename(file_key)
        local_path = os.path.join(download_dir, file_name)
        try:
            s3_client.download_file(bucket_name, file_key, local_path)
            downloaded_files.append(local_path)
            logging.info("Downloaded file: %s", file_key)
        except Exception as e:
            logging.error("Error downloading file %s: %s", file_key, str(e))

    return downloaded_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download truck data from S3 for a specific date and hour.")
    parser.add_argument(
        "datetime", type=str, help="Date and hour in format 'YYYY-MM-DD-HH' (e.g. '2024-11-04-12')")
    args = parser.parse_args()

    s3_client = connect_to_s3()

    files_to_download = list_files_by_date_and_hour(
        s3_client, BUCKET, args.datetime)

    if files_to_download:
        downloaded_files = download_files(
            s3_client, BUCKET, files_to_download, DOWNLOAD_DIR)
    else:
        logging.info("No files downloaded.")
