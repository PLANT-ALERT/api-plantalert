from pydantic import BaseModel
from typing import Optional, List


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
    user_id: Optional[int]
    id: int
    name: str
    image: Optional[str]
    light: Optional[int]
    soil_humidity: Optional[MinMax]
    air_humidity: Optional[MinMax]
    air_temperature: Optional[MinMax]


class FlowerSortedResponse(BaseModel):
    user_flowers: Optional[List[FlowerResponse]]
    default_flowers: Optional[List[FlowerResponse]]
    other_flowers: Optional[List[FlowerResponse]]