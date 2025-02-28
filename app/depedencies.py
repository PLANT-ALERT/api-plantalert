from app.connector import return_influxdb_client
from passlib.context import CryptContext

influx_client = return_influxdb_client()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
