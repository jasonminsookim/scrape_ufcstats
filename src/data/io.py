import pandas as pd
from prefect import task
import prefect
import yaml
from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy import exc


# Loads the config file.
with open("config.yml") as f:
    yaml_config = yaml.load(f, Loader=yaml.FullLoader)

DATABASE = {
    "drivername": "postgresql",
    "host": "localhost",
    "database": "fightdata",
    "username": yaml_config["db_creds"]["username"],
    "password": yaml_config["db_creds"]["password"],
}


@task
def connect_postgres():
    """ Connect to the PostgreSQL database server """

    # Gets the logger for prefect.
    logger = prefect.context.get("logger")

    # Attempts to connect to the database server.
    engine = None
    try:
        # connect to the PostgreSQL server
        logger.info(f'Connecting to the PostgreSQL database {DATABASE["database"]} ...')
        engine = create_engine(url.URL(**DATABASE))
    except (Exception, exc.SQLAlchemyError) as error:
        logger.warning(error)

    logger.info("Connection to db successful.")
    return engine


@task
def read_csv(path):
    return pd.read_csv(path)


@task
def df_to_table(df, engine, table_name):
    # Gets the logger for prefect.
    logger = prefect.context.get("logger")

    try:
        logger.info(f"Moving df to postgres {table_name} table ...")
        df.to_sql(table_name, con=engine)
    except (Exception, exc.SQLAlchemyError) as error:
        logger.warning(error)
