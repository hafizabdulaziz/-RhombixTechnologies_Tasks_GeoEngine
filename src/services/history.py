from src.database.models import SessionLocal, LookupHistory
from src.core.models import GeolocationData

class HistoryService:
    @staticmethod
    def save_lookup(data: GeolocationData):
        session = SessionLocal()
        record = LookupHistory(
            ip=data.ip,
            city=data.city,
            region=data.region,
            country=data.country,
            latitude=data.latitude,
            longitude=data.longitude,
            provider=data.provider
        )
        session.add(record)
        session.commit()
        session.close()

    @staticmethod
    def get_history():
        session = SessionLocal()
        records = session.query(LookupHistory).all()
        session.close()
        return records
