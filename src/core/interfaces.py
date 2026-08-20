from abc import ABC, abstractmethod
from src.core.models import GeolocationData

class GeolocationProvider(ABC):
    @abstractmethod
    def fetch_geolocation(self, ip: str) -> GeolocationData:
        """Fetch geolocation data for a given IP address."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider."""
        pass
