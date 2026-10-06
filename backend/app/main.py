from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import Base, engine, SessionLocal
from .models.entities import Zone, EnvironmentalObservation, PriorityPrediction, InterventionRecommendation, Alert
from .api import auth, zones, analysis, dashboard
from .gis.geometry import calculate_geodesic_area_sq_km, calculate_centroid, get_spatial_scale_category, shape

# Initialize Database Schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Professional AI + GIS Ecological Restoration Decision-Support Platform REST API."
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(zones.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

# --- Initial Seed Spatial Study Areas with Real GeoJSON Polygons ---
SEED_STUDY_AREAS = [
    {
        "zone_code": "ZONE-001",
        "name": "Cauvery Riverbed Delta Riparian Study Area",
        "region": "Cauvery Basin & Tamil Nadu",
        "district": "Thanjavur / Karur",
        "state": "Tamil Nadu",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [78.020, 10.920],
                [78.130, 10.920],
                [78.140, 11.000],
                [78.030, 11.010],
                [78.020, 10.920]
            ]]
        },
        "priority_score": 88.0,
        "priority_class": "Critical",
        "analysis_status": "ANALYZED"
    },
    {
        "zone_code": "ZONE-002",
        "name": "Agasthyamalai Rainforest Fringe Reserve",
        "region": "Western Ghats Biodiversity Hotspot",
        "district": "Tirunelveli",
        "state": "Tamil Nadu",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [77.200, 8.560],
                [77.290, 8.570],
                [77.300, 8.680],
                [77.210, 8.670],
                [77.200, 8.560]
            ]]
        },
        "priority_score": 76.0,
        "priority_class": "High",
        "analysis_status": "ANALYZED"
    },
    {
        "zone_code": "ZONE-003",
        "name": "Nilgiris Shola-Grassland Mosaic Study Zone",
        "region": "Nilgiris Biosphere Reserve",
        "district": "Nilgiris",
        "state": "Tamil Nadu",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [76.640, 11.360],
                [76.750, 11.370],
                [76.760, 11.460],
                [76.650, 11.450],
                [76.640, 11.360]
            ]]
        },
        "priority_score": 84.0,
        "priority_class": "Critical",
        "analysis_status": "ANALYZED"
    },
    {
        "zone_code": "ZONE-004",
        "name": "Rayalaseema Semi-Arid Watershed Basin",
        "region": "Deccan Plateau Drylands",
        "district": "Anantapur",
        "state": "Andhra Pradesh",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [77.520, 14.610],
                [77.680, 14.620],
                [77.690, 14.750],
                [77.530, 14.740],
                [77.520, 14.610]
            ]]
        },
        "priority_score": 92.0,
        "priority_class": "Critical",
        "analysis_status": "ANALYZED"
    },
    {
        "zone_code": "ZONE-005",
        "name": "Perambalur Dryland Ecological Corridor",
        "region": "Cauvery Basin & Tamil Nadu",
        "district": "Perambalur",
        "state": "Tamil Nadu",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [78.820, 11.180],
                [78.920, 11.190],
                [78.930, 11.270],
                [78.830, 11.260],
                [78.820, 11.180]
            ]]
        },
        "priority_score": None,
        "priority_class": "Not Analyzed",
        "analysis_status": "NOT_ANALYZED"
    },
    {
        "zone_code": "ZONE-006",
        "name": "Shevaroy Slopes Deciduous Zone",
        "region": "Eastern Ghats Escarpment",
        "district": "Salem",
        "state": "Tamil Nadu",
        "country": "India",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [78.160, 11.780],
                [78.270, 11.790],
                [78.280, 11.890],
                [78.170, 11.880],
                [78.160, 11.780]
            ]]
        },
        "priority_score": 68.0,
        "priority_class": "High",
        "analysis_status": "ANALYZED"
    }
]

@app.on_event("startup")
def seed_spatial_database():
    db = SessionLocal()
    try:
        # Clear & re-seed if schema upgraded
        existing_count = db.query(Zone).count()
        if existing_count < len(SEED_STUDY_AREAS):
            # Clean re-seed
            db.query(Zone).delete()
            db.commit()

            for item in SEED_STUDY_AREAS:
                geom_obj = shape(item["geometry"])
                area_sq_km = calculate_geodesic_area_sq_km(geom_obj)
                c_lat, c_lon = calculate_centroid(geom_obj)
                scale = get_spatial_scale_category(area_sq_km)

                zone = Zone(
                    zone_code=item["zone_code"],
                    name=item["name"],
                    region=item["region"],
                    district=item["district"],
                    state=item["state"],
                    country=item["country"],
                    geometry_json=item["geometry"],
                    centroid_lat=c_lat,
                    centroid_lon=c_lon,
                    area_sq_km=area_sq_km,
                    analysis_scale=scale,
                    priority_score=item["priority_score"],
                    priority_class=item["priority_class"],
                    analysis_status=item["analysis_status"],
                    created_by="GIS Engine Seeder",
                    geometry_source="Survey of India / OpenStreetMap",
                    geometry_version="1.0"
                )
                db.add(zone)
            db.commit()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "system": "EcoRestore AI Decision Support System",
        "status": "Online",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }
