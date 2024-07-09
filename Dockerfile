# Dockerfile for extending the official Airflow image to include AWS CLI

# Start from the official Airflow image
FROM apache/airflow:2.9.2

# Switch to root user to install additional packages
USER root

# Install AWS CLI using pip
RUN pip3 install awscli

# Install the Apache Airflow provider for Amazon AWS
RUN pip3 install --upgrade apache-airflow-providers-amazon

ENV AWS_ACCESS_KEY_ID="mention_your_access_key"
ENV AWS_SECRET_ACCESS_KEY="mention_your_access_key"
ENV AWS_DEFAULT_REGION="mention_your_aws_region"

# Switch back to the airflow user
USER airflow
