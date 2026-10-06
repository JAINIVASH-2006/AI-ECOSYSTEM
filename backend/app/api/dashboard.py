from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.entities import Zone, Alert
from ..schemas.schemas import DashboardSummary
from ..services.zone_service import serialize_zone_detail

router = APIRouter(prefix="/dashboard", tags=["Dashboard Aggregations"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    zones = db.query(Zone).all()
    formatted = [serialize_zone_detail(z) for z in zones]

    total_zones = len(formatted)
    if total_zones == 0:
        return {
            "total_zones": 0,
            "total_area_sq_km": 0.0,
            "avg_health_score": 0.0,
            "critical_zones_count": 0,
            "mean_ndvi": 0.0,
            "total_carbon_offset_k_tco2e": 0.0,
            "total_budget_lakhs": 0.0,
            "priority_counts": {},
            "active_alerts": []
        }

    total_area_sq_km = round(sum(z.get("area_sq_km", 0.0) for z in formatted), 2)
    analyzed_zones = [z for z in formatted if z.get("priority_score") is not None]
    avg_health = 50.0  # Baseline
    critical_count = sum(1 for z in formatted if z.get("priority_class") in ["Critical", "High"])
    mean_ndvi = 0.42

    priority_counts = {}
    for z in formatted:
        p_class = z.get("priority_class", "Not Analyzed")
        priority_counts[p_class] = priority_counts.get(p_class, 0) + 1

    alerts = db.query(Alert).filter(Alert.is_acknowledged == False).all()
    active_alerts = [
        {
            "id": a.id,
            "zone_id": a.zone_id,
            "title": a.title,
            "message": a.message,
            "severity": a.severity,
            "timestamp": a.created_at.strftime("%Y-%m-%d %H:%M")
        }
        for a in alerts
    ]

    return {
        "total_zones": total_zones,
        "total_area_sq_km": total_area_sq_km,
        "avg_health_score": avg_health,
        "critical_zones_count": critical_count,
        "mean_ndvi": mean_ndvi,
        "total_carbon_offset_k_tco2e": 125.0,
        "total_budget_lakhs": 180.5,
        "priority_counts": priority_counts,
        "active_alerts": active_alerts
    }
