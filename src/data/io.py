import os
import pandas as pd
from sqlalchemy import create_engine
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", key="ts"),
        structlog.processors.KeyValueRenderer(
            key_order=["event", "table", "record_count"]
        ),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


def get_db_engine():
    """Create and return a SQLAlchemy engine using the database URL from the environment variables."""
    db_url = os.getenv("POSTGRES_DB_URL")
    if not db_url:
        logger.error("Database URL not set")
        raise ValueError("POSTGRES_DB_URL is not set in the .env file.")
    logger.info("Database engine created", db_url=db_url)
    return create_engine(db_url)


def read_csv_data(file_path):
    """Read and return data from a CSV file, converting appropriate columns to datetime."""
    df = pd.read_csv(file_path)
    for col in df.columns:
        if "date" in col or "datetime" in col:
            df[col] = pd.to_datetime(df[col])
    return df


def load_data_to_database(df, table_name, engine):
    """Load the DataFrame into the specified PostgreSQL table."""
    logger.info("Loading data into database", table=table_name, record_count=len(df))
    df.to_sql(table_name, con=engine, if_exists="replace", index=False)


def main():
    """Main function to manage the workflow of reading, processing, and uploading data."""
    engine = get_db_engine()

    # Paths relative to `src` directory
    events_path = "data/events.csv"
    fights_path = "data/fights.csv"

    # Process and load events
    events_data = read_csv_data(events_path)
    load_data_to_database(events_data, "events", engine)

    # Process and load fights
    fights_data = read_csv_data(fights_path)
    load_data_to_database(fights_data, "fights", engine)


if __name__ == "__main__":
    main()
