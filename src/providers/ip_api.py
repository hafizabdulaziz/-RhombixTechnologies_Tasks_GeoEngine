import requests
from src.core.interfaces import GeolocationProvider
from src.core.models import GeolocationData

class IpApiProvider(GeolocationProvider):
    def __init__(self):
        self._name = "ip-api"
        self._base_url = "http://ip-api.com/json/"

    @property
    def name(self) -> str:
        return self._name

    def fetch_geolocation(self, ip: str) -> GeolocationData:
        """Fetch geolocation data from ip-api.com."""
        response = requests.get(f"{self._base_url}{ip}")
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "fail":
            raise ValueError(f"Failed to fetch geolocation: {data.get('message')}")

        return GeolocationData(
            ip=data.get("query", ip),
            city=data.get("city"),
            region=data.get("regionName"),
            country=data.get("country"),
            latitude=data.get("lat"),
            longitude=data.get("lon"),
            provider=self.name
        )
