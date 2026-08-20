from src.core.models import GeolocationData
from src.providers.factory import ProviderFactory
from src.services.failover import FailoverService

class GeolocationService:
    def __init__(self):
        self._factory = ProviderFactory()
        self._failover_service = FailoverService(self._factory.get_providers())

    def get_location(self, ip: str) -> GeolocationData:
        """Get geolocation data for an IP, using failover if necessary."""
        return self._failover_service.fetch_with_failover(ip)
