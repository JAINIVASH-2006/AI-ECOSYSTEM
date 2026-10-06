import math
from typing import Dict, Any, Tuple, List, Optional
from shapely.geometry import shape, Point, Polygon, MultiPolygon
from shapely.validation import explain_validity

def validate_geojson_geometry(geom_dict: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Any]]:
    """
    Validates GeoJSON geometry structure, polygon closure, coordinate ranges, and topological validity.
    """
    if not isinstance(geom_dict, dict):
        return False, "Geometry must be a JSON object.", None
    
    geom_type = geom_dict.get("type")
    coords = geom_dict.get("coordinates")

    if not geom_type or coords is None:
        return False, "Geometry must contain 'type' and 'coordinates'.", None

    if geom_type not in ["Polygon", "MultiPolygon"]:
        return False, f"Unsupported geometry type '{geom_type}'. Only Polygon or MultiPolygon allowed for zones.", None

    try:
        geom = shape(geom_dict)
    except Exception as e:
        return False, f"Malformed GeoJSON coordinate structure: {str(e)}", None

    if geom.is_empty:
        return False, "Geometry is empty.", None

    if not geom.is_valid:
        reason = explain_validity(geom)
        return False, f"Invalid polygon topology: {reason}", None

    # Validate coordinate bounds (WGS84 EPSG:4326)
    minx, miny, maxx, maxy = geom.bounds
    if minx < -180.0 or maxx > 180.0 or miny < -90.0 or maxy > 90.0:
        return False, f"Coordinates out of bounds: Lon [{minx}, {maxx}], Lat [{miny}, {maxy}]", None

    return True, None, geom

def calculate_geodesic_area_sq_km(geom: Any) -> float:
    """
    Calculates approximate ellipsoidal area in square kilometers for WGS84 polygons.
    Uses spherical polygon quadrature integration to account for latitude convergence.
    """
    if isinstance(geom, MultiPolygon):
        return sum(calculate_geodesic_area_sq_km(p) for p in geom.geoms)

    # Polygon exterior ring coordinates: (lon, lat)
    coords = list(geom.exterior.coords)
    if len(coords) < 3:
        return 0.0

    radius = 6378.137  # WGS84 Earth radius in km
    area = 0.0

    for i in range(len(coords) - 1):
        lon1, lat1 = math.radians(coords[i][0]), math.radians(coords[i][1])
        lon2, lat2 = math.radians(coords[i + 1][0]), math.radians(coords[i + 1][1])
        area += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))

    area = abs(area * radius * radius / 2.0)

    # Subtract interior holes if any
    for interior in geom.interiors:
        hole_coords = list(interior.coords)
        hole_area = 0.0
        for i in range(len(hole_coords) - 1):
            lon1, lat1 = math.radians(hole_coords[i][0]), math.radians(hole_coords[i][1])
            lon2, lat2 = math.radians(hole_coords[i + 1][0]), math.radians(hole_coords[i + 1][1])
            hole_area += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
        area -= abs(hole_area * radius * radius / 2.0)

    return round(max(0.001, area), 2)

def calculate_centroid(geom: Any) -> Tuple[float, float]:
    """
    Returns (latitude, longitude) centroid of the geometry.
    """
    c = geom.centroid
    return round(c.y, 6), round(c.x, 6)

def get_spatial_scale_category(area_sq_km: float) -> str:
    """
    Categorizes the spatial scale of an analysis zone.
    """
    if area_sq_km < 10.0:
        return "Small"
    elif area_sq_km <= 100.0:
        return "Local"
    elif area_sq_km <= 1000.0:
        return "Regional"
    else:
        return "Large Regional"

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two points in km.
    """
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 2)
