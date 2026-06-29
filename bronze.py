import os
import pandas as pd
import boto3
from dotenv import load_dotenv
from io import StringIO
from sqlalchemy import create_engine
from datetime import datetime, timedelta

load_dotenv()

# -------------CONFIGURATION-------------

aws_bucket="careplusstorage"
aws_prefix="support-tickets/raw/"
date_file="date_tracker.txt"

aws_config={
    "secret_key" : os.getenv("AWS_secret_key"),
    "access_key" : os.getenv("AWS_access_key"),
    "region" : os.getenv("AWS_region")
}

# -------------UTILITY FUNCTIONS-------------

def get_engine():
    return create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}")

def upload_to_s3(df, bucket, key):
    # Buffer for AWS
    csv_buffer=StringIO()
    df.to_csv(csv_buffer, index=False)
    s3=boto3.client('s3', config=aws_config)
    s3.put_object(
        bucket=bucket,
        key=key,
        body=csv_buffer.getvalue()
    )

def read_last_date(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
    #return "2025-06-30"  Starting point before 1st July

def update_last_date(file_path, new_date):
    with open(file_path, 'w') as f:
        f.write(new_date)

def get_next_date(last_date_str):
    last_date=datetime.strptime(last_date_str, "%Y-%m-%d")
    next_date=last_date + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")

# -------------MAIN INGESTION LOGIC-------------

def began_ingestion():
    engine=get_engine()
    last_date=read_last_date(file_path=date_file)
    next_date=get_next_date(last_date_str=last_date)

    # Query only specific day’s data
    query = f"""
        SELECT * FROM support_tickets:
        WHERE DATE(created_at) = '{next_date}'
    """
    df = pd.read_sql(sql=query, con=engine)
    if df.empty:
        print(f"No data found for {next_date}. Skipping upload.")
        return
    else:
        print(df.shape)
        print(df.head())

    # upload to s3
    s3_key = f"{aws_prefix}support_tickets_{next_date}.csv"
    upload_to_s3(df, aws_bucket, s3_key)

    # Update date tracker
    update_last_date(date_file, next_date)
    print(f"Updated tracker to {next_date}")

# Run
# This block ONLY runs when you do: python bronze.py
if __name__ == "__main__":
    began_ingestion()