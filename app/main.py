from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.include_routers import include_routers
from pathlib import Path
import os

description = """
    [github repository of project](https://github.com/PLANT-ALERT/api-plantalert)
"""

app = FastAPI(
    title="Plant Alert API",
    description=description,
    version="0.0.1",
)   

app = include_routers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
