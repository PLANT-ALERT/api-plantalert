from fastapi import HTTPException

from app.depedencies import influx_client
from fastapi import APIRouter
from app.enviroment import enviroment
import requests
router = APIRouter()

query_api = influx_client.query_api()

NOTIFY_URL = "https://app.nativenotify.com/api/indie/notification"
BULK_URL = "https://app.nativenotify.com/api/notification"

def call_notify_api(user_id: int, title: str, message: str):
    try:
        response = requests.post(NOTIFY_URL, json={"subID": user_id, "appId": enviroment.NATIVENOTIFY_FIRST, "appToken": enviroment.NATIVENOTIFY_SECOND, "title": title, "message": message})
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error posting soil data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def call_notify_api_bulk(title: str, message: str):
    try:
        response = requests.post(BULK_URL, json={"appId": enviroment.NATIVENOTIFY_FIRST, "appToken": enviroment.NATIVENOTIFY_SECOND, "title": title, "body": message})
        if response.status_code == 201:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error posting soil data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/soil")
def notification_soil(user_id: str):
    return call_notify_api(user_id=int(user_id), title="Please water me", message="Your plant isnt watered enough, please take your time to water")

@router.get("/bulk")
def notification_bulk(title: str, message: str):
    return call_notify_api_bulk(title=title, message=message)
