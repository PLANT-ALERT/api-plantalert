from sqlalchemy.sql import func

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.connector import Base, engine
from app.models.flower import Flower
from app.models.home import Home
from app.models.user import User


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    mac_address = Column(String(20), nullable=False)
    description = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    flower_id = Column(Integer, ForeignKey(Flower.id) , nullable=True)
    user_id = Column(Integer, ForeignKey(User.id) , nullable=False)
    home_id = Column(Integer, ForeignKey(Home.id) , nullable=True)


    flower = relationship('Flower', foreign_keys='Sensor.flower_id')
    home = relationship('Home', foreign_keys='Sensor.home_id')
    user = relationship('User', foreign_keys='Sensor.user_id')

Base.metadata.create_all(engine)