import axios from "axios";

const API_BASE = "http://127.0.0.1:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

/**
 * Fetch all zones as GeoJSON FeatureCollection
 */
export async function getZones(filters = {}) {
  const params = {};
  if (filters.priority_class && filters.priority_class !== "ALL") {
    params.priority_class = filters.priority_class;
  }
  if (filters.analysis_status && filters.analysis_status !== "ALL") {
    params.analysis_status = filters.analysis_status;
  }

  const response = await apiClient.get("/zones", { params });
  return response.data;
}

/**
 * Fetch a single zone with full spatial and analysis metadata
 */
export async function getZone(id) {
  const response = await apiClient.get(`/zones/${id}`);
  return response.data;
}

/**
 * Create a new restoration study zone with GeoJSON Polygon
 */
export async function createZone(data) {
  const response = await apiClient.post("/zones", data);
  return response.data;
}

/**
 * Update zone metadata
 */
export async function updateZone(id, data) {
  const response = await apiClient.put(`/zones/${id}`, data);
  return response.data;
}

/**
 * Delete a zone
 */
export async function deleteZone(id) {
  const response = await apiClient.delete(`/zones/${id}`);
  return response.data;
}

/**
 * Find zones within radius from coordinate
 */
export async function getNearbyZones(lat, lon, radiusKm = 50) {
  const response = await apiClient.get("/zones/nearby", {
    params: { lat, lon, radius_km: radiusKm },
  });
  return response.data;
}

/**
 * Check point-in-polygon containment
 */
export async function findZoneForPoint(lat, lon) {
  const response = await apiClient.post("/zones/contains-point", {
    latitude: lat,
    longitude: lon,
  });
  return response.data;
}

/**
 * OpenStreetMap Nominatim Geocoder Search (with debouncing & rate-limiting)
 */
let lastGeocodeTime = 0;
export async function searchLocation(query) {
  if (!query || query.trim().length < 2) return [];

  // Enforce 1s debounce rate-limit for Nominatim usage policy
  const now = Date.now();
  if (now - lastGeocodeTime < 600) {
    await new Promise((resolve) => setTimeout(resolve, 600 - (now - lastGeocodeTime)));
  }
  lastGeocodeTime = Date.now();

  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`;
    const res = await axios.get(url, {
      headers: { "Accept-Language": "en" },
      timeout: 5000,
    });
    return res.data.map((item) => ({
      place_id: item.place_id,
      display_name: item.display_name,
      lat: parseFloat(item.lat),
      lon: parseFloat(item.lon),
      type: item.type,
      boundingbox: item.boundingbox,
    }));
  } catch (error) {
    console.warn("Geocoding lookup failed:", error);
    return [];
  }
}
