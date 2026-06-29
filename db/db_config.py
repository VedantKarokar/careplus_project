import sqlalchemy as sq
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

class Configure_DB:
        def __init__(self):
                self.engine = sq.create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DATABASE")}")
                pass

        def create_table(self, query : str):
                with self.engine.connect() as conn:
                        conn.execute(query)
                        conn.commit()

        def insert_data(file : str):
                with open(file, "r") as f:
                        data = f.read()
                return data

        








