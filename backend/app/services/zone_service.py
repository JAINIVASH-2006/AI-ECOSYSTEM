import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.entities import Zone
from ..gis.geometry import (
    validate_geojson_geometry,
    calculate_geodesic_area_sq_km,
    calculate_centroid,
    get_spatial_scale_category
)
from ..gis.spatial_queries import find_nearby_zones, find_containing_zone
from ..schemas.schemas import ZoneCreate, ZoneUpdate

def serialize_zone_to_feature(zone: Zone) -> Dict[str, Any]:
    """
    Serializes a database Zone entity into a valid GeoJSON Feature.
    """
    return {
        "type": "Feature",
        "geometry": zone.geometry_json,
        "properties": {
            "id": zone.id,
            "zone_code": zone.zone_code,
            "name": zone.name,
            "region": zone.region,
            "district": zone.district,
            "state": zone.state,
            "country": zone.country,
            "area_sq_km": zone.area_sq_km,
            "analysis_scale": zone.analysis_scale,
            "priority_score": zone.priority_score,
            "priority_class": zone.priority_class or "Not Analyzed",
            "analysis_status": zone.analysis_status or "NOT_ANALYZED",
            "created_at": zone.created_at.strftime("%Y-%m-%d %H:%M") if zone.created_at else None
        }
    }

def serialize_zone_detail(zone: Zone) -> Dict[str, Any]:
    """
    Serializes a database Zone entity into a detailed REST response object.
    """
    return {
        "id": zone.id,
        "zone_code": zone.zone_code,
        "name": zone.name,
        "region": zone.region,
        "district": zone.district,
        "state": zone.state,
        "country": zone.country,
        "area_sq_km": zone.area_sq_km,
        "analysis_scale": zone.analysis_scale,
        "centroid": {
            "latitude": zone.centroid_lat,
            "longitude": zone.centroid_lon
        },
        "geometry": zone.geometry_json,
        "priority_score": zone.priority_score,
        "priority_class": zone.priority_class or "Not Analyzed",
        "analysis_status": zone.analysis_status or "NOT_ANALYZED",
        "created_by": zone.created_by or "system",
        "geometry_source": zone.geometry_source or "EcoRestore GIS Engine",
        "created_at": zone.created_at.strftime("%Y-%m-%d %H:%M") if zone.created_at else None,
        "updated_at": zone.updated_at.strftime("%Y-%m-%d %H:%M") if zone.updated_at else None
    }

def get_all_zones_geojson(db: Session, priority_class: Optional[str] = None, analysis_status: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns all zones as a standard GeoJSON FeatureCollection.
    """
    query = db.query(Zone)
    if priority_class and priority_class != "ALL":
        query = query.filter(Zone.priority_class == priority_class)
    if analysis_status and analysis_status != "ALL":
        query = query.filter(Zone.analysis_status == analysis_status)

    zones = query.all()
    features = [serialize_zone_to_feature(z) for z in zones if z.geometry_json]

    return {
        "type": "FeatureCollection",
        "features": features
    }

def get_zone_by_id(db: Session, zone_id: int) -> Zone:
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone with ID {zone_id} not found.")
    return zone

def create_zone(db: Session, payload: ZoneCreate) -> Zone:
    """
    Validates GeoJSON geometry, computes geodesic area in km² and centroid,
    generates unique zone code, and persists the new zone.
    """
    is_valid, err_msg, geom_obj = validate_geojson_geometry(payload.geometry)
    if not is_valid:
        raise HTTPException(status_code=422, detail=f"Spatial Validation Error: {err_msg}")

    # Compute spatial attributes
    area_sq_km = calculate_geodesic_area_sq_km(geom_obj)
    centroid_lat, centroid_lon = calculate_centroid(geom_obj)
    scale = get_spatial_scale_category(area_sq_km)

    # Generate unique zone code
    zone_count = db.query(Zone).count()
    zone_code = f"ZONE-{zone_count + 1:03d}"

    zone = Zone(
        zone_code=zone_code,
        name=payload.name,
        region=payload.region or "Custom Study Area",
        district=payload.district,
        state=payload.state,
        country=payload.country or "India",
        geometry_json=payload.geometry,
        centroid_lat=centroid_lat,
        centroid_lon=centroid_lon,
        area_sq_km=area_sq_km,
        analysis_scale=scale,
        priority_score=None,
        priority_class="Not Analyzed",
        analysis_status="NOT_ANALYZED",
        created_by=payload.created_by or "analyst",
        geometry_source="User Drawn GeoJSON",
        geometry_version="1.0"
    )

    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

def update_zone(db: Session, zone_id: int, payload: ZoneUpdate) -> Zone:
    zone = get_zone_by_id(db, zone_id)
    if payload.name:
        zone.name = payload.name
    if payload.district:
        zone.district = payload.district
    if payload.state:
        zone.state = payload.state
    if payload.region:
        zone.region = payload.region
    db.commit()
    db.refresh(zone)
    return zone

def delete_zone(db: Session, zone_id: int) -> bool:
    zone = get_zone_by_id(db, zone_id)
    db.delete(zone)
    db.commit()
    return True

def query_containing_zone(db: Session, lat: float, lon: float) -> Optional[Dict[str, Any]]:
    zones = db.query(Zone).all()
    containing = find_containing_zone(lat, lon, zones)
    if containing:
        return serialize_zone_detail(containing)
    return None

def query_nearby_zones(db: Session, lat: float, lon: float, radius_km: float = 50.0) -> List[Dict[str, Any]]:
    zones = db.query(Zone).all()
    nearby = find_nearby_zones(lat, lon, zones, radius_km)
    return [
        {
            "zone": serialize_zone_detail(item["zone"]),
            "distance_km": item["distance_km"]
        }
        for item in nearby
    ]
