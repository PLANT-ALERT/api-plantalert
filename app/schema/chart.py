from pydantic import BaseModel
from typing import Optional

class extraData(BaseModel):
    formattedValue: Optional[str]
    formattedTime: Optional[str]

class ChartResponse(BaseModel):
    x: Optional[str]
    y: Optional[float]
    extraData: Optional[extraData]