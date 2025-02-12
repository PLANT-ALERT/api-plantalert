from app.depedencies import cursor, pwd_context, influx_client
from fastapi import HTTPException, Query
from typing import Optional
from fastapi.encoders import jsonable_encoder
from app.models.sensors import Sensor, Sensor_Response, SensorDataResponse
from fastapi import APIRouter

router = APIRouter()

@router.get("/data/{mac_address}/{hours}", tags=["Influx"])
async def get_sensor_data(mac_address: str, hours: int):
    query_api = influx_client.query_api()

    query = f"""
    from(bucket: "db")
    |> range(start: -{hours}h) // Adjust the time range as needed
    |> aggregateWindow(every: 5m, fn: mean)
    |> filter(fn: (r) => r["topic"] == "/sensors/{mac_address}")
    |> sort(columns: ["_field"], desc: false) // Replace "_field" with the desired column to sort by
    """

    tables = query_api.query(query)

    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time(),
                "field": record.get_field(),
                "value": record.get_value(),
            })

    return results;

@router.get("/last_data/{mac_address}", tags=["Influx"])
async def get_last_sensor_data(mac_address: str):
    query_api = influx_client.query_api()

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


@router.post("", response_model=Sensor, status_code=201, tags=["Sensors"])
async def create_sensor(sensor: Sensor):
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (sensor.mac_address,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="MAC address already exists.")
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


@router.get("/{mac_address}", tags=["Sensors"])
async def get_sensor(mac_address: str):
    """Retrieve a sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sensor not found.")
    sensor_json = {
        "user_id": row[0],
        "home_id": row[1],
        "name": row[2],
        "description": row[3],
        "mac_address": row[4],
        "location": row[5],
        "age": row[6],
        "flower_id": row[7],
        "created_at": row[8]
    }

    return jsonable_encoder(sensor_json)

@router.put("/{mac_address}", response_model=Sensor, tags=["Sensors"])
async def update_sensor(mac_address: str, updated_sensor: Sensor):
    """Update an existing sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Sensor not found.")

    cursor.execute(
        """
        UPDATE sensors
        SET user_id = %s, home_id = %s, name = %s, description = %s, location = %s, age = %s, flower_id = %s, created_at = %s
        WHERE mac_address = %s
        """,
        (updated_sensor.user_id, updated_sensor.home_id, updated_sensor.name, updated_sensor.description, updated_sensor.location, updated_sensor.age, updated_sensor.flower_id, updated_sensor.created_at, mac_address)
    )
    return updated_sensor

@router.delete("/{mac_address}", response_model=dict, tags=["Sensors"])
async def delete_sensor(mac_address: str):
    """Delete a sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Sensor not found.")

    cursor.execute("DELETE FROM sensors WHERE mac_address = %s", (mac_address,))
    return {"detail": "Sensor deleted successfully."}

