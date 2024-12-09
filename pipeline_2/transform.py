# pylint: disable=broad-exception-caught
"""Transform script to clean and process the downloaded data ready for upload."""
import os
import logging
import pandas as pd

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

CARD_PAYMENT_ID = 1
CASH_PAYMENT_ID = 2


def extract_truck_id(file_path: str) -> int:
    """Extract truck ID from filenames with format T3_T[truck_id]_[other metadata].csv."""
    filename = os.path.basename(file_path)
    parts = filename.split('_')

    if len(parts) > 2 and parts[0] == "T3" and parts[1][1:].isdigit():
        truck_id = int(parts[1][1:])
        return truck_id

    raise ValueError(
        f"Error extracting truck ID from {filename}")


def load_data_from_directory(directory: str) -> pd.DataFrame:
    """ Load data from all CSV files in a specified directory into a single DataFrame."""
    dataframes = []
    for file in os.listdir(directory):
        if file.endswith(".csv") and file.startswith("T3_T"):
            file_path = os.path.join(directory, file)
            try:
                df = pd.read_csv(file_path)
                df['truck_id'] = extract_truck_id(file_path)
                dataframes.append(df)
                logging.info("Loaded data from %s", file_path)
            except Exception as e:
                logging.error("Error loading %s: %s", file_path, str(e))

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data by handling unexpected, invalid, extreme and missing values."""

    df['total'] = pd.to_numeric(df['total'], errors='coerce')
    df = df.dropna(subset=['total'])

    df = df[(df['total'] > 0) & (df['total'] <= 100)]

    df['total'] = df['total'].round(2).astype(
        float).apply(lambda x: f"{x:.2f}")

    df['type'] = df['type'].str.lower().replace(
        {'card': CARD_PAYMENT_ID, 'cash': CASH_PAYMENT_ID})
    df = df.rename(columns={'type': 'payment_method_id'})
    df['payment_method_id'] = df['payment_method_id'].astype(int)

    logging.info("Data cleaning complete.")
    return df


def save_clean_data(df: pd.DataFrame, output_file: str) -> None:
    """Save the cleaned DataFrame to a CSV file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    logging.info("Cleaned data saved to %s", output_file)


if __name__ == "__main__":
    raw_data = load_data_from_directory("data")
    if not raw_data.empty:
        cleaned_data = clean_data(raw_data)
        save_clean_data(cleaned_data, "data/cleaned_data.csv")
    else:
        logging.warning("No data loaded; cleaned data file not created.")
