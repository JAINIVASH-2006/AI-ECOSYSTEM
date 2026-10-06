"""
EcoRestore AI — OpenWeather API Integration Service
===================================================
Fetches live real-time meteorological observations (temperature, humidity,
precipitation, wind, weather conditions) for any ecological zone by latitude/longitude.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional
import urllib.request
import json


def get_api_key() -> str:
    """Retrieve the OpenWeather API key from environment variable or default."""
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def fetch_live_weather(
    lat: float,
    lon: float,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch real-time weather observations from OpenWeatherMap API.

    Parameters
    ----------
    lat : float
        Latitude of the target zone.
    lon : float
        Longitude of the target zone.
    api_key : str, optional
        OpenWeather API key (defaults to OPENWEATHER_API_KEY env var).

    Returns
    -------
    dict
        Parsed weather data with temperature, humidity, rainfall, and weather summary.
    """
    key = api_key or get_api_key()
    if not key:
        return {
            "success": False,
            "error": "Missing OpenWeather API Key. Please set OPENWEATHER_API_KEY in your .env file or UI settings.",
            "data": None,
        }

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "EcoRestoreAI/2.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status != 200:
                return {
                    "success": False,
                    "error": f"HTTP Error {response.status}",
                    "data": None,
                }
            payload = json.loads(response.read().decode("utf-8"))

            main = payload.get("main", {})
            weather_desc = payload.get("weather", [{}])[0].get("description", "Unknown").title()
            weather_icon = payload.get("weather", [{}])[0].get("icon", "01d")
            rain = payload.get("rain", {}).get("1h", payload.get("rain", {}).get("3h", 0.0))
            wind = payload.get("wind", {}).get("speed", 0.0)

            return {
                "success": True,
                "data": {
                    "temperature_c": main.get("temp", 25.0),
                    "feels_like_c": main.get("feels_like", 25.0),
                    "humidity_pct": main.get("humidity", 50),
                    "pressure_hpa": main.get("pressure", 1013),
                    "rainfall_mm": float(rain),
                    "wind_speed_ms": float(wind),
                    "weather_description": weather_desc,
                    "weather_icon": weather_icon,
                    "location_name": payload.get("name", "Field Station"),
                    "source": "OpenWeather API (Live)",
                },
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to connect to OpenWeather API: {str(e)}",
            "data": None,
        }
