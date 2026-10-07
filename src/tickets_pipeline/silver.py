# lambda function
import boto3
import numpy as np
import pandas as pd
import pyarrow      # added to get the output data in parquet
from io import StringIO
from dotenv import load_dotenv
from logging_config.log_config import setup_logging

logger = setup_logging(name = "tickets")

load_dotenv()

s3_resource = boto3.resource('s3')

def transform_data(data):
    # Transformation
    csv_buffer = StringIO(data)
    df = pd.read_csv(csv_buffer)
    df = df.drop(columns = "agent_feedback")
    df["resolved_at"] = df["resolved_at"].replace(to_replace = '', value = np.nan)
    df["num_interactions"] = df["num_interactions"].replace(to_replace = -999999, value = np.nan)
    df["priority"] = df["priority"].replace({"Lw":"Low","Medum":"Medium","Hgh":"High"})
    df = df.to_parquet()
    return df

def read_data(bucket, key):
    # Read data from S3
    s3_object = s3_resource.Object(bucket, key)
    content = s3_object.get()['Body'].read().decode('utf-8')
    return content

def lambda_handler(event, context):
    # Extract bucket name and object key
    source_key = event["Records"][0]["object"]["key"]
    source_bucket = event["Records"][0]["bucket"]["name"]
    target_key = "support_tickets/processed/tickets.parquet"

    # Access data from S3
    raw_content = read_data(bucket = source_bucket, key = source_key)

    # Transform data
    transformed_data = transform_data(data = raw_content)

    # Ingest again
    s3_resource.Object(source_bucket, target_key).put(
        Body = transformed_data,
        ContentType = 'application/octet-stream'
    )
