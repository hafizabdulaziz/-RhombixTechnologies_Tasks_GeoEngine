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
    assert "GeoEngine Pro" in response.text
    assert "Interactive Visual Node Mapping" in response.text


def test_api_health():
    """Test that the health endpoint returns provider status and general health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "active_providers" in data


def test_api_history():
    """Test that history endpoint successfully returns a list of recent lookups."""
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_lookup_validation_error():
    """Test that passing an empty target returns a 400 Bad Request error."""
    response = client.post("/api/lookup", json={"ip_or_domain": "   "})
    assert response.status_code == 400
    assert "Target IP or Domain cannot be empty" in response.json()["detail"]


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
    response = client.post("/api/lookup", json=payload)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["target"] == "8.8.8.8"
    assert result["resolved_ip"] == "8.8.8.8"
    assert result["data"]["ip"] == "8.8.8.8"
    assert result["data"]["city"] == "Mountain View"
    assert result["data"]["country"] == "United States"
    assert result["data"]["latitude"] == 37.4223
    assert result["data"]["longitude"] == -122.0847
    assert "map_coordinates" in result
    assert result["map_coordinates"]["lat"] == 37.4223
    assert "map_html" in result
    assert "leaflet" in result["map_html"].lower()
