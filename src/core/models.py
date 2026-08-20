from dataclasses import dataclass
from typing import Optional

@dataclass
class GeolocationData:
    ip: str
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    provider: Optional[str] = None
