from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.include_routers import include_routers
app = FastAPI()

app = include_routers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins for production
    allow_credentials=True,
    allow_methods=["*"],  # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"],  # Allows headers like 'Content-Type'
)
