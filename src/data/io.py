import pandas as pd
from prefect import task
import glob
import prefect
import psycopg2
import yaml


@task()
def connect_postgres():
    """ Connect to the PostgreSQL database server """

    # Gets the logger for prefect.
    logger = prefect.context.get("logger")

    # Loads the config file.
    with open("config.yml") as f:
        yaml_config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Config file loaded successfully.")

    params_dict = {
        "host": "localhost",
        "database": "fightdata",
        "user": yaml_config["db_creds"]["username"],
        "password": yaml_config["db_creds"]["password"],
    }

    # Attempts to connect to the database server.
    conn = None
    try:
        # connect to the PostgreSQL server
        logger.info(f'Connecting to the PostgreSQL database {params_dict["database"]} ...')
        conn = psycopg2.connect(**params_dict)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.warning(error)

    logger.info("Connection to db successful.")
    return conn


@task()
def get_filenames(path, extension):
    """"Extracts the dates for all the files that match the extension in a given directory path."""
    result = glob.glob(path + f"*.{extension}")
    return result


@task()
def arr_to_series(arr):
    """Converts an array into a pd Series."""
    return pd.Series(arr)


@task()
def get_string_date(csv_file_names_arr):
    return csv_file_names_arr.apply(
        lambda x: x.split("event_urls_")[1].split(".csv")[0]
    )


@task()
def get_max_date(string_dates_arr):
    logger = prefect.context.get("logger")
    dates_arr = pd.to_datetime(string_dates_arr)
    max_date = dates_arr.max()
    logger.info(f"The most recent date for events scraping is: {max_date}")
    return max_date
