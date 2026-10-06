from typing import List, Dict, Any, Optional
from shapely.geometry import shape, Point
from .geometry import haversine_distance_km

def point_in_zone(lat: float, lon: float, zone_geometry_dict: Dict[str, Any]) -> bool:
    """
    Checks if a geographic point (lat, lon) is contained within a zone polygon geometry.
    """
    try:
        pt = Point(lon, lat)
        geom = shape(zone_geometry_dict)
        return geom.contains(pt) or geom.touches(pt)
    except Exception:
        return False

def find_containing_zone(lat: float, lon: float, zones: List[Any]) -> Optional[Any]:
    """
    Finds the first zone in the list that contains the given latitude and longitude.
    """
    pt = Point(lon, lat)
    for z in zones:
        if z.geometry_json:
            try:
                geom = shape(z.geometry_json)
                if geom.contains(pt) or geom.touches(pt):
                    return z
            except Exception:
                continue
    return None

def find_nearby_zones(lat: float, lon: float, zones: List[Any], radius_km: float = 50.0) -> List[Dict[str, Any]]:
    """
    Finds and ranks zones within radius_km from a given coordinate.
    """
    nearby = []
    for z in zones:
        if z.centroid_lat is not None and z.centroid_lon is not None:
            dist = haversine_distance_km(lat, lon, z.centroid_lat, z.centroid_lon)
            if dist <= radius_km:
                nearby.append({
                    "zone": z,
                    "distance_km": dist
                })
    
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby
