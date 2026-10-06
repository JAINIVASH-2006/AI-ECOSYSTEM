import os
from pathlib import Path
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "EcoRestore AI — Decision Support Backend"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Security & Auth
    SECRET_KEY: str = "ecorestore-super-secret-jwt-token-key-2026-secure"
    JWT_SECRET: str = "ecorestore-super-secret-jwt-token-key-2026-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days
    
    # Database
    DATABASE_URL: str = f"sqlite:///{PROJECT_ROOT}/ecorestore_v2.db"
    
    # External API Keys (Kept strictly on backend)
    OPENWEATHER_API_KEY: str = "e3e0e3948173f1b079e09f66e9f16b36"
    NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    SOILGRIDS_BASE_URL: str = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    GBIF_BASE_URL: str = "https://api.gbif.org/v1/occurrence/search"
    
    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]

    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
