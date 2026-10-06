import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from ..core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="ENVIRONMENTAL_ANALYST") # ADMIN, ENVIRONMENTAL_ANALYST, PROJECT_MANAGER, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    district = Column(String(255), nullable=True)
    state = Column(String(255), nullable=True)
    country = Column(String(100), default="India")
    
    # PostGIS GeoJSON Polygon Geometry & Spatial Centroid
    geometry_json = Column(JSON, nullable=True)
    centroid_lat = Column(Float, nullable=False)
    centroid_lon = Column(Float, nullable=False)
    
    # Area & Spatial Scale
    area_sq_km = Column(Float, default=10.0)
    analysis_scale = Column(String(50), default="Local") # Small, Local, Regional, Large Regional
    
    # Restoration Priority Status
    priority_score = Column(Float, nullable=True) # None if Not Analyzed
    priority_class = Column(String(50), default="Not Analyzed") # Very Low, Low, Moderate, High, Critical, Not Analyzed
    analysis_status = Column(String(50), default="NOT_ANALYZED") # NOT_ANALYZED, PENDING, ANALYZED
    
    # GIS Audit Metadata
    created_by = Column(String(100), default="system")
    geometry_source = Column(String(100), default="EcoRestore GIS Engine")
    geometry_version = Column(String(50), default="1.0")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    observations = relationship("EnvironmentalObservation", back_populates="zone", cascade="all, delete-orphan")
    predictions = relationship("PriorityPrediction", back_populates="zone", cascade="all, delete-orphan")
    recommendations = relationship("InterventionRecommendation", back_populates="zone", cascade="all, delete-orphan")
    projects = relationship("RestorationProject", back_populates="zone", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="zone", cascade="all, delete-orphan")

class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    observation_date = Column(DateTime, default=datetime.datetime.utcnow)
    data_type = Column(String(50), default="OBSERVED") # OBSERVED, DERIVED, MODEL_PREDICTED, SIMULATED
    
    # Key Scientific Metrics
    ndvi = Column(Float, nullable=False) # 0 to 1
    soil_organic_carbon = Column(Float, nullable=False) # %
    soil_moisture = Column(Float, nullable=False) # %
    annual_rainfall_mm = Column(Float, nullable=False)
    biodiversity_index = Column(Float, nullable=False) # 0 to 100
    human_pressure_index = Column(Float, nullable=False) # 0 to 100
    erosion_hazard = Column(String(100), default="Moderate")
    primary_threat = Column(String(255), default="Vegetation Loss")
    threats_json = Column(JSON, default=list)
    data_confidence_score = Column(Float, default=85.0)

    zone = relationship("Zone", back_populates="observations")

class PriorityPrediction(Base):
    __tablename__ = "priority_predictions"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    priority_score = Column(Float, nullable=False) # 0 to 100
    priority_tier = Column(String(50), nullable=False) # CRITICAL, HIGH, MODERATE, LOW, VERY_LOW
    health_score = Column(Float, nullable=False) # 0 to 100
    opportunity_score = Column(Float, default=65.0) # 0 to 100
    shap_contributions = Column(JSON, default=dict)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow)

    zone = relationship("Zone", back_populates="predictions")

class InterventionRecommendation(Base):
    __tablename__ = "intervention_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    primary_intervention = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    suitability_score = Column(Float, default=85.0)
    recommended_species = Column(JSON, default=list)
    est_cost_lakhs = Column(Float, default=25.0)
    est_carbon_offset_tco2e = Column(Float, default=15000.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    zone = relationship("Zone", back_populates="recommendations")

class RestorationProject(Base):
    __tablename__ = "restoration_projects"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="IN_PROGRESS") # PROPOSED, APPROVED, IN_PROGRESS, COMPLETED
    manager_name = Column(String(255), default="Project Team")
    budget_lakhs = Column(Float, default=20.0)
    progress_pct = Column(Float, default=35.0)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    target_completion = Column(DateTime, nullable=True)

    zone = relationship("Zone", back_populates="projects")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="HIGH") # CRITICAL, HIGH, MODERATE, LOW
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    zone = relationship("Zone", back_populates="alerts")
