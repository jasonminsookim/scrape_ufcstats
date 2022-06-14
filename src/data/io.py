from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

engine = create_engine(os.getenv("POSTGRES_DB_URL"))
events_df = pd.read_csv("../data/events.csv")
events_df["event_date"] = pd.to_datetime(events_df["event_date"])
events_df["datetime_scraped"] = pd.to_datetime(events_df["datetime_scraped"])
print("Events df shape:")
print(events_df.shape)
events_df.to_sql("events", engine, if_exists="replace", index=False)
