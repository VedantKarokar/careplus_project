import boto3
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from datetime import date, timedelta
from botocore.exceptions import ClientError
from logging_config.log_config import setup_logging
import re
from io import BytesIO

load_dotenv()

logger = setup_logging(name = 'logs')

s3_resource = boto3.resource('s3')

def read_data(bucket, key):
    s3_object = s3_resource.Object(bucket, key)
    content = s3_object.get()['Body'].read().decode('utf-8')
    return content

def transform_data(data):
    entries = [entry.strip() for entry in data.split("---") if entry.strip()]
    # Regex pattern to extract data
    log_pattern = re.compile(
        r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(?P<log_level>[A-Za-z0-9_]+)\] '
        r'(?P<component>[^\s]+) - TicketID=(?P<ticket_id>[^\s]+) SessionID=(?P<session_id>[^\s]+)\s*'
        r'IP=(?P<ip>.*?) \| ResponseTime=(?P<response_time>-?\d+)ms \| CPU=(?P<cpu>[\d.]+)% \| EventType=(?P<event_type>.*?) \| Error=(?P<error>\w+)\s*'
        r'UserAgent="(?P<user_agent>.*?)"\s*'
        r'Message="(?P<message>.*?)"\s*'
        r'Debug="(?P<debug>.*?)"\s*'
        r'TraceID=(?P<trace_id>.*)'
    )
    parsed_entries = []
    for entry in entries:
        match = log_pattern.search(entry)
        if match:
            parsed_entries.append(match.groupdict())
    df = pd.DataFrame(parsed_entries)
    df = df.drop("trace_id", axis=1)
    df = df.astype({
    "response_time": "int",
    "cpu": "float"
    })
    df['error'] = df['error'].str.lower().map({'true': True, 'false': False})
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce').astype('datetime64[ms]')
    df = df[df.response_time>=0]
    fix_log_level = {'INF0': 'INFO', 'DEBG': 'DEBUG', 'warnING': 'WARNING', 'EROR': 'ERROR'}
    df['log_level'] = df['log_level'].replace(fix_log_level)
    df = df.drop_duplicates()
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    return buffer

def lambda_handler(event, context):
    start_date = date(2025, 6, 30)
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = event['Records'][0]['s3']['object']['key']

    for i in range(1,32):
        new_date = start_date + timedelta(days=i)
        target_key = f'{new_date}'
        data = read_data(bucket = source_bucket, key = source_key)
        transformed_data = transform_data(data=data) # Transform Data
        s3_resource.Object(
            source_bucket,
            target_key
            ).put(
            Body = transformed_data.getvalue(),
            ContentType = 'application/octet-stream'
        )
