import sqlalchemy as sq
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() #load env variables

class Configure_DB:
        def __init__(self):
                self.engine=sq.create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DATABASE")}")
                pass

        def query_db(self, query : str):
                with self.engine.connect() as conn:
                        conn.execute(query)
                        conn.commit()

        def get_data(file_name : str):
                with open(file_name, "r") as f:
                        data = f.read()
                return data

table_query=f"CREATE TABLE IF NOT EXIST `support_tickets`("\
                "`ticket_id` text,"\
                "`created_at` text,"\
                "`resolved_at` text,"\
                "`agent` text,"\
                "`priority` text,"\
                "`num_interactions` text,"\
                "`IssUeCat` text,"\
                "`channel` text,"\
                "`status` text,"\
                "`agent_feedback` text"\
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;)"

create_table=Configure_DB.query_db(query=table_query)

data_query=f"INSERT INTO `support_tickets` VALUES ({Configure_DB.get_data("data.csv")})"

add_data=Configure_DB.query_db(query=data_query)


