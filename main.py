from http.client import HTTPResponse

from fastapi import FastAPI, HTTPException, Query

import connector
from connector import return_cursor, return_influxdb_client
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import os


app = FastAPI()

influx_client = return_influxdb_client();

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allows headers like 'Content-Type'
)

# Database cursor
cursor = return_cursor()

# Pydantic models for input validation
class Home(BaseModel):
    name: str
    address: str
    create_at: datetime

class User(BaseModel):
    home_id: Optional[int] = None
    image: Optional[str] = None
    username: str
    email: str
    password: str

class Sensor(BaseModel):
    user_id: int  # Association with a user
    home_id: Optional[int]  # Association with a user
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int

class Sensor_Response(BaseModel):
    home_id: Optional[int]  # Association with a user
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int
    created_at: datetime

class Flower(BaseModel):
    user_id: Optional[int]  # null => demo flowers
    image: str
    name: str
    max_soil_humidity: int
    min_soil_humidity: int
    max_air_humidity: int
    min_air_humidity: int
    max_air_temperature: int
    min_air_temperature: int
    light: int

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    user_id: int

SECRET_KEY = connector.return_secret()
ALGORITHM = "HS256"



# User Management Endpoints
@app.post("/users/", tags=["Users"])
async def create_user(user: User):
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user.username,))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=401, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)
    cursor.execute(
        """
        INSERT INTO users (home_id, username, email, password, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id
        """,
        (user.home_id, user.username, user.email, hashed_password),
    )
    user_id = cursor.fetchone()[0]
    cursor.connection.commit()
    return {"user_id": user_id }

@app.post("/login/", response_model=TokenResponse, tags=["Users"])
async def login(login_request: LoginRequest):
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (login_request.username,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id, hashed_password = result

    if not pwd_context.verify(login_request.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"user_id": user_id}

@app.get("/users/", tags=["Users"])
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

@app.get("/users/{user_id}", tags=["Users"])
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

@app.put("/users/{user_id}", response_model=User, tags=["Users"])
async def update_user(user_id: int, user: User):
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute(
        "UPDATE users SET home_id = %s, image = %s, username = %s, email = %s, password = %s WHERE id = %s",
        (user.home_id, user.image, user.username, user.email, user.password, user_id),
    )
    return user

@app.delete("/users/{user_id}", tags=["Users"])
async def delete_user(user_id: int):
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    return {"detail": "User deleted"}

# Home Management Endpoints
@app.post("/homes/", response_model=Home, tags=["Homes"])
async def create_sensor(sensor: Home):
    cursor.execute("SELECT COUNT(*) FROM homes WHERE id = %s", (sensor.id,))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=400, detail="Home already exists")
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (sensor.user_id,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=400, detail="User not found")
    cursor.execute(
        "INSERT INTO homes (name, mac_address, location, user_id, age, flower_id, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (sensor.name, sensor.mac_address, sensor.location, sensor.user_id, sensor.age, sensor.flower_id, sensor.created_at),
    )
    return sensor

@app.get("/sensors/data/{mac_address}/{hours}/", tags=["Influx"])
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

@app.get("/sensors/last_data/{mac_address}/", tags=["Influx"])
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


@app.post("/sensors/", response_model=Sensor, status_code=201, tags=["Sensors"])
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

@app.get("/sensors/", response_model=List[Sensor_Response], tags=["Sensors"])
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


@app.get("/sensors/{mac_address}", tags=["Sensors"])
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

class SensorDataResponse(BaseModel):
    time: str
    field_name: str
    field_value: float

@app.put("/sensors/{mac_address}", response_model=Sensor, tags=["Sensors"])
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

@app.delete("/sensors/{mac_address}", response_model=dict, tags=["Sensors"])
async def delete_sensor(mac_address: str):
    """Delete a sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Sensor not found.")

    cursor.execute("DELETE FROM sensors WHERE mac_address = %s", (mac_address,))
    return {"detail": "Sensor deleted successfully."}



