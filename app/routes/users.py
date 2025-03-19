from fastapi import HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter
from app.models.user import User
from app.schema.users import UserResponse, UserUpdate
# tohle potrevuje kazda route
from fastapi.params import Depends, File
from sqlalchemy.orm import Session
from app.connector import get_db
from app.routes.image import upload_image

router = APIRouter()

@router.get("")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.put("/update_user_image")
async def update_user_image(user_id: int,file: UploadFile = File(...),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    image_response = await upload_image(file)

    if not image_response:
        raise HTTPException(status_code=404, detail="Image not found")

    user.image = image_response.file_url

    db.commit()
    db.refresh(user)



@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).where(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(username=str(user.username), email=str(user.email), image=str(user.image), created_at=str(user.created_at))


@router.put("/{user_id}")
async def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user attributes dynamically
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
