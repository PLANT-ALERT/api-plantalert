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
    id: int
    name: str
    user_id: Optional[int] = None
    image: Optional[str] = None
    light: Optional[int] = None
    soil_humidity: Optional[MinMax] = None
    air_humidity: Optional[MinMax] = None
    air_temperature: Optional[MinMax] = None


class FlowerSortedResponse(BaseModel):
    user_flowers: Optional[List[FlowerResponse]]
    default_flowers: Optional[List[FlowerResponse]]
    other_flowers: Optional[List[FlowerResponse]]