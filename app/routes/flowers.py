from app.depedencies import influx_client
from app.connector import get_db
from fastapi import HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter
from typing import List
from app.models.flower import Flower

router = APIRouter()

query_api = influx_client.query_api()

from app.schema.flower import FlowerCreate, FlowerResponse, MinMax

@router.post("")
async def create_flower(flower: FlowerCreate, db: Session = Depends(get_db)):
    if db.query(Flower).filter(Flower.name == flower.name).count():
        raise HTTPException(status_code=202, detail="Flower already exists")

    new_flower = Flower(
        name=flower.name,
        user_id=flower.user_id,
        image=flower.image,
        light=flower.light,
        max_air_humidity=int(flower.air_humidity.max),
        min_air_humidity=int(flower.air_humidity.min),
        max_soil_humidity=int(flower.soil_humidity.max),
        min_soil_humidity=int(flower.soil_humidity.min),
        max_air_temperature=float(flower.air_temperature.max),
        min_air_temperature=float(flower.air_temperature.min),
    )

    try:
        db.add(new_flower)
        db.commit()
        db.refresh(new_flower)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.post("/bulk")
async def create_flower_bulk(flowers: List[FlowerCreate], db: Session = Depends(get_db)):
    for flower in flowers:
        new_flower = Flower(
            name=flower.name,
            user_id=flower.user_id,
            image=flower.image,
            light=flower.light,
            max_air_humidity=int(flower.air_humidity.max),
            min_air_humidity=int(flower.air_humidity.min),
            max_soil_humidity=int(flower.soil_humidity.max),
            min_soil_humidity=int(flower.soil_humidity.min),
            max_air_temperature=float(flower.air_temperature.max),
            min_air_temperature=float(flower.air_temperature.min),
        )

        try:
            db.add(new_flower)
            db.commit()
            db.refresh(new_flower)
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=500, detail="Database error")

@router.get("", response_model=List[FlowerResponse])
async def return_flower(db: Session = Depends(get_db)):
    response = db.query(Flower).all()

    flower_response = [
        FlowerResponse(
            name=str(flower.name),
            light=str(flower.light),
            image=str(flower.image),
            air_temperature=MinMax(min=float(flower.min_air_temperature), max=float(flower.max_air_temperature)),
            soil_humidity=MinMax(min=float(flower.min_soil_humidity), max=float(flower.max_soil_humidity)),
            air_humidity=MinMax(min=float(flower.min_air_humidity), max=float(flower.max_air_humidity)),
        )
        for flower in response
    ]
    return flower_response