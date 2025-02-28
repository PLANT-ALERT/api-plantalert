from pydantic import BaseModel
from typing import Optional

class MinMax(BaseModel):
    min: float
    max: float

class FlowerCreate(BaseModel):
    user_id: Optional[int]
    name: str
    image: Optional[str]
    light: Optional[int]
    soil_humidity: Optional[MinMax]
    air_humidity: Optional[MinMax]
    air_temperature: Optional[MinMax]


class FlowerResponse(BaseModel):
    name: str
    image: Optional[str]
    light: Optional[int]
    soil_humidity: Optional[MinMax]
    air_humidity: Optional[MinMax]
    air_temperature: Optional[MinMax]
