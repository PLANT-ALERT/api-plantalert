from pydantic import BaseModel
from typing import Optional

from datetime import datetime

class SensorCreate(BaseModel):
    user_id: int
    home_id: Optional[int]
    name: str
    description: Optional[str]
    mac_address: str
    location: Optional[str]
    age: Optional[int]
    flower_id: Optional[int]

class SensorGet(BaseModel):
    id: int
    description: Optional[str]
    created_at: datetime
    user_id: int
    name: str
    mac_address: str
    age: Optional[int]
    flower_id: Optional[int]
    home_id: Optional[int]

class SensorLastDataResponse(BaseModel):
    time: datetime
    humidity: Optional[int]
    light: Optional[float]
    soil: Optional[int]
    temp: Optional[float]

class FlowerChange(BaseModel):
    sensor_id: int
    flower_id: Optional[int]