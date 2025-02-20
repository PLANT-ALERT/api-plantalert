from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.include_routers import include_routers
from pathlib import Path
import os

description = Path(os.path.dirname(os.path.abspath(__file__)) + "/description.md").read_text(encoding="utf-8")

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
