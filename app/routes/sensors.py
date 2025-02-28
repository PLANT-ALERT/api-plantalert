from fastapi.params import Depends
from app.connector import get_db
from sqlalchemy.exc import IntegrityError
from app.depedencies import pwd_context, influx_client
from fastapi import HTTPException, Query
from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.schema.sensors import Sensor, SensorLastDataResponse
from app.models.sensor import Sensor as SensorModel
from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()

query_api = influx_client.query_api()

# @router.get("/data/{mac_address}/{hours}", tags=["Influx"])
# async def get_sensor_data(mac_address: str, hours: int):
#     query = f"""
#     from(bucket: "db")
#     |> range(start: -{hours}h) // Adjust the time range as needed
#     |> aggregateWindow(every: 5m, fn: mean)
#     |> filter(fn: (r) => r["topic"] == "/sensors/{mac_address}")
#     |> sort(columns: ["_field"], desc: false) // Replace "_field" with the desired column to sort by
#     """
#
#     tables = query_api.query(query)
#
#     results = []
#     for table in tables:
#         for record in table.records:
#             results.append({
#                 "time": record.get_time(),
#                 "field": record.get_field(),
#                 "value": record.get_value(),
#             })
#
#     return results;

@router.get("/last_data/{mac_address}", description="returns last available data", response_model=SensorLastDataResponse)
async def get_last_sensor_data(mac_address: str) -> SensorLastDataResponse:

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

@router.get("")
async def get_sensors(
    user_id: Optional[int] = Query(None),
    home_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Sensor)

    if user_id is not None:
        query = query.filter(Sensor.user_id == user_id)
    elif home_id is not None:
        query = query.filter(Sensor.home_id == home_id)

    sensors = query.all()

    return sensors


@router.get("/{mac_address}")
async def get_sensor(mac_address: str, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.mac_address == mac_address).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found.")

    return jsonable_encoder(sensor)


@router.delete("/{mac_address}", response_model=dict)
async def delete_sensor(mac_address: str, db: Session = Depends(get_db)):
    # Find the sensor
    sensor = db.query(Sensor).filter(Sensor.mac_address == mac_address).first()

    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found.")

    # Delete the sensor
    db.delete(sensor)
    db.commit()

    return {"detail": "Sensor deleted successfully."}