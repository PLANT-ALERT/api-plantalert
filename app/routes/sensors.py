from fastapi.params import Depends
from app.connector import get_db
from sqlalchemy.exc import IntegrityError
from app.depedencies import pwd_context, influx_client
from fastapi import HTTPException, Query
from typing import Optional
from app.schema.flower import FlowerResponse, MinMax
from app.schema.sensors import Sensor, SensorLastDataResponse, FlowerChange
from app.models.sensor import Sensor as SensorModel
from app.models.flower import Flower as FlowerModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

query_api = influx_client.query_api()

@router.get("/last_data/{mac_address}", description="returns last available data", response_model=SensorLastDataResponse)
async def get_last_sensor_data(mac_address: str):

    query = f"""
    from(bucket: "db")
        |> range(start: -1y) // Adjust the range as needed
        |> filter(fn: (r) => r["topic"] == "/sensors/{mac_address}")
        |> group(columns: ["_field"]) // Group by field to isolate each one
        |> last() // Get the last value for each group (field)
    """
    # Execute query and fetch results
    tables = query_api.query(query)

    result = {}

    # Parse the results
    for table in tables:
        for record in table.records:
            result.update({
                record.get_field(): record.get_value()
            })

    return result

@router.get("/last_data/humidity/{mac_address}", description="returns only last known humidity", response_model=int)
async def get_last_sensor_data_humidity(mac_address: str):
    query = f"""
    from(bucket: "db")
        |> range(start: -1y) // Adjust the range as needed
        |> filter(fn: (r) => r["topic"] == "/sensors/{mac_address}")
        |> filter(fn: (r) => r["_field"] == "humidity")
        |> group(columns: ["_field"]) // Group by field to isolate each one
        |> last() // Get the last value for each group (field)
    """
    # Execute query and fetch results
    tables = query_api.query(query)

    result: int = -1

    # Parse the results
    for table in tables:
        for record in table.records:
            result = record.get_value()


    return result


@router.post("")
async def create_sensor(sensor: Sensor, db: Session = Depends(get_db)):
    if db.query(SensorModel).filter(SensorModel.mac_address == sensor.mac_address).first():
        raise HTTPException(status_code=401, detail="MAC address already exists.")

    new_sensor = SensorModel(
        user_id=sensor.user_id,
        mac_address=sensor.mac_address,
        name=sensor.name,
    )

    try:
        db.add(new_sensor)
        db.commit()
        db.refresh(new_sensor)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.put("/flower")
async def set_flower(sensor: FlowerChange, db: Session = Depends(get_db)):
    if sensor.flower_id is not None and db.query(FlowerModel).filter(FlowerModel.id == sensor.flower_id).count() <= 0:
        raise HTTPException(status_code=404, detail="Flower not found")
    flower = db.query(SensorModel).filter(SensorModel.id == sensor.sensor_id).first()
    flower.flower_id = sensor.flower_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/flower")
async def get_flower_by_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = db.query(SensorModel).filter(SensorModel.id == sensor_id).first()

    if sensor is None:
        raise HTTPException(status_code=404, detail="Sensor not found")

    flower = db.query(FlowerModel).filter(FlowerModel.id == sensor.flower_id).first()

    response = FlowerResponse(
            user_id=None,
            id=int(flower.id),
            name=str(flower.name),
            light=int(flower.light),
            image=str(flower.image),
            air_temperature=MinMax(min=float(flower.min_air_temperature), max=float(flower.max_air_temperature)),
            soil_humidity=MinMax(min=float(flower.min_soil_humidity), max=float(flower.max_soil_humidity)),
            air_humidity=MinMax(min=float(flower.min_air_humidity), max=float(flower.max_air_humidity)),
        )

    return response



@router.get("")
async def get_sensors(
    user_id: Optional[int] = Query(None),
    home_id: Optional[int] = Query(None),
    mac_address: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(SensorModel)

    if user_id is not None:
        query = query.filter(SensorModel.user_id == user_id)
    elif home_id is not None:
        query = query.filter(SensorModel.home_id == home_id)
    elif mac_address is not None:
        query = query.filter(SensorModel.mac_address == mac_address)

    sensors = query.all()

    return sensors

@router.delete("/{mac_address}", response_model=dict)
async def delete_sensor(mac_address: str, db: Session = Depends(get_db)):
    # Find the sensor
    sensor = db.query(SensorModel).filter(SensorModel.mac_address == mac_address).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found.")

    # Delete the sensor
    db.delete(sensor)
    db.commit()

    return {"detail": "Sensor deleted successfully."}

@router.get("/am_i_registred/{mac_address}", status_code=200, response_model=str, description="Checks if sensors macadd is in database, used for factory reseting sensor if not present in db")
async def am_i_registred(mac_address: str, db: Session = Depends(get_db)):
    if len(mac_address) == 12:
        mac_address = ":".join(mac_address[i:i + 2] for i in range(0, 12, 2))

    sensor = db.query(SensorModel).filter(SensorModel.mac_address == mac_address).first()

    if sensor:
        return "ok"

    if not sensor:
        raise HTTPException(status_code=204, detail="Sensor not found.")