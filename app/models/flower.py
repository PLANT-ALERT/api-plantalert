from sqlalchemy import Column, Integer, String, Float
from app.connector import Base, engine
class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    max_soil_humidity = Column(Integer, nullable=True)
    min_soil_humidity = Column(Integer, nullable=True)
    max_air_humidity = Column(Integer, nullable=True)
    min_air_humidity = Column(Integer, nullable=True)
    max_air_temperature = Column(Float, nullable=True)
    min_air_temperature = Column(Float, nullable=True)
    light = Column(Integer, nullable=True)
    image = Column(String(50), nullable=True)
    name = Column(String(50), nullable=False)

Base.metadata.create_all(engine)