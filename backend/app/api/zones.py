from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..core.database import get_db
from ..schemas.schemas import (
    ZoneCreate,
    ZoneUpdate,
    ZoneDetailResponse,
    ZoneGeoJSONFeatureCollection,
    PointContainmentRequest,
    NearbyZoneItem
)
from ..services import zone_service

router = APIRouter(prefix="/zones", tags=["Restoration Zones & GIS Operations"])

@router.get("", response_model=ZoneGeoJSONFeatureCollection)
def get_zones_geojson(
    priority_class: Optional[str] = Query(None, description="Filter by priority tier (Very Low, Low, Moderate, High, Critical, Not Analyzed)"),
    analysis_status: Optional[str] = Query(None, description="Filter by analysis status (NOT_ANALYZED, PENDING, ANALYZED)"),
    db: Session = Depends(get_db)
):
    """
    Returns all spatial restoration zones as a standard GeoJSON FeatureCollection.
    """
    return zone_service.get_all_zones_geojson(db, priority_class, analysis_status)

@router.get("/nearby", response_model=List[NearbyZoneItem])
def get_nearby_zones(
    lat: float = Query(..., description="Target Latitude (-90 to 90)"),
    lon: float = Query(..., description="Target Longitude (-180 to 180)"),
    radius_km: float = Query(50.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Finds and ranks zones within radius_km from the provided coordinate.
    """
    if lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0:
        raise HTTPException(status_code=400, detail="Coordinates out of valid WGS84 range.")
    return zone_service.query_nearby_zones(db, lat, lon, radius_km)

@router.post("/contains-point", response_model=Optional[ZoneDetailResponse])
def check_point_containment(payload: PointContainmentRequest, db: Session = Depends(get_db)):
    """
    Point-in-polygon query: Checks if coordinates fall inside any saved restoration zone polygon.
    """
    if payload.latitude < -90.0 or payload.latitude > 90.0 or payload.longitude < -180.0 or payload.longitude > 180.0:
        raise HTTPException(status_code=400, detail="Coordinates out of valid WGS84 range.")
    
    result = zone_service.query_containing_zone(db, payload.latitude, payload.longitude)
    return result

@router.get("/{zone_id}", response_model=ZoneDetailResponse)
def get_zone(zone_id: int, db: Session = Depends(get_db)):
    """
    Retrieves full spatial metadata, centroid, area in km², and status for a specific zone.
    """
    zone = zone_service.get_zone_by_id(db, zone_id)
    return zone_service.serialize_zone_detail(zone)

@router.post("", response_model=ZoneDetailResponse, status_code=201)
def create_new_zone(payload: ZoneCreate, db: Session = Depends(get_db)):
    """
    Validates GeoJSON polygon geometry, calculates area in km² and centroid, and registers a new restoration study area.
    """
    zone = zone_service.create_zone(db, payload)
    return zone_service.serialize_zone_detail(zone)

@router.put("/{zone_id}", response_model=ZoneDetailResponse)
def update_zone_metadata(zone_id: int, payload: ZoneUpdate, db: Session = Depends(get_db)):
    """
    Updates zone name or administrative district/state metadata.
    """
    zone = zone_service.update_zone(db, zone_id, payload)
    return zone_service.serialize_zone_detail(zone)

@router.delete("/{zone_id}", status_code=200)
def delete_existing_zone(zone_id: int, db: Session = Depends(get_db)):
    """
    Deletes a zone and all associated GIS records.
    """
    zone_service.delete_zone(db, zone_id)
    return {"message": f"Zone {zone_id} deleted successfully."}
