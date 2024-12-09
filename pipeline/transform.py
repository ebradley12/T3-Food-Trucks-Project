"""Import libraries"""
import os
import logging
import pandas as pd


INPUT_DIR = 'data/historical'
OUTPUT_FILE = 'data/historical/combined_transactions.csv'

CARD_PAYMENT_ID = 1
CASH_PAYMENT_ID = 2


def extract_truck_id(file_path: str) -> str:
    """Extract truck ID from filename."""
    filename = os.path.basename(file_path)
    truck_id = filename.split('_')[-1].replace('.parquet', '')
    return truck_id


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the DataFrame by removing invalid rows and converting data types."""
    df = df[df['total'].notnull() & (df['total'] != 0) &
            (df['total'] != 'VOID')]
    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    df = df.dropna(subset=['total'])

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    df['type'] = df['type'].str.lower().replace(
        {'card': CARD_PAYMENT_ID, 'cash': CASH_PAYMENT_ID})
    df = df.rename(columns={'type': 'payment_method_id'})
    df['payment_method_id'] = df['payment_method_id'].astype(int)
    logging.info("Data cleaning complete.")
    return df


def combine_transaction_data_files(input_dir: str, output_file: str) -> None:
    """Combine all .parquet files in input_dir into a single CSV file."""
    all_truck_data = []

    for file_name in os.listdir(input_dir):
        if file_name.endswith('.parquet'):
            file_path = os.path.join(input_dir, file_name)
            trucks = pd.read_parquet(file_path)

            trucks['truck_id'] = extract_truck_id(file_path)
            trucks = clean_data(trucks)
            all_truck_data.append(trucks)

    combined_df = pd.concat(all_truck_data, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    logging.info("Combined transaction data saved to %s", output_file)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    combine_transaction_data_files(INPUT_DIR, OUTPUT_FILE)
