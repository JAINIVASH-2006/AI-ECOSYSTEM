from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "ENVIRONMENTAL_ANALYST"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

# --- GIS & Spatial Schemas ---
class ZoneCreate(BaseModel):
    name: str
    geometry: Dict[str, Any]
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    region: Optional[str] = "Custom Analysis Area"
    created_by: Optional[str] = "analyst"

class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None

class Centroid(BaseModel):
    latitude: float
    longitude: float

class ZoneGeoJSONProperties(BaseModel):
    id: int
    zone_code: str
    name: str
    region: str
    district: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    area_sq_km: float
    analysis_scale: str
    priority_score: Optional[float] = None
    priority_class: str = "Not Analyzed"
    analysis_status: str = "NOT_ANALYZED"
    created_at: Optional[str] = None

class ZoneGeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: Dict[str, Any]
    properties: ZoneGeoJSONProperties

class ZoneGeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[ZoneGeoJSONFeature]

class ZoneDetailResponse(BaseModel):
    id: int
    zone_code: str
    name: str
    region: str
    district: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    area_sq_km: float
    analysis_scale: str
    centroid: Centroid
    geometry: Optional[Dict[str, Any]] = None
    priority_score: Optional[float] = None
    priority_class: str = "Not Analyzed"
    analysis_status: str = "NOT_ANALYZED"
    created_by: str = "system"
    geometry_source: str = "EcoRestore GIS Engine"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class PointContainmentRequest(BaseModel):
    latitude: float
    longitude: float

class NearbyZonesRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 50.0

class NearbyZoneItem(BaseModel):
    zone: ZoneDetailResponse
    distance_km: float

# --- Simulation Schemas ---
class SimulationRequest(BaseModel):
    zone_id: int
    afforestation_density_pct: float = 50.0
    water_harvesting_units: int = 10
    biochar_treatment_pct: float = 30.0

class SimulationResponse(BaseModel):
    zone_id: int
    current_health: float
    projected_health: float
    health_gain_pct: float
    current_ndvi: float
    projected_ndvi: float
    ndvi_gain: float
    current_carbon_tco2e: float
    simulated_total_carbon_tco2e: float
    cost_estimate_lakhs: float

class DashboardSummary(BaseModel):
    total_zones: int
    total_area_sq_km: float
    avg_health_score: float
    critical_zones_count: int
    mean_ndvi: float
    total_carbon_offset_k_tco2e: float
    total_budget_lakhs: float
    priority_counts: Dict[str, int]
    active_alerts: List[Dict[str, Any]]
