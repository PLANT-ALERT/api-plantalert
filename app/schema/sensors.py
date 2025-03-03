from pydantic import BaseModel
from typing import  Optional

class Sensor(BaseModel):
    user_id: int
    home_id: Optional[int]
    name: str
    description: Optional[str]
    mac_address: str
    location: Optional[str]
    age: Optional[int]
    flower_id: Optional[int]

class SensorLastDataResponse(BaseModel):
    humidity: int
    light: float
    soil: int
    temp: float

class FlowerChange(BaseModel):
    sensor_id: int
    flower_id: Optional[int]