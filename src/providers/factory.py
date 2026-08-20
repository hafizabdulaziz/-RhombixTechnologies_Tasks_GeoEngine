from typing import List
from src.core.interfaces import GeolocationProvider
from src.providers.ip_api import IpApiProvider

class ProviderFactory:
    def __init__(self):
        self._providers: List[GeolocationProvider] = [IpApiProvider()]

    def get_providers(self) -> List[GeolocationProvider]:
        return self._providers
