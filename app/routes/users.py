from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from app.depedencies import cursor, pwd_context
from app.models.users import User, TokenResponse, LoginRequest
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_users():
    cursor.execute("SELECT home_id, id, username, email, image, created_at FROM users")
    users = cursor.fetchall()  # Vrací seznam tuple
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
async def get_user(user_id: int):
    cursor.execute("SELECT username, email, image, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_json = {
        "username": user[0],
        "email": user[1],
        "image": user[2],
        "created_at": user[3],
    }

    return jsonable_encoder(user_json)