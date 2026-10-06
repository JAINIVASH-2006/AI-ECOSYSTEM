import React from "react";
import {
  X,
  MapPin,
  Sparkles,
  Layers,
  Activity,
  AlertTriangle,
  Clock,
  ShieldCheck,
  Compass,
  CheckCircle2,
  Trash2,
  Edit3
} from "lucide-react";
import { PRIORITY_COLORS } from "./MapLegend";

export default function ZoneDetailsPanel({ zone, onClose, onAnalyze, onDelete }) {
  if (!zone) return null;

  const pClass = zone.priority_class || "Not Analyzed";
  const tier = PRIORITY_COLORS[pClass] || PRIORITY_COLORS["Not Analyzed"];
  const isAnalyzed = zone.analysis_status === "ANALYZED";

  return (
    <div className="gis-zone-detail-panel">
      {/* Header */}
      <div className="panel-top-header">
        <div>
          <div className="flex-align-gap">
            <span
              className="tier-badge-pill"
              style={{ backgroundColor: tier.bg, color: tier.color, borderColor: tier.color }}
            >
              {tier.label} {zone.priority_score !== null && `(${zone.priority_score}/100)`}
            </span>
            <span className="scale-badge-pill">{zone.analysis_scale || "Local"} Scale</span>
          </div>
          <h2 className="panel-zone-title">{zone.name}</h2>
          <p className="panel-zone-code">{zone.zone_code} • {zone.district || zone.region}, {zone.state || "India"}</p>
        </div>

        <button className="panel-close-btn" onClick={onClose} aria-label="Close details">
          <X size={18} />
        </button>
      </div>

      <div className="panel-scroll-content">
        {/* Spatial Geometrics Card */}
        <div className="gis-meta-card">
          <h4 className="meta-card-title">
            <Compass size={15} className="text-emerald-600" />
            <span>Spatial & Geodesic Attributes</span>
          </h4>
          <div className="meta-stats-grid">
            <div className="meta-box">
              <span className="mb-label">Calculated Area</span>
              <span className="mb-val">{zone.area_sq_km} km²</span>
            </div>
            <div className="meta-box">
              <span className="mb-label">Spatial Scale</span>
              <span className="mb-val">{zone.analysis_scale}</span>
            </div>
            <div className="meta-box">
              <span className="mb-label">Centroid Latitude</span>
              <span className="mb-val">{zone.centroid?.latitude?.toFixed(5) || zone.centroid_lat?.toFixed(5) || "N/A"}° N</span>
            </div>
            <div className="meta-box">
              <span className="mb-label">Centroid Longitude</span>
              <span className="mb-val">{zone.centroid?.longitude?.toFixed(5) || zone.centroid_lon?.toFixed(5) || "N/A"}° E</span>
            </div>
          </div>
        </div>

        {/* Environmental Analysis Status Card */}
        <div className="gis-analysis-status-card">
          <div className="flex-between mb-2">
            <h4 className="meta-card-title">
              <Activity size={15} className="text-emerald-600" />
              <span>Environmental Telemetry Status</span>
            </h4>
            <span className={`status-pill ${isAnalyzed ? "status-live" : "status-pending"}`}>
              {isAnalyzed ? "Analyzed" : "Not Synchronized"}
            </span>
          </div>

          <p className="status-explainer">
            {isAnalyzed
              ? "Environmental indicators (NDVI, soil condition, water stress, human pressure) are active."
              : "Real environmental indicators (Sentinel-2 NDVI, NASA POWER rainfall, SoilGrids, GBIF) will be fetched during Phase 3 analysis."}
          </p>

          <div className="data-readiness-checklist">
            <div className="checklist-item">
              <span className="cl-label">🛰️ Sentinel-2 Satellite Vegetation</span>
              <span className="cl-status text-muted">{isAnalyzed ? "Available" : "Not checked"}</span>
            </div>
            <div className="checklist-item">
              <span className="cl-label">🌧️ NASA POWER Climate & Rainfall</span>
              <span className="cl-status text-muted">{isAnalyzed ? "Available" : "Not checked"}</span>
            </div>
            <div className="checklist-item">
              <span className="cl-label">🌱 SoilGrids Carbon & Condition</span>
              <span className="cl-status text-muted">{isAnalyzed ? "Available" : "Not checked"}</span>
            </div>
            <div className="checklist-item">
              <span className="cl-label">🐾 GBIF Biodiversity Records</span>
              <span className="cl-status text-muted">{isAnalyzed ? "Available" : "Not checked"}</span>
            </div>
          </div>
        </div>

        {/* GIS Audit & Provenance */}
        <div className="gis-audit-card">
          <h4 className="meta-card-title">
            <ShieldCheck size={15} className="text-emerald-600" />
            <span>GIS Provenance & Audit Metadata</span>
          </h4>
          <div className="audit-rows">
            <div className="audit-row">
              <span className="a-lbl">Geometry Source:</span>
              <span className="a-val">{zone.geometry_source || "EcoRestore GIS Engine"}</span>
            </div>
            <div className="audit-row">
              <span className="a-lbl">Created By:</span>
              <span className="a-val">{zone.created_by || "System"}</span>
            </div>
            <div className="audit-row">
              <span className="a-lbl">Created Timestamp:</span>
              <span className="a-val">{zone.created_at || "2026-10-06"}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="panel-footer-actions">
        {onDelete && (
          <button
            className="btn-action-delete"
            onClick={() => onDelete(zone.id)}
            title="Delete this zone"
          >
            <Trash2 size={15} />
          </button>
        )}
        <button
          className="btn-action-primary"
          onClick={() => onAnalyze(zone)}
        >
          <Sparkles size={16} />
          <span>Analyze Environment (Phase 3 Ready)</span>
        </button>
      </div>
    </div>
  );
}
