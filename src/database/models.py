from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class LookupHistory(Base):
    __tablename__ = 'lookup_history'
    id = Column(Integer, primary_key=True)
    ip = Column(String)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    provider = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine('sqlite:///geoengine.db')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
