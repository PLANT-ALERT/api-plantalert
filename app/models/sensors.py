from pydantic import BaseModel
from typing import  Optional

class Sensor(BaseModel):
    user_id: int
    home_id: Optional[int]
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int

class SensorLastDataResponse(BaseModel):

    humidity: int
    light: float
    soil: int
    temp: float