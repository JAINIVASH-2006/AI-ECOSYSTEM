import React from "react";
import { Sparkles, Eye, MapPin, AlertCircle, Compass } from "lucide-react";
import { PRIORITY_COLORS } from "./MapLegend";

export default function ZonePopup({ properties, onInspect, onAnalyze }) {
  const pClass = properties.priority_class || "Not Analyzed";
  const tier = PRIORITY_COLORS[pClass] || PRIORITY_COLORS["Not Analyzed"];
  const isAnalyzed = properties.analysis_status === "ANALYZED";

  return (
    <div className="gis-zone-popup-card">
      <div className="popup-top-bar">
        <span
          className="popup-badge"
          style={{ backgroundColor: tier.bg, color: tier.color, borderColor: tier.color }}
        >
          {tier.label} {properties.priority_score !== null && `(${properties.priority_score})`}
        </span>
        <span className="popup-scale-tag">{properties.analysis_scale || "Local"}</span>
      </div>

      <h4 className="popup-zone-code">{properties.zone_code}</h4>
      <p className="popup-zone-name">{properties.name}</p>

      <div className="popup-meta-grid">
        <div className="popup-meta-box">
          <span className="meta-lbl">Area</span>
          <span className="meta-val">{properties.area_sq_km} km²</span>
        </div>
        <div className="popup-meta-box">
          <span className="meta-lbl">Region</span>
          <span className="meta-val">{properties.district || properties.region}</span>
        </div>
      </div>

      <div className="popup-status-box">
        <span className="status-title">Status:</span>
        <span className={`status-val ${isAnalyzed ? "text-emerald-700" : "text-amber-700"}`}>
          {isAnalyzed ? "AI Restoration Telemetry Active" : "Environmental Data Not Yet Synchronized"}
        </span>
      </div>

      <div className="popup-actions-grid">
        <button
          className="btn-popup-secondary"
          onClick={() => onInspect(properties)}
        >
          <Eye size={13} />
          <span>View Zone</span>
        </button>
        <button
          className="btn-popup-primary"
          onClick={() => onAnalyze(properties)}
        >
          <Sparkles size={13} />
          <span>Analyze Zone</span>
        </button>
      </div>
    </div>
  );
}
