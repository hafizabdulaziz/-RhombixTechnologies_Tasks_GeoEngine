import logging
import time
from typing import List
from src.core.interfaces import GeolocationProvider
from src.core.models import GeolocationData

logger = logging.getLogger(__name__)

class ProviderException(Exception):
    """Custom exception for provider-specific failures."""
    pass

class FailoverService:
    def __init__(self, providers: List[GeolocationProvider], max_retries: int = 2):
        self.providers = providers
        self.max_retries = max_retries

    def fetch_with_failover(self, ip: str) -> GeolocationData:
        errors = []
        for provider in self.providers:
            for attempt in range(self.max_retries + 1):
                try:
                    logger.info(f"Attempting lookup with provider: {provider.name} (Attempt {attempt + 1})")
                    return provider.fetch_geolocation(ip)
                except Exception as e:
                    error_msg = f"Provider {provider.name} failed (Attempt {attempt + 1}): {e}"
                    logger.warning(error_msg)
                    errors.append(error_msg)
                    
                    if attempt < self.max_retries:
                        time.sleep(1 * (attempt + 1))  # Progressive backoff
                        continue
                    break # Exhausted retries for this provider
        
        error_summary = " | ".join(errors)
        logger.critical(f"All providers failed for IP: {ip}. Errors: {error_summary}")
        raise ProviderException(f"Geolocation lookup failed after trying all providers. Summary: {error_summary}")
