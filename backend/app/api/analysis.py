from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.entities import Zone
from ..schemas.schemas import SimulationRequest, SimulationResponse

router = APIRouter(prefix="/analysis", tags=["AI Analysis & Simulation Engine"])

@router.post("/simulation", response_model=SimulationResponse)
def run_simulation(payload: SimulationRequest, db: Session = Depends(get_db)):
    zone = db.query(Zone).filter(Zone.id == payload.zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found.")

    obs = zone.observations[-1] if zone.observations else None
    pred = zone.predictions[-1] if zone.predictions else None
    rec = zone.recommendations[-1] if zone.recommendations else None

    current_health = pred.health_score if pred else 45.0
    current_ndvi = obs.ndvi if obs else 0.35
    current_carbon = rec.est_carbon_offset_tco2e if rec else 20000.0

    # Dynamic What-If Ecological Trajectory
    gain_health = round(
        payload.afforestation_density_pct * 0.22 +
        payload.water_harvesting_units * 0.85 +
        payload.biochar_treatment_pct * 0.15,
        1
    )
    projected_health = min(98.0, current_health + gain_health)
    
    gain_ndvi = round(
        (payload.afforestation_density_pct * 0.0035) + (payload.water_harvesting_units * 0.006),
        3
    )
    projected_ndvi = min(0.92, round(current_ndvi + gain_ndvi, 3))

    extra_carbon = round((payload.afforestation_density_pct / 100.0) * current_carbon * 0.45)
    simulated_carbon = current_carbon + extra_carbon

    cost_estimate = round(
        (payload.afforestation_density_pct * 0.4) +
        (payload.water_harvesting_units * 1.5) +
        (payload.biochar_treatment_pct * 0.25),
        2
    )

    return {
        "zone_id": zone.id,
        "current_health": current_health,
        "projected_health": projected_health,
        "health_gain_pct": gain_health,
        "current_ndvi": current_ndvi,
        "projected_ndvi": projected_ndvi,
        "ndvi_gain": gain_ndvi,
        "current_carbon_tco2e": current_carbon,
        "simulated_total_carbon_tco2e": simulated_carbon,
        "cost_estimate_lakhs": cost_estimate
    }
