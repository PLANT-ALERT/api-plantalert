from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter
from app.models.user import User
from app.schema.users import UserResponse
# tohle potrevuje kazda route
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.connector import get_db

router = APIRouter()

@router.get("")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).where(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(username=str(user.username), email=str(user.email), image=str(user.image), created_at=str(user.created_at))