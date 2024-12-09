# pylint: disable=redefined-outer-name

"""Import libraries"""
import os
import logging
from typing import List
from dotenv import dotenv_values
from boto3 import client, Session

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

BUCKET = "sigma-resources-truck"
HISTORICAL_PREFIX = "historical/"
METADATA_PREFIX = "metadata/"


def initialise_s3_client(config: dict) -> Session.client:
    """Initialise and return the S3 client."""
    try:
        s3 = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                    aws_secret_access_key=config["SECRET_ACCESS_KEY"])
        logging.info("S3 client initialised successfully.")
        return s3
    except Exception as e:
        logging.error("Error initializing S3 client: %s", str(e))
        raise


def download_files(s3, bucket: str, prefix: str, file_extension: str) -> List[str]:
    """Downloads relevant .parquet truck data files from S3 to the data/historical/ folder."""
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' not in response:
            logging.warning(
                "No files found with prefix '%s' in bucket '%s'", prefix, bucket)
            return []

        downloaded_files = []
        os.makedirs(f"data/{prefix}", exist_ok=True)

        for obj in response['Contents']:
            file_key = obj['Key']

            if not file_key.endswith(file_extension):
                continue

            local_file_path = os.path.join("data", file_key)
            s3.download_file(bucket, file_key, local_file_path)
            downloaded_files.append(local_file_path)
            logging.info("Downloaded file: %s", file_key)

        return downloaded_files
    except Exception as e:
        logging.error("Error downloading files: %s", str(e))
        return []


if __name__ == "__main__":
    config = dotenv_values(".env")
    s3 = initialise_s3_client(config)

    historical_files = download_files(
        s3,
        BUCKET,
        HISTORICAL_PREFIX,
        file_extension='.parquet'
    )
    logging.info("Downloaded historical truck data files: %s",
                 historical_files)

    metadata_files = download_files(
        s3,
        BUCKET,
        METADATA_PREFIX,
        file_extension='.xlsx'
    )
    logging.info("Downloaded metadata files: %s", metadata_files)
