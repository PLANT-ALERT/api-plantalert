from app.depedencies import pwd_context, influx_client
from fastapi import APIRouter

router = APIRouter()

query_api = influx_client.query_api()