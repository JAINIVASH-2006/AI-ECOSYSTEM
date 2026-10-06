// Centralized API Service for FastAPI Backend
const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function fetchZones(filters = {}) {
  const params = new URLSearchParams();
  if (filters.region && filters.region !== "All Regions") params.append("region", filters.region);
  if (filters.priority_tier && filters.priority_tier !== "ALL") params.append("priority_tier", filters.priority_tier);
  if (filters.search) params.append("search", filters.search);

  const url = `${API_BASE_URL}/zones${params.toString() ? `?${params.toString()}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch zones from backend API");
  return await res.json();
}

export async function fetchDashboardSummary() {
  const res = await fetch(`${API_BASE_URL}/dashboard/summary`);
  if (!res.ok) throw new Error("Failed to fetch dashboard summary");
  return await res.json();
}

export async function runSimulation(payload) {
  const res = await fetch(`${API_BASE_URL}/analysis/simulation`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to execute What-If simulation");
  return await res.json();
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) throw new Error("Authentication failed");
  return await res.json();
}
