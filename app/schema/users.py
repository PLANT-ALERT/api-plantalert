from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional

class TokenResponse(BaseModel):
    user_id: int

class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    home_id: Optional[int] = None
    image: Optional[str] = None
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    image: str
    created_at: datetime