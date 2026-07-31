import os
import pandas as pd
from typing import Optional
from dotenv import load_dotenv
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import exc

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

#Create an engine
engine=create_engine(f"mysql+pymysql://{os.getenv("MYSQL_ROOT_USER")}:{os.getenv("MYSQL_ROOT_PASSWORD")}@{os.getenv("MYSQL_HOST")}/{os.getenv("MYSQL_DATABASE")}", pool_pre_ping=True)

#Create the table using defined data model and engine
try:
        Base.metadata.create_all(engine)
except exc.OperationalError as e:
        e.add_note("Connection Lost")
        raise

#Add data
def upload_data(batch_size, engine = engine):
                with Session(engine, autoflush=False) as session:
                        for x, frame in enumerate(pd.read_csv("data.csv", keep_default_na=False, chunksize=batch_size),start=1,):
                                session.execute(insert(Tickets), frame.to_dict(orient="records"))
                                session.commit()
                                status = print(f"Batch {x} uploaded")
                return status

try:
        upload_data(batch_size=200)
except FileNotFoundError as e:
        e.add_note("Check the data file is in your project folder.")
        raise
except exc.OperationalError as e:
        e.add_note("Connection error, rerun the code")
        raise
except exc.IntegrityError as e:
        e.add_note("Data already exists in database.")
        raise
