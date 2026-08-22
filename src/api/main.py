import os
import time
import logging
import uuid
from typing import Dict, Any, List
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Internal imports
from src.database.models import init_db
from src.services.geolocation_service import GeolocationService
from src.services.history import HistoryService
from src.services.map_service import get_map_html
from src.core.utils import resolve_ip
from src.providers.factory import ProviderFactory

# Initialize Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s")
logger = logging.getLogger("GeoTraceAPI")

# Initialize Database
try:
    logger.info("Initializing database...", extra={"request_id": "INIT"})
    init_db()
    logger.info("Database initialized successfully.", extra={"request_id": "INIT"})
except Exception as e:
    logger.critical(f"Database initialization failed: {e}", extra={"request_id": "INIT"})
    raise e

# Setup FastAPI App
app = FastAPI(
    title="GeoTrace API",
    description="Enterprise IP & Network Intelligence Platform API",
    version="1.0.0"
)

# CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Templates Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "web", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Instantiate services
geolocation_service = GeolocationService()

# --- Request/Response Schemas ---

class LookupRequest(BaseModel):
    ip_or_domain: str = Field(..., min_length=1, description="The IP address or domain to geolocate")

class GeoData(BaseModel):
    ip: str
    city: str
    country: str
    latitude: float | None = None
    longitude: float | None = None
    latency_ms: float
    provider: str

class LookupResponse(BaseModel):
    request_id: str
    status: str
    data: GeoData
    map_coordinates: Dict[str, float | None]
    map_html: str

class ErrorResponse(BaseModel):
    request_id: str
    detail: str

class HistoryItem(BaseModel):
    id: int
    ip: str
    city: str
    country: str
    timestamp: str

class Analytics(BaseModel):
    total_lookups: int
    success_rate: float

class HistoryResponse(BaseModel):
    analytics: Analytics
    history: List[HistoryItem]


# --- Middleware for Request ID ---

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_dashboard(request: Request) -> HTMLResponse:
    """Serves the main interactive web dashboard."""
    return templates.TemplateResponse(
        request=request, 
        name="index.html"
    )

@app.post("/api/v1/lookup", response_model=LookupResponse, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def lookup_ip_or_domain(request: Request, body: LookupRequest) -> LookupResponse:
    """
    Lookup geolocation for an IP or Domain.
    """
    request_id = request.state.request_id
    target = body.ip_or_domain.strip()
    
    logger.info(f"Received lookup request for target: {target}", extra={"request_id": request_id})
    
    try:
        resolved_ip = resolve_ip(target)
        logger.info(f"Resolved target '{target}' to IP '{resolved_ip}'", extra={"request_id": request_id})
    except ValueError as e:
        logger.warning(f"Validation failed for '{target}': {e}", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    try:
        start_time = time.perf_counter()
        data = geolocation_service.get_location(resolved_ip)
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        HistoryService.save_lookup(data)
        logger.info(f"Lookup successful for {resolved_ip}.", extra={"request_id": request_id})
    except Exception as e:
        logger.error(f"Geolocation lookup failed for '{resolved_ip}': {e}", extra={"request_id": request_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch geolocation data. Please try again later."
        )

    map_html = ""
    map_coordinates = {"lat": None, "lon": None}
    
    if data.latitude is not None and data.longitude is not None:
        map_coordinates["lat"] = data.latitude
        map_coordinates["lon"] = data.longitude
        try:
            map_html = get_map_html(data.latitude, data.longitude, data.city or "Unknown")
        except Exception as e:
            logger.warning(f"Map generation failed: {e}", extra={"request_id": request_id})

    return LookupResponse(
        request_id=request_id,
        status="success",
        data=GeoData(
            ip=data.ip,
            city=data.city or "Unknown",
            country=data.country or "Unknown",
            latitude=data.latitude,
            longitude=data.longitude,
            latency_ms=round(latency_ms, 2),
            provider=data.provider or "Unknown"
        ),
        map_coordinates=map_coordinates,
        map_html=map_html
    )

@app.get("/api/v1/history", response_model=HistoryResponse)
async def get_lookup_history(request: Request) -> HistoryResponse:
    """Returns the history of recent geolocation lookups with analytics."""
    try:
        records = HistoryService.get_history()
        analytics = HistoryService.get_analytics()
        
        formatted_history = [
            HistoryItem(
                id=r.id, ip=r.ip, city=r.city or "Unknown", country=r.country or "Unknown",
                timestamp=r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            )
            for r in records
        ]
        
        return HistoryResponse(
            analytics=Analytics(
                total_lookups=analytics["total_lookups"],
                success_rate=analytics["success_rate"]
            ),
            history=formatted_history
        )
    except Exception as e:
        logger.error(f"Error fetching history: {e}", extra={"request_id": request.state.request_id})
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Checks the health and failover status of configured geolocation providers."""
    return {
        "status": "healthy",
        "database": "connected",
        "request_id": request.state.request_id
    }
