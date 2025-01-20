import mariadb
import sys
from dotenv import load_dotenv
import os
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT")
db_database = os.getenv("DB_DATABASE")

try:
    conn = mariadb.connect(
        user=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_database
    )

except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

def return_cursor():
    return cur

def return_secret():
    return os.getenv("SECRET")

influx_client = InfluxDBClient(url=os.getenv("INFLUXDB_URL"), token=os.getenv("INFLUXDB_TOKEN"), org=os.getenv("INFLUXDB_ORG"))

def return_influxdb_client():
    return influx_client