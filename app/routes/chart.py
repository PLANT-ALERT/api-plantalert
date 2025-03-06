from app.depedencies import influx_client
from app.schema.chart import ChartResponse, extraData
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

query_api = influx_client.query_api()

def fetch_sensor_data(mac_address: str, hours: int, field_name: str):
    """Fetches sensor data for a specific field from InfluxDB."""
    query = f"""
    from(bucket: "db")
    |> range(start: -{hours}h)
    |> filter(fn: (r) => r["topic"] == "/sensors/{mac_address}")
    |> filter(fn: (r) => r["_field"] == "{field_name}")
    |> aggregateWindow(every: 1m, fn: mean)
    |> filter(fn: (r) => exists r._value)
    |> yield(name: "mean")
    """

    tables = query_api.query(query)

    results = []
    for table in tables:
        for record in table.records:
            results.append(ChartResponse(
                x=str(record.get_time()),  # Convert to milliseconds
                y=record.get_value(),
                extraData=extraData(
                    formattedValue=str(f"{record.get_value()}"),
                    formattedTime=str(f"{record.get_time().isoformat()}"),
                )
            ))

    return results


@router.get("/soil-humidity/{mac_address}/{hours}", response_model=List[ChartResponse])
async def get_soil_humidity(mac_address: str, hours: int):
    return fetch_sensor_data(mac_address, hours, "soil")


@router.get("/air-humidity/{mac_address}/{hours}", response_model=List[ChartResponse])
async def get_air_humidity(mac_address: str, hours: int):
    return fetch_sensor_data(mac_address, hours, "humidity")


@router.get("/temperature/{mac_address}/{hours}", response_model=List[ChartResponse])
async def get_temperature(mac_address: str, hours: int):
    return fetch_sensor_data(mac_address, hours, "temp")


@router.get("/light/{mac_address}/{hours}", response_model=List[ChartResponse])
async def get_light(mac_address: str, hours: int):
    return fetch_sensor_data(mac_address, hours, "light")