import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from io import StringIO
from sqlalchemy import create_engine
from boto3.s3.transfer import TransferConfig
from datetime import datetime
import logging

logging.basicConfig(
        filename="ingestion.log",
        level=logging.ERROR,
        format = "%(asctime)s - %(levelname)s - %(message)s",
)
load_dotenv()

aws_bucket="careplusstorage"
aws_prefix="support_tickets/raw/"

engine = create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}",echo = True)

def s3_upload(df, bucket, key):
    # Buffer for AWS
    csv_buffer=StringIO()
    df.to_csv(
        csv_buffer,
        index=False
        )
    s3=boto3.client(
        service_name='s3'
        )
    boto3.s3.transfer.TransferConfig(
        multipart_chunksize=2
        )
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=csv_buffer.getvalue()
        )

def began_ingestion():
    # Query data
    query = f"""
        SELECT * FROM Tickets;
        """
    df = pd.read_sql(sql=query, con=engine)
    if df.empty:
        print(f"No data found, skipping upload.")
    # upload to s3
    timestamp = datetime.utcnow().strftime("%d%m%Y%H%M%S")
    s3_key = f"{aws_prefix}{timestamp}.csv"
    return s3_upload(df, aws_bucket, s3_key)

# Run
# This block ONLY runs when you do: python bronze.py
if __name__ == "__main__":
    began_ingestion()