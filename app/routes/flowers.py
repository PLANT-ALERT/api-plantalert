from app.depedencies import influx_client
from app.connector import get_db
from fastapi import HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter
from typing import List, Optional, Union
from app.models.flower import Flower
from app.schema.flower import FlowerSortedResponse, FlowerResponse

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

@router.get("", response_model=FlowerSortedResponse)
async def return_flowers(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    user_flowers = []
    default_flowers = []
    other_flowers = []

    if user_id is not None:
        user_flowers = db.query(Flower).filter(Flower.user_id == user_id).all()
        other_flowers = db.query(Flower).filter(Flower.user_id != user_id).filter(Flower.user_id != None).all()
    else:
        other_flowers = db.query(Flower).filter(Flower.user_id != None).all()

    default_flowers = db.query(Flower).filter((Flower.user_id == 0) | (Flower.user_id == None)).all()

    def serialize(flowers: List[Flower]) -> Optional[List[FlowerResponse]]:
        if not flowers:
            return None
        return [
            FlowerResponse(
                user_id=flower.user_id,
                id=flower.id,
                name=flower.name,
                light=flower.light,
                image=flower.image,
                air_temperature=MinMax(min=flower.min_air_temperature, max=flower.max_air_temperature),
                soil_humidity=MinMax(min=flower.min_soil_humidity, max=flower.max_soil_humidity),
                air_humidity=MinMax(min=flower.min_air_humidity, max=flower.max_air_humidity),
            )
            for flower in flowers
        ]

    return FlowerSortedResponse(
        user_flowers=serialize(user_flowers),
        default_flowers=serialize(default_flowers),
        other_flowers=serialize(other_flowers),
    )


@router.get("/{flower_id}", response_model=FlowerResponse)
async def return_flower(flower_id: int, db: Session = Depends(get_db)):
    flower = db.query(Flower).filter(Flower.id == flower_id).first()

    return FlowerResponse(
        id=flower.id,
        name=flower.name,
        light=flower.light,
        image=flower.image,
        air_temperature=MinMax(min=flower.min_air_temperature, max=flower.max_air_temperature),
        soil_humidity=MinMax(min=flower.min_soil_humidity, max=flower.max_soil_humidity),
        air_humidity=MinMax(min=flower.min_air_humidity, max=flower.max_air_humidity),
    )

