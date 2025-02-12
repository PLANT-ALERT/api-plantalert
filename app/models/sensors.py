from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SensorDataResponse(BaseModel):
    time: str
    field_name: str
    field_value: float


class Sensor(BaseModel):
    user_id: int  # Association with a user
    home_id: Optional[int]  # Association with a user
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int

class Sensor_Response(BaseModel):
    home_id: Optional[int]  # Association with a user
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int
    created_at: datetime
