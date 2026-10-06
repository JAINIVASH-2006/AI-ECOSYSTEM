import React from "react";
import { X, Printer, Download, Sparkles, CheckCircle2, ShieldAlert } from "lucide-react";
import { PRIORITY_TIERS } from "../data/zonesData";

export default function ActionPlanModal({ isOpen, onClose, zones, stats }) {
  if (!isOpen) return null;

  const criticalZones = zones.filter((z) => z.priorityTier === "CRITICAL");

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="flex-center-gap">
              <span className="badge-live">
                <Sparkles size={13} /> AI Executive Brief
              </span>
              <span className="badge-satellite">Generated on {new Date().toLocaleDateString()}</span>
            </div>
            <h2 className="modal-title">EcoRestore AI — Strategic Restoration Action Plan</h2>
          </div>
          <button className="btn-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Executive Summary */}
          <div className="report-section">
            <h4 className="section-heading">1. Executive Summary & Landscape Health</h4>
            <p className="section-p">
              The EcoRestore AI spatial optimization engine analyzed <b>{stats.totalHa.toLocaleString()} hectares</b> across{" "}
              <b>{zones.length} priority ecological zones</b>. The average landscape health index is currently{" "}
              <b>{stats.avgHealth}%</b> with a mean vegetation canopy NDVI of <b>{stats.avgNdvi}</b>. Immediate intervention
              is required for <b>{criticalZones.length} critical high-degradation hotspots</b> to prevent irreversible topsoil loss
              and biodiversity collapse.
            </p>

            <div className="report-kpi-row">
              <div className="rep-kpi">
                <span className="rep-kpi-label">Monitored Zones</span>
                <span className="rep-kpi-val">{zones.length} Sites</span>
              </div>
              <div className="rep-kpi">
                <span className="rep-kpi-label">Immediate Critical Sites</span>
                <span className="rep-kpi-val text-rose">{criticalZones.length} Hotspots</span>
              </div>
              <div className="rep-kpi">
                <span className="rep-kpi-label">5-Yr Carbon Offset</span>
                <span className="rep-kpi-val text-purple">{(stats.totalCarbon / 1000).toFixed(1)}k tCO₂e</span>
              </div>
              <div className="rep-kpi">
                <span className="rep-kpi-label">Total Est. Budget</span>
                <span className="rep-kpi-val text-emerald">₹{stats.totalCost} Lakhs</span>
              </div>
            </div>
          </div>

          {/* Phase 1 Priority Actions */}
          <div className="report-section">
            <h4 className="section-heading">2. Phase-1 Urgent Intervention Targets (Months 1–6)</h4>
            <div className="report-zones-list">
              {criticalZones.map((zone) => (
                <div key={zone.id} className="report-zone-item">
                  <div className="rep-zone-top">
                    <div>
                      <b className="rep-zone-name">{zone.name}</b>
                      <span className="rep-zone-region"> ({zone.region})</span>
                    </div>
                    <span className="tag-danger">Priority Score: {zone.priorityScore}/100</span>
                  </div>
                  <p className="rep-zone-strategy">
                    <b>Action Plan:</b> {zone.interventionDetails}
                  </p>
                  <div className="rep-species-tags">
                    <span className="sp-header">Target Flora:</span>
                    {zone.recommendedSpecies.slice(0, 3).map((s, i) => (
                      <span key={i} className="sp-pill">{s.name}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Environmental Impact Metrics */}
          <div className="report-section">
            <h4 className="section-heading">3. Projected Ecological Returns (5-Year Horizon)</h4>
            <ul className="report-bullets">
              <li>
                <CheckCircle2 size={16} className="text-emerald inline-icon" />
                <b>Soil Stabilisation:</b> 72% estimated reduction in surface runoff velocity and topsoil erosion.
              </li>
              <li>
                <CheckCircle2 size={16} className="text-emerald inline-icon" />
                <b>Groundwater Recharge:</b> Estimated 28% increase in aquifer percolation across micro-watersheds.
              </li>
              <li>
                <CheckCircle2 size={16} className="text-emerald inline-icon" />
                <b>Carbon Sequestration:</b> Net projected capture of ~{stats.totalCarbon.toLocaleString()} tonnes of CO₂ equivalent.
              </li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-outline" onClick={() => window.print()}>
            <Printer size={16} />
            <span>Print Report</span>
          </button>
          <button className="btn btn-primary" onClick={onClose}>
            <Download size={16} />
            <span>Done</span>
          </button>
        </div>
      </div>
    </div>
  );
}
