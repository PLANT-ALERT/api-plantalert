from pydantic import BaseModel
from typing import Optional


class UploadResponseImage(BaseModel):
    file_url: str

