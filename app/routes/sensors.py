from app.depedencies import cursor, pwd_context, influx_client
from fastapi import HTTPException, Query
from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.models.sensors import Sensor, SensorLastDataResponse
from fastapi import APIRouter

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


@router.post("", status_code=201)
async def create_sensor(sensor: Sensor):
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (sensor.mac_address,))
    if cursor.fetchone():
        raise HTTPException(status_code=401, detail="MAC address already exists.")
    try:
        cursor.execute(
            """
            INSERT INTO sensors (user_id, name, mac_address, created_at)
            VALUES (%s, %s, %s, now())
            """,
            (sensor.user_id, sensor.name, sensor.mac_address,)
        )
        cursor.connection.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sensor: {str(e)}")
    return sensor

@router.get("")
async def get_sensors(user_id: Optional[int] = Query(None), home_id: Optional[int] = Query(None)):
    if user_id is not None:
        cursor.execute(
            "SELECT home_id, name, description, mac_address, location, age, flower_id, created_at FROM sensors WHERE user_id = %s",
            (user_id,)
        )
    elif home_id is not None:
        cursor.execute(
            "SELECT home_id, name, description, mac_address, location, age, flower_id, created_at FROM sensors WHERE home_id = %s",
            (home_id,)
        )
    else:
        cursor.execute(
            "SELECT home_id, name, description, mac_address, location, age, flower_id, created_at FROM sensors"
        )

    sensor_data = cursor.fetchall()

    sensors = [
        {
            "home_id": row[0],
            "name": row[1],
            "description": row[2],
            "mac_address": row[3],
            "location": row[4],
            "age": row[5],
            "flower_id": row[6],
            "created_at": row[7],
        }
        for row in sensor_data
    ]

    return sensors


@router.get("/{mac_address}")
async def get_sensor(mac_address: str):
    """Retrieve a sensor by its MAC address."""
    cursor.execute("SELECT home_id, name, location, description, age, flower_id, created_at FROM sensors WHERE mac_address = %s", (mac_address,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor not found.")
    sensor_json = {
        "home_id": row.home_id,
        "name": row.name,
        "description": row.description,
        "mac_address": row.mac_address,
        "location": row.location,
        "age": row.age,
        "flower_id": row.flower_id,
        "created_at": row.created_at,
    }

    return jsonable_encoder(sensor_json)


@router.delete("/{mac_address}", response_model=dict)
async def delete_sensor(mac_address: str):
    """Delete a sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Sensor not found.")

    cursor.execute("DELETE FROM sensors WHERE mac_address = %s", (mac_address,))
    return {"detail": "Sensor deleted successfully."}

