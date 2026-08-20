from typing import List
from src.core.interfaces import GeolocationProvider
from src.core.models import GeolocationData

class FailoverService:
    def __init__(self, providers: List[GeolocationProvider]):
        self.providers = providers

    def fetch_with_failover(self, ip: str) -> GeolocationData:
        for provider in self.providers:
            try:
                return provider.fetch_geolocation(ip)
            except Exception as e:
                print(f"Provider {provider.name} failed: {e}")
                continue
        raise Exception("All providers failed to fetch geolocation data.")
