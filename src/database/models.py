import os
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# Use absolute path to ensure DB is created in project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'geoengine.db')}"

Base = declarative_base()

class LookupHistory(Base):
    __tablename__ = 'lookup_history'
    id = Column(Integer, primary_key=True)
    ip = Column(String, index=True)
    city = Column(String)
    region = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    provider = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))

# sqlite check_same_thread=False is needed for multi-threaded/async apps
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)
