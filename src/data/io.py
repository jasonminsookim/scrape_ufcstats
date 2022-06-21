from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

# Events.
engine = create_engine(os.getenv("POSTGRES_DB_URL"))
events_df = pd.read_csv("../data/events.csv")
events_df["event_date"] = pd.to_datetime(events_df["event_date"])
events_df["datetime_scraped"] = pd.to_datetime(events_df["datetime_scraped"])
print("Moving events data to Postgres Heroku.")
print("Events df shape:")
print(events_df.shape)
events_df.to_sql("events", engine, if_exists="replace", index=True)

print("Moving fights to Postgres Heroku.")
fights_df = pd.read_csv("../data/fights.csv")
fights_df["datetime_scraped"] = pd.to_datetime(fights_df["datetime_scraped"])
print("Fights df shape:")
print(fights_df.shape)
fights_df.to_sql("fights", engine, if_exists="replace", index=True)

