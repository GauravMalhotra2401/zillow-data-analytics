# zillow-data-analytics

Zillow Data Pipeline
**1. Project Overview**
**1.1. Project Title:**

Zillow Data Pipeline: Real Estate Data Extraction, Processing, and Analysis

**1.2. Project Goal:**

This project aims to build an end-to-end data pipeline that extracts real estate data from the Zillow Rapid API, cleans and transforms it, and loads it into a Redshift data warehouse for analysis and visualization using Quicksight. The pipeline is designed to provide insights into real estate market trends, allowing for informed decision-making by business stakeholders.

**1.3. Data Source:**

The primary data source is the Zillow Rapid API, which provides access to real estate property listings, market trends, and other relevant information.

**1.4. Target Audience:**

The target audience for this pipeline includes:

Data Analysts: To perform in-depth analysis of real estate market data.

Business Stakeholders: To gain insights for strategic decision-making related to real estate investments, pricing, and market trends.

**2. Pipeline Architecture**
**2.1. Diagram:**

**<img width="1465" alt="pipeline-architecture-1" src="https://github.com/GauravMalhotra2401/zillow-data-analytics/assets/171425382/d89a6a27-f34d-41fa-a68a-e573073c1266">


**2.2. Step-by-Step Explanation:**

**Step 1: Data Extraction (PythonOperator)**

Description: Extracts real estate data from the Zillow Rapid API using Python requests and stores it in a JSON file (e.g., response_data_{today's_date}.json).

Technology: PythonOperator in Airflow, utilizing the requests library for API calls.

**Step 2: Data Landing to S3 (BashOperator)**

Description: Moves the extracted JSON file from the local environment to an S3 bucket (landing zone) for secure storage and further processing.

Technology: BashOperator in Airflow, utilizing AWS CLI commands for S3 interactions.

**Step 3: Lambda Function 1: S3 to Intermediate Zone**

Description: Triggered when a new JSON file lands in the S3 landing zone. It copies the file to another S3 bucket (intermediate zone) to prevent direct modifications of the source data.

Technology: AWS Lambda function with Python code for S3 interactions.

**Step 4: Lambda Function 2: Data Cleaning, Transformation, and CSV Conversion**

Description: Triggered when a file arrives in the intermediate zone. This function performs data cleaning, transformation, converts the JSON data to a Pandas DataFrame, and finally saves it as a CSV file in a dedicated S3 bucket (cleaned-data-zone-csvbucket).

Technology: AWS Lambda function with Python code, utilizing Pandas for data manipulation and CSV writing.

**Step 5: S3KeySensor: Monitoring for CSV File Arrival**

Description: Periodically checks the cleaned-data-zone-csvbucket for the arrival of the CSV file.

Technology: S3KeySensor operator in Airflow, constantly polling the S3 bucket for new files.

**Step 6: Data Loading to Redshift (S3ToRedshiftOperator)**

Description: Once the CSV file arrives, it is loaded into a pre-defined table in a Redshift data warehouse for further analysis.

Technology: S3ToRedshiftOperator in Airflow, transferring data from S3 to Redshift.

**Step 7: Data Visualization (Quicksight)**

Description: The data in Redshift is visualized using AWS Quicksight, allowing business stakeholders to generate charts, graphs, and reports for insights and decision-making.

Technology: AWS Quicksight, connected to the Redshift cluster.

**3. Deployment Instructions**
**3.1. Prerequisites:**

AWS Account: A valid AWS account with necessary permissions for creating S3 buckets, Lambda functions, Redshift clusters, and Quicksight dashboards.

Docker: Installed on your local machine for containerizing the Airflow environment.

Python: Installed with the required libraries (e.g., requests, boto3, pandas).

Airflow: Installed and configured locally.
