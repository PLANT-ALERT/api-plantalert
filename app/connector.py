from influxdb_client import InfluxDBClient
from sqlalchemy.ext.declarative import declarative_base
from app.enviroment import enviroment
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL

url = URL.create(
    drivername="mysql+pymysql",
    username=enviroment.DB_USERNAME,
    password=enviroment.DB_PASSWORD,
    host=enviroment.DB_HOST,
    port=enviroment.DB_PORT,
    database=enviroment.DB_DATABASE,
)

engine = create_engine(url)
session = sessionmaker(bind=engine)
Base = declarative_base()



def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()


def return_secret():
    return enviroment.SECRET

influx_client = InfluxDBClient(url=enviroment.INFLUXDB_URL, token=enviroment.INFLUXDB_TOKEN, org=enviroment.INFLUXDB_ORG)

def return_influxdb_client():
    return influx_client