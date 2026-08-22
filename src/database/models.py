import os
from sqlalchemy import Column, Integer, String, Float, DateTime, create_engine, Index
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# Database URL
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'geoengine.db')}"

Base = declarative_base()

class LookupHistory(Base):
    __tablename__ = 'lookup_history'
    id = Column(Integer, primary_key=True)
    ip = Column(String, index=True, nullable=False)
    city = Column(String, nullable=True)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    provider = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)

    __table_args__ = (
        Index('idx_ip_timestamp', 'ip', 'timestamp'),
    )

# Use absolute path and optimized SQLite settings
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True # Helps with reconnection
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)

