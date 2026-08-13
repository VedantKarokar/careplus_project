import os
import logging
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import exc
from src.Tickets.db.db_config import Tickets

logger = logging.getLogger(__name__)

#Load env variables
load_dotenv()

#Create an engine
engine=create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}:{os.getenv("MYSQL_PORT")}/{os.getenv("MYSQL_DATABASE")}", pool_pre_ping=True)

#Add data
def upload_data(batch_size, engine = engine):
                with Session(engine, autoflush=False) as session:
                        with session.begin():
                                for x, frame in enumerate(pd.read_csv("Tickets/data.csv", keep_default_na=False, chunksize=batch_size),start=1,):
                                        session.execute(insert(Tickets), frame.to_dict(orient="records"))
                                session.commit()
                                print("Upload Successfull!")

try:
        upload_data(batch_size=200)
        logger.info("Data was uploaded successfully")
except FileNotFoundError as e:
        e.add_note("Check the data file is in your project folder.")
        logger.error("File not found error occurred")
        raise
except exc.OperationalError as e:
        e.add_note("Connection error, rerun the code.")
        logger.error("Connection error occurred")
        raise
except exc.IntegrityError as e:
        e.add_note("Data already exists in database.")
        logger.error("Data was added in an already populated database")
        raise
