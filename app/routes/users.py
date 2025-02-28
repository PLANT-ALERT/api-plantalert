from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter
from app.models.user import User
# tohle potrevuje kazda route
from fastapi.params import Depends
from sqlalchemy.orm import Session
from app.connector import get_db

router = APIRouter()

@router.get("")
async def get_users(db: Session = Depends(get_db)):

    users = db.query(User).all()
    users_json = [
        {
            "home_id": user[0],
            "id": user[1],
            "username": user[2],
            "email": user[3],
            "image": user[4],
            "created_at": user[5],
        }
        for user in users
    ]
    return jsonable_encoder(users_json)

@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).where(User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_json = {
        "username": user[0],
        "email": user[1],
        "image": user[2],
        "created_at": user[3],
    }

    return jsonable_encoder(user_json)