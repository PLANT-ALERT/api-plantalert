from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.depedencies import pwd_context
from app.schema.users import User, TokenResponse, LoginRequest
from app.models.user import User as UserModel
from fastapi import APIRouter
from app.connector import get_db

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def create_user(user: User, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.username == user.username).first():
        raise HTTPException(status_code=401, detail="User already exists")

    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(status_code=402, detail="Email already used")

    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Create a new user
    new_user = UserModel(
        home_id=user.home_id,
        username=user.username,
        email=user.email,
        password=hashed_password,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    return {"user_id": new_user.id}

@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    # Fetch user by username
    user = db.query(UserModel).filter(UserModel.username == login_request.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Username not found")

    # Verify password
    if not pwd_context.verify(login_request.password, user.password):
        raise HTTPException(status_code=402, detail="Password not found")

    return TokenResponse(
        user_id=int(user.id)
    )

