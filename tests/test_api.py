import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app
from src.core.models import GeolocationData

client = TestClient(app)


def test_serve_dashboard():
    """Test that the main index route returns 200 and serves the dashboard HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "GeoTrace" in response.text
    assert "Live Map" in response.text


def test_api_health():
    """Test that the health endpoint returns provider status and general health."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

def test_api_history():
    """Test that history endpoint successfully returns a list of recent lookups."""
    response = client.get("/api/v1/history")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert isinstance(data["history"], list)

def test_api_lookup_validation_error():
    """Test that passing an empty target returns a 422 Validation error."""
    # Pydantic min_length=1 triggers 422
    response = client.post("/api/v1/lookup", json={"ip_or_domain": ""})
    assert response.status_code == 422

def test_api_lookup_malformed_input():
    """Test that malformed input returns a 400 error."""
    response = client.post("/api/v1/lookup", json={"ip_or_domain": "127.0.0.1127.0."})
    assert response.status_code == 400

@patch("src.services.geolocation_service.GeolocationService.get_location")
def test_api_lookup_success(mock_get_location):
    """Test a successful geolocation lookup via the POST endpoint using mock data."""
    # Mocking GeolocationService output to isolate the API test from external API calls
    mock_get_location.return_value = GeolocationData(
        ip="8.8.8.8",
        city="Mountain View",
        region="California",
        country="United States",
        latitude=37.4223,
        longitude=-122.0847,
        provider="ip-api"
    )

    payload = {"ip_or_domain": "8.8.8.8"}
    response = client.post("/api/v1/lookup", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["data"]["ip"] == "8.8.8.8"
