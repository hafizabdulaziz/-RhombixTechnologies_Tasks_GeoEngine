from contextlib import contextmanager
from sqlalchemy import func
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
    def get_history(limit: int = 50):
        with SessionLocal() as session:
            return session.query(LookupHistory).order_by(LookupHistory.timestamp.desc()).limit(limit).all()

    @staticmethod
    def get_analytics():
        with SessionLocal() as session:
            total = session.query(func.count(LookupHistory.id)).scalar()
            # Current logic assumes all saved lookups were successful.
            return {
                "total_lookups": total or 0,
                "success_rate": 100.0 if total and total > 0 else 0.0
            }
