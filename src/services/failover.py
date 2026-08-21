import logging
import time
from typing import List
from src.core.interfaces import GeolocationProvider
from src.core.models import GeolocationData

logger = logging.getLogger(__name__)

class FailoverService:
    def __init__(self, providers: List[GeolocationProvider], max_retries: int = 1):
        self.providers = providers
        self.max_retries = max_retries

    def fetch_with_failover(self, ip: str) -> GeolocationData:
        for provider in self.providers:
            for attempt in range(self.max_retries + 1):
                try:
                    logger.info(f"Attempting lookup with provider: {provider.name} (Attempt {attempt + 1})")
                    return provider.fetch_geolocation(ip)
                except Exception as e:
                    logger.warning(f"Provider {provider.name} failed (Attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries:
                        time.sleep(1)  # Brief backoff
                        continue
                    break # Exhausted retries for this provider
        
        logger.critical(f"All providers failed for IP: {ip}")
        raise Exception(f"All providers failed to fetch geolocation data for {ip}.")
