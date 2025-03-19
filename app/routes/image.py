from fastapi import HTTPException
import uuid
from fastapi import APIRouter
from botocore.exceptions import NoCredentialsError
from fastapi import FastAPI, File, UploadFile, HTTPException
from app.depedencies import s3_client
from app.enviroment import enviroment
import os

from app.schema.image import UploadResponseImage

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}

@router.post("/upload/", response_model=UploadResponseImage)
async def upload_image(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .jpg and .png images are allowed")

    new_filename = f"{uuid.uuid4()}{ext}"

    try:
        s3_client.upload_fileobj(file.file, enviroment.R2_BUCKET_NAME, new_filename, ExtraArgs={"ContentType": "image/jpeg"})
        file_url = f"{enviroment.AWS_CUSTOM_DOMAIN}/{enviroment.R2_BUCKET_NAME}/{new_filename}"
        return UploadResponseImage(file_url=file_url)
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Invalid Cloudflare R2 credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))