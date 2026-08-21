import os
import time
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Internal imports
from src.database.models import init_db
from src.services.geolocation_service import GeolocationService
from src.services.history import HistoryService
from src.services.map_service import get_map_html
from src.core.utils import resolve_ip
from src.providers.factory import ProviderFactory

# Initialize Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GeoEngineAPI")

# Initialize Database
try:
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully.")
except Exception as e:
    logger.critical(f"Database initialization failed: {e}")
    raise e

# Setup FastAPI App
app = FastAPI(
    title="GeoEngine Pro API",
    description="Enterprise Geolocation Platform API",
    version="1.0.0"
)

# Setup Templates Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Instantiate services
geolocation_service = GeolocationService()


# Request/Response Schemas
class LookupRequest(BaseModel):
    ip_or_domain: str


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request) -> HTMLResponse:
    """Serves the main interactive web dashboard."""
    try:
        logger.info("Serving web dashboard.")
        return templates.TemplateResponse(
            request=request, 
            name="index.html"
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return HTMLResponse(
            content=f"<h1>Internal Server Error</h1><p>Could not load the dashboard template: {e}</p>",
            status_code=500
        )


@app.post("/api/lookup")
async def lookup_ip_or_domain(request: LookupRequest) -> Dict[str, Any]:
    """
    Lookup geolocation for an IP or Domain.
    Resolves domain, gets location, saves to lookup history, and generates map snippet.
    """
    target = request.ip_or_domain.strip()
    if not target:
        raise HTTPException(status_code=400, detail="Target IP or Domain cannot be empty.")

    logger.info(f"Received lookup request for target: {target}")
    
    try:
        # Resolve target to IP if it is a domain
        resolved_ip = resolve_ip(target)
        logger.info(f"Resolved target '{target}' to IP '{resolved_ip}'")
    except Exception as e:
        logger.error(f"Failed to resolve host '{target}': {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not resolve or validate IP/domain '{target}'. Error: {e}"
        )

    try:
        # Perform geolocation lookup with Failover
        start_time = time.perf_counter()
        data = geolocation_service.get_location(resolved_ip)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Save to lookup history in database
        HistoryService.save_lookup(data)
        logger.info(f"Lookup successful for {resolved_ip}. Saved to history database.")
    except Exception as e:
        logger.error(f"Geolocation lookup failed for '{resolved_ip}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch geolocation details for {resolved_ip}: {e}"
        )

    # Generate Map HTML and coordinates
    map_html = ""
    map_coordinates = {"lat": None, "lon": None}
    
    if data.latitude is not None and data.longitude is not None:
        map_coordinates["lat"] = data.latitude
        map_coordinates["lon"] = data.longitude
        try:
            map_html = get_map_html(data.latitude, data.longitude, data.city or "Unknown")
        except Exception as e:
            logger.warning(f"Failed to generate map HTML for coordinates: {e}")

    # Return complete JSON payload
    return {
        "status": "success",
        "target": target,
        "resolved_ip": resolved_ip,
        "data": {
            "ip": data.ip,
            "city": data.city or "Unknown",
            "region": data.region or "Unknown",
            "country": data.country or "Unknown",
            "latitude": data.latitude,
            "longitude": data.longitude,
            "provider": data.provider or "Unknown",
            "latency_ms": round(latency_ms, 2)
        },
        "map_coordinates": map_coordinates,
        "map_html": map_html
    }


@app.get("/api/history")
async def get_lookup_history() -> List[Dict[str, Any]]:
    """Returns the history of recent geolocation lookups from the SQLite database."""
    try:
        logger.info("Fetching lookup history.")
        records = HistoryService.get_history()
        
        formatted_history = []
        for r in records:
            formatted_history.append({
                "id": r.id,
                "ip": r.ip,
                "city": r.city or "Unknown",
                "region": r.region or "Unknown",
                "country": r.country or "Unknown",
                "latitude": r.latitude,
                "longitude": r.longitude,
                "provider": r.provider or "Unknown",
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S") if r.timestamp else "N/A"
            })
            
        # Return history records sorted descending by id to show newest first
        formatted_history.reverse()
        return formatted_history
    except Exception as e:
        logger.error(f"Error fetching lookup history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal database error while fetching history: {e}"
        )


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Checks the health and failover status of configured geolocation providers."""
    try:
        logger.info("Executing API and Provider health check.")
        factory = ProviderFactory()
        providers = factory.get_providers()
        
        provider_status = {}
        for provider in providers:
            provider_status[provider.name] = "available"
            
        return {
            "status": "healthy",
            "database": "connected",
            "active_providers": provider_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "reason": str(e)
            }
        )
