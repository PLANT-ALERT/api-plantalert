from sqlalchemy import Column, Integer, String, Float, DateTime
from app.connector import Base, engine

class Home(Base):
    __tablename__ = 'home'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)


Base.metadata.create_all(engine)