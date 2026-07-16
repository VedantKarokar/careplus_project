import os
import pandas as pd
import numpy as np
import logging
from time import sleep
from io import StringIO
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

logging.basicConfig(
        filename="db/db.log",
        level=logging.DEBUG,
        format = "%(asctime)s - %(levelname)s - %(message)s",
)
#Load env variables
load_dotenv()

#Define a Model
class Base(DeclarativeBase):
        pass

class Tickets(Base):
        __tablename__ = "Tickets"

        ticket_id : Mapped[Optional[str]] = mapped_column(String(20),primary_key=True)

        created_at : Mapped[Optional[str]] = mapped_column(String(20))

        resolved_at : Mapped[Optional[str]] = mapped_column(String(20))

        agent : Mapped[Optional[str]] = mapped_column(String(30))

        priority : Mapped[Optional[str]] = mapped_column(String(10))

        num_interactions : Mapped[Optional[str]] = mapped_column(String(10))

        IssueCat : Mapped[Optional[str]] = mapped_column(String(50))

        channel : Mapped[Optional[str]] = mapped_column(String(10))

        status : Mapped[Optional[str]] = mapped_column(String(10))

        agent_feedback : Mapped[Optional[str]] = mapped_column(String(10))

        def __repr__(self):
                return f"Tickets(ticket_id={self.ticket_id!r}, created_at={self.created_at!r}, resolved_at={self.resolved_at!r}), agent={self.agent!r}, priority={self.priority!r}, num_interactions={self.num_interactions!r}, IssueCat={self.IssueCat!r}, channel={self.channel!r}, status={self.status!r}, agent_feedback={self.agent_feedback}"

print("*")
sleep(1)
print("*")
sleep(1)
print("*")
sleep(2)

#Create an engine        
engine=create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DATABASE")}", echo=True)

#Create the table using defined data model and engine
Base.metadata.create_all(engine)

print("*")
sleep(1)
print("*")
sleep(1)
print("*")
sleep(2)

#Add data
BATCH_SIZE = 200
with Session(engine, autoflush=False) as session:
        with open("data.csv", "r") as f:
                data = f.read()
                data = StringIO(data)
                df = pd.read_csv(data, keep_default_na=False)
                data = df.to_dict(orient="records")
                for i in range(0, len(data), BATCH_SIZE):
                        batch = data[i : i + BATCH_SIZE]
                        session.execute(insert(Tickets), batch)
                        print("*")
                        sleep(1)
                        print("*")
                        sleep(1)
                        print("*")
                        sleep(2)
                        session.commit()
print("-------------------------------------------------------")