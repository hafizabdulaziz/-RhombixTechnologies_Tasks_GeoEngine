import pytest
from src.core.models import GeolocationData
from src.providers.ip_api import IpApiProvider

def test_geolocation_data():
    data = GeolocationData(ip="8.8.8.8", city="TestCity")
    assert data.ip == "8.8.8.8"
    assert data.city == "TestCity"

def test_ip_api_provider_name():
    provider = IpApiProvider()
    assert provider.name == "ip-api"
