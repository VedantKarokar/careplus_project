import os
import pandas as pd
import logging
from dotenv import load_dotenv
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import exc
from tickets_pipeline.db.db_config import Tickets
from logging_config.log_config import setup_logging

logger = setup_logging(name = "tickets")

#Load env variables
load_dotenv()

#Create an engine
engine=create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}", pool_pre_ping=True)

#Add data
def upload_data(batch_size, engine = engine):
                with Session(engine, autoflush=False) as session:
                        with session.begin():
                                for x, frame in enumerate(pd.read_csv("src/tickets_pipeline/data.csv", keep_default_na=False, chunksize=batch_size),start=1,):
                                        session.execute(insert(Tickets), frame.to_dict(orient="records"))
                                session.commit()
                                print("Upload Successfull!")

try:
        upload_data(batch_size=200)
        logger.debug("Data was uploaded successfully")

except FileNotFoundError as e:
        print("Check the data file is in your project folder.")
        logger.error("File not found error occurred")
        
except exc.OperationalError as e:
        print("Connection error, rerun the code.")
        logger.error("Connection error occurred")

except exc.IntegrityError as e:
        print("Data already exists in database.")
        logger.error("Data was added in an already populated database")
