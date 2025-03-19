from app.connector import return_influxdb_client
from passlib.context import CryptContext
from app.enviroment import enviroment
import boto3

influx_client = return_influxdb_client()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

s3_client = boto3.client(
    "s3",
    endpoint_url=enviroment.R2_ENDPOINT_URL,
    aws_access_key_id=enviroment.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=enviroment.AWS_SECRET_ACCESS_KEY
)