import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from io import BytesIO
from datetime import date, timedelta
from logging_config.log_config import setup_logging

logger = setup_logging(name = "logs")

logger.info("Bronze layer ingestion started for logs_pipeline")

load_dotenv()

aws_bucket="careplusstorage"
aws_prefix="support_logs/raw/"

def s3_upload(bucket, key, body):
    s3 = boto3.client(
        service_name = 's3'
        )
    s3.put_object(
        Bucket = bucket,
        Key = key,
        Body = body
        )

def began_ingestion():
    start_date = date(2025, 6, 30)
    for i in range(1,32):
        # Buffer for AWS
        csv_buffer = BytesIO()

        new_date = start_date + timedelta(days = i)

        filepath = f"src/logs_pipeline/data/support_logs_{new_date}.log"

        with open(filepath, mode = 'r', encoding = 'utf-8') as f:
            content = f.read()
            csv_buffer.write(content.encode("utf-8")) 
            # log file's content is written to the buffer and converted from str to bytes

        s3_upload(
            bucket = aws_bucket,
            key = f"{aws_prefix}{new_date}",
            body = csv_buffer.getvalue()
            )
        print(f"File {new_date} ingested.")

try:
    began_ingestion()
    logger.info("Files Successfully Ingested.")

except boto3.exceptions.ClientError:
    logger.exception("Failed to upload to S3")
