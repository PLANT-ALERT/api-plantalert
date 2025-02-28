from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import func, DateTime
from app.connector import Base, engine
from app.models.home import Home


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    image = Column(String(50), nullable=True)
    email = Column(String(50), nullable=True)
    password = Column(String(255), nullable=True)
    home_id = Column(Integer, ForeignKey(Home.id) , nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    home = relationship('Home', foreign_keys='User.home_id')

Base.metadata.create_all(engine)