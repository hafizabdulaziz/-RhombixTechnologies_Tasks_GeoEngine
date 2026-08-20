import logging
from typing import List
from src.core.interfaces import GeolocationProvider
from src.core.models import GeolocationData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FailoverService:
    def __init__(self, providers: List[GeolocationProvider]):
        self.providers = providers

    def fetch_with_failover(self, ip: str) -> GeolocationData:
        for provider in self.providers:
            try:
                logger.info(f"Attempting lookup with provider: {provider.name}")
                return provider.fetch_geolocation(ip)
            except Exception as e:
                logger.error(f"Provider {provider.name} failed: {e}")
                continue
        logger.critical(f"All providers failed for IP: {ip}")
        raise Exception(f"All providers failed to fetch geolocation data for {ip}.")
