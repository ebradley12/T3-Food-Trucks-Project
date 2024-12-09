# T3 Food Trucks Dashboard

## Overview

The T3 Food Trucks Dashboard is an interactive web application that enables users to explore and monitor transaction data for T3’s food trucks. The dashboard is designed to provide insights into financial performance and transaction activity, assisting the T3 team in identifying high-performing trucks, peak transaction times, and preferred payment methods. The app uses Streamlit and Altair for visualization and connects to an AWS Redshift database for data storage.

## Features

The dashboard is organized into two main sections:
1. **Financial Performance**:
   - **Total Revenue per Truck**: A bar chart showing total revenue per truck to identify top-performing trucks.
   - **Average Transaction Value per Truck**: A bar chart showing average transaction value, useful for profitability analysis.
   - **Revenue Trends per Truck**: A line chart that allows trend analysis over time to identify revenue patterns.

2. **Truck Activity and Transactions**:
   - **Transaction Count per Truck**: A bar chart showing the number of transactions per truck, indicating customer engagement.
   - **Peak Transaction Times**: A line chart showing transaction volume by hour, helping to identify peak hours.
   - **Payment Method Distribution**: A pie chart and bar chart displaying the proportions of card and cash payments, highlighting customer payment preferences.

[View the Wireframe Design](./dashboard/food_trucks_wireframe_design.png) for a visual layout of the dashboard structure.

## Setup and Installation

To deploy the dashboard, ensure you have Docker installed on your machine and follow these steps:

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone <repository-url>
cd dashboard 
```


### 2. Set Up Environment Variables
Create a .env file in the dashboard directory with the following variables to securely connect to your Redshift database:
```bash
HOST=<your-redshift-host>
PORT=<your-redshift-port>
USERNAME=<your-redshift-username>
PASSWORD=<your-redshift-password>
DATABASE_NAME=<your-database-name>
```

### 3. Install Dependencies
Ensure all dependencies are listed in requirements.txt. If you haven't done so already, update the requirements.txt file with the necessary libraries, then install:
```bash
pip install -r requirements.txt 
```

### 4. Dockerize and Build the Dashboard
The dashboard is set up to run within a Docker container. The Dockerfile is configured to use Python 3.12, install required dependencies, and expose the necessary port.

Build the Docker Image
Use the following command to build the Docker image for the dashboard:
```bash
docker build -t t3-food-trucks-dashboard .
```

### 5. Run the Docker Container Locally
Run the Docker container and expose port 8501 to access the Streamlit dashboard:
```bash
docker run -p 8501:8501 --env-file .env t3-food-trucks-dashboard
```

### 6. Access the Dashboard
Once the container is running, open your web browser and navigate to:
```bash
http://localhost:8501
```

## Deployment on AWS ECS

For deployment on AWS ECS, follow these steps:

### 1. Create an ECR Repository: Store your Docker image in an Amazon ECR repository.

### 2. Use --platform linux/amd64 to ensure compatibility with AWS architecture when building the image.
Upload the Docker Image to ECR:

### 3. Authenticate with ECR and push your image to the repository.
Set Up ECS Task Definition: Create a task definition in ECS, referencing the Docker image URI from ECR and configuring the necessary port (8501) and environment variables.

### 4. Create ECS Service: Launch the service using the task definition to make the dashboard accessible in the cloud.

## Usage

The dashboard includes the following filters in the sidebar:

 - Date Range: Allows users to filter transactions by a specified date range.
- Truck: Filter data for specific trucks.
- Payment Method: Toggle between cash, card, or both types of payments.

---

## Code Overview
- dashboard.py: The main dashboard script, which connects to Redshift, applies filters, and generates visualizations using Altair and Streamlit.
- Dockerfile: Sets up the container environment for running the dashboard.
- .env: Stores sensitive environment variables such as database credentials (excluded from version control).
- requirements.txt: Lists the dependencies required to run the dashboard.
