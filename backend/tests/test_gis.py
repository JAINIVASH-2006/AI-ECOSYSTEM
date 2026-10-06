import pytest
from shapely.geometry import Polygon
from app.gis.geometry import (
    validate_geojson_geometry,
    calculate_geodesic_area_sq_km,
    calculate_centroid,
    get_spatial_scale_category,
    haversine_distance_km
)
from app.gis.spatial_queries import point_in_zone

def test_valid_polygon_geometry():
    valid_poly = {
        "type": "Polygon",
        "coordinates": [[[78.0, 10.0], [78.1, 10.0], [78.1, 10.1], [78.0, 10.1], [78.0, 10.0]]]
    }
    is_valid, err, geom = validate_geojson_geometry(valid_poly)
    assert is_valid is True
    assert err is None
    assert geom is not None

def test_invalid_polygon_self_intersection():
    # Self-intersecting bow-tie polygon
    invalid_poly = {
        "type": "Polygon",
        "coordinates": [[[0.0, 0.0], [2.0, 2.0], [0.0, 2.0], [2.0, 0.0], [0.0, 0.0]]]
    }
    is_valid, err, geom = validate_geojson_geometry(invalid_poly)
    assert is_valid is False
    assert "Invalid polygon topology" in err

def test_invalid_coordinates_out_of_bounds():
    out_of_bounds = {
        "type": "Polygon",
        "coordinates": [[[190.0, 0.0], [191.0, 0.0], [191.0, 1.0], [190.0, 1.0], [190.0, 0.0]]]
    }
    is_valid, err, geom = validate_geojson_geometry(out_of_bounds)
    assert is_valid is False
    assert "Coordinates out of bounds" in err

def test_geodesic_area_calculation():
    # ~0.1 deg x 0.1 deg square near equator ~ 123 km²
    poly_geom = Polygon([[78.0, 10.0], [78.1, 10.0], [78.1, 10.1], [78.0, 10.1], [78.0, 10.0]])
    area = calculate_geodesic_area_sq_km(poly_geom)
    assert 115.0 < area < 130.0

def test_centroid_calculation():
    poly_geom = Polygon([[78.0, 10.0], [78.2, 10.0], [78.2, 10.2], [78.0, 10.2], [78.0, 10.0]])
    lat, lon = calculate_centroid(poly_geom)
    assert round(lat, 1) == 10.1
    assert round(lon, 1) == 78.1

def test_spatial_scale_categories():
    assert get_spatial_scale_category(5.0) == "Small"
    assert get_spatial_scale_category(50.0) == "Local"
    assert get_spatial_scale_category(500.0) == "Regional"
    assert get_spatial_scale_category(1500.0) == "Large Regional"

def test_haversine_distance():
    # Distance between Chennai (13.0827, 80.2707) and Bangalore (12.9716, 77.5946) ~ 290 km
    dist = haversine_distance_km(13.0827, 80.2707, 12.9716, 77.5946)
    assert 280.0 < dist < 305.0

def test_point_in_zone_containment():
    poly_dict = {
        "type": "Polygon",
        "coordinates": [[[78.0, 10.0], [78.2, 10.0], [78.2, 10.2], [78.0, 10.2], [78.0, 10.0]]]
    }
    assert point_in_zone(10.1, 78.1, poly_dict) is True
    assert point_in_zone(11.0, 78.1, poly_dict) is False
