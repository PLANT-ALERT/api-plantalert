from fastapi import FastAPI, HTTPException, Query
from connector import return_cursor
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.encoders import jsonable_encoder

app = FastAPI()

# Database cursor
cursor = return_cursor()

# Pydantic models for input validation
class Home(BaseModel):
    name: str
    address: str
    create_at: datetime

class User(BaseModel):
    home_id: Optional[int]
    image: str
    username: str
    email: str
    password: str
    created_at: datetime

class Sensor(BaseModel):
    user_id: int  # Association with a user
    home_id: Optional[int]  # Association with a user
    name: str
    description: str
    mac_address: str
    location: str
    age: int
    flower_id: int

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

# User Management Endpoints
@app.post("/users/", response_model=User)
async def create_user(user: User):
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user.username,))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=400, detail="User already exists")
    cursor.execute(
        "INSERT INTO users (home_id, image, username, email, password, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
        (user.home_id, user.image, user.username, user.email, user.password, user.created_at),
    )
    cursor.connection.commit()
    return user

@app.get("/users/")
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
    # Volitelně: Použít jsonable_encoder pro zajištění kompatibility s JSON serializací
    return jsonable_encoder(users_json)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    cursor.execute("SELECT home_id, id, username, email, image, created_at FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_json = {
        "home_id": user[0],
        "id": user[1],
        "username": user[2],
        "email": user[3],
        "image": user[4],
        "created_at": user[5],
    }

    # Volitelně: Použít jsonable_encoder pro zajištění kompatibility s JSON serializací
    return jsonable_encoder(user_json)

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute(
        "UPDATE users SET home_id = %s, image = %s, username = %s, email = %s, password = %s, created_at = %s WHERE id = %s",
        (user.home_id, user.image, user.username, user.email, user.password, user.created_at, user_id),
    )
    return user

@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
    if cursor.fetchone()[0] == 0:
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    return {"detail": "User deleted"}

# Home Management Endpoints
@app.post("/homes/", response_model=Home)
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

@app.post("/sensors/", response_model=Sensor, status_code=201)
async def create_sensor(sensor: Sensor):
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (sensor.mac_address,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="MAC address already exists.")
    try:
        cursor.execute(
            """
            INSERT INTO sensors (user_id, home_id, name, description, mac_address, location, age, flower_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
            """,
            (sensor.user_id, sensor.home_id, sensor.name, sensor.description, sensor.mac_address, sensor.location,
            sensor.age, sensor.flower_id)
        )
        cursor.connection.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sensor: {str(e)}")
    return sensor

@app.get("/sensors/")
async def get_sensors(user_id: Optional[int] = Query(None), home_id: Optional[int] = Query(None)):
    """Retrieve a list of sensors, optionally filtered by user_id or home_id."""
    if user_id is not None:
        cursor.execute("SELECT * FROM sensors WHERE user_id = %s", (user_id,))
    elif home_id is not None:
        cursor.execute("SELECT * FROM sensors WHERE home_id = %s", (home_id,))
    else:
        cursor.execute("SELECT * FROM sensors")

    sensors = cursor.fetchall()
    return [
        {
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
        for row in sensors
    ]

@app.get("/sensors/{mac_address}")
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

@app.put("/sensors/{mac_address}", response_model=Sensor)
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

@app.delete("/sensors/{mac_address}", response_model=dict)
async def delete_sensor(mac_address: str):
    """Delete a sensor by its MAC address."""
    cursor.execute("SELECT * FROM sensors WHERE mac_address = %s", (mac_address,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Sensor not found.")

    cursor.execute("DELETE FROM sensors WHERE mac_address = %s", (mac_address,))
    return {"detail": "Sensor deleted successfully."}



