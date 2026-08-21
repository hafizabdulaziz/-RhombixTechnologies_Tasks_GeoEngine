from contextlib import contextmanager
from src.database.models import SessionLocal, LookupHistory
from src.core.models import GeolocationData

class HistoryService:
    @contextmanager
    def _get_session():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def save_lookup(data: GeolocationData):
        with HistoryService._get_session() as session:
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

    @staticmethod
    def get_history():
        with SessionLocal() as session:
            return session.query(LookupHistory).all()
