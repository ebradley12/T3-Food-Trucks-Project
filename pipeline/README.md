# Tasty Truck Treats (T3) Data Pipeline Project

This project is part of a data engineering solution for **Tasty Truck Treats (T3)**, a catering company specializing in food trucks. The objective is to build a data pipeline that collects, processes, and analyses transaction-level data from each truck, enabling T3 to make data-driven decisions to optimise their business operations.

## Project Structure

### 1. **Extract Script** (`extract_data.py`)

The extract script connects to T3’s S3 bucket to retrieve all relevant data files. The bucket contains:
- **Historical transaction data** for each truck in `.parquet` format within the `historical/` folder.
- **Metadata** about each truck in an `.xlsx` file within the `metadata/` folder.

**Steps in the Extract Script**:
- Initializes an S3 client using credentials from an `.env` file.
- Downloads transaction data (`.parquet` files) from the `historical/` folder.
- Downloads metadata (`.xlsx` file) from the `metadata/` folder.
- Filters files based on file extension to ensure only `.parquet` or `.xlsx` files are downloaded.
  
**Script Location**: `extract_data.py`

### 2. **Transform Script** (`transform_data.py`)

The transform script loads the downloaded transaction data files and prepares them for analysis. Specifically, it:
- **Combines all transaction data** files into a single CSV file to facilitate cross-truck analysis.
- **Extracts the truck ID** from each file’s name and adds it as a new column in the data.
- **Cleans the data** by:
  - Removing rows where `total` is zero, blank, NULL, or marked as "VOID".
  - Converting columns to appropriate data types (e.g., `total` to numeric, `timestamp` to datetime).
  - Dropping any unnecessary columns.
  
The resulting data is saved to `data/cleaned_combined_transactions.csv`, a consolidated and cleaned dataset ready for analysis.

**Script Location**: `transform_data.py`

### 3. **Load Script** (`load.py`)

The load script uploads the cleaned and transformed data into a Redshift database for further analysis and reporting. It:
- Connects to the Redshift database using credentials in the `.env` file.
- Inserts data from the combined CSV file into the `FACT_Transaction` table in Redshift.

**Script Location**: `load.py`

### 4. **ETL Pipeline Script** (`etl_pipeline.py`)

The `etl_pipeline.py` script orchestrates the full ETL process by running the extract, transform, and load steps in sequence. This script:
- Uses the functions in `extract.py`, `transform.py`, and `load.py`.
- Ensures that data is extracted from S3, transformed for consistency, and loaded into the Redshift database in one seamless process.

**Script Location**: `etl_pipeline.py`

### 5. **Data Exploration Notebook** (`data_analysis.ipynb`)

The data exploration notebook (`data_analysis.ipynb`) loads the cleaned transaction data and performs initial analysis to gain insights into T3’s operations. The notebook answers the following key questions:

- **Which truck has the highest number of transactions?**
- **Which truck has the lowest total transaction value?**
- **What is the average transaction value?**
- **What is the average transaction value for each truck?**
- **What proportion of transactions use cash versus card?**

The notebook also includes **visualisations** created using the Vega-Altair library:

1. **Bar Chart**: Displays the average transaction total for each truck.
2. **Pie Chart**: Shows the proportion of transactions made using cash or card.
3. **Line Chart**: Illustrates daily total transaction values to identify trends.

## Dashboard Application (`dashboard.py`)

The **T3 Food Trucks Dashboard** provides an interactive way to explore transaction data for T3’s food trucks. Built with Streamlit, it includes:
- Visualizations of total revenue, average transaction value, transaction volume by truck, peak transaction times, and payment method distribution.
- Sidebar filters for date range, truck selection, and payment type.

### Docker Setup

To make deployment easier, the ETL pipeline is containerised with Docker. Docker allows for consistent environments and easy deployment on ECS or other cloud platforms.

**Dockerfile for ETL Pipeline** (`Dockerfile`):
```Dockerfile
# Dockerfile for the ETL Pipeline
FROM python:3.8

WORKDIR /pipeline

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "etl_pipeline.py"]

To build and run the Docker container locally:
```bash
docker build -t t3-etl-pipeline .
docker run --env-file .env t3-etl-pipeline
```

## Recommendations

Based on the analysis, the following recommendations have been made to help T3 achieve its business objectives:

1. **Introduce Dynamic Pricing Based on Demand**: Analyse peak times, locations, and customer demographics to implement variable pricing strategies, potentially raising prices slightly during high-demand periods or locations.
2. **Focus on High-Performing Trucks for Marketing**: Use insights from high-performing trucks to boost profitability and apply successful strategies to other trucks.
3. **Experiment with Daily Promotions Based on Revenue Trends**: Implement promotions on days with lower sales to drive traffic and stabilise weekly revenue.


## Setup and Installation

1. **Clone the Repository**: 
   - Clone this repository to your local machine:
   ```bash
   git clone https://github.com/ebradley12/Coursework-Data-Engineering-Week-3.git
   cd dashboard
   ```

2. **Set Up Environment Variables**: 
   - Create a .env file in the root directory with the following variables to securely connect to your AWS and Redshift instances:
   ```bash
   ACCESS_KEY_ID=<your-access-key-id>
   SECRET_ACCESS_KEY=<your-secret-access-key>
   BUCKET=<your-s3-bucket-name>
   HOST=<your-redshift-host>
   PORT=<your-redshift-port>
   USERNAME=<your-redshift-username>
   PASSWORD=<your-redshift-password>
   DATABASE_NAME=<your-database-name>
   SCHEMA=<your-database-schema>
   ```

3. **Install Dependencies**: 
   - Install all required dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt

   ```

4. **Run the Extract Script**: `extract_data.py`
   - Ensure your AWS credentials are in an `.env` file in the root directory.
   - Execute the script to download data files from the S3 bucket.

5. **Run the Transform Script**: `transform_data.py`
   - This script combines, cleans, and saves transaction data to a single CSV file, ready for analysis.

6. **Run the Load Script**: `load.py`
   - Use this script to upload the cleaned and combined transaction data to your Redshift database.

7. **Run the ETL Pipeline Script**: `etl_pipeline.py`
   - Alternatively, you can execute the full ETL pipeline, which runs the extract, transform, and load steps sequentially.

8. **Explore Data in the Notebook**: `data_analysis.ipynb`
   - Open the notebook in Jupyter and follow the steps to analyse and visualise the data.
   - Review the recommendations section to gain insights for T3’s business strategy.

## Project Requirements

- **Python 3+**
- **AWS S3 Access**: Ensure your `.env` file contains `ACCESS_KEY_ID` and `SECRET_ACCESS_KEY`.
- **Libraries**:
  - `pandas`
  - `boto3`
  - `dotenv`
  - `redshift_connector`
  - `streamlit`
  - `altair`

Install required packages with:
```bash
pip3 install pandas boto3 python-dotenv altair