import React, { useState } from "react";
import { ChevronDown, ChevronUp, Layers, Info } from "lucide-react";

export const PRIORITY_COLORS = {
  "Critical": { color: "#7c3aed", bg: "#f5f3ff", range: "81–100", label: "Critical" },
  "High": { color: "#ef4444", bg: "#fef2f2", range: "61–80", label: "High" },
  "Moderate": { color: "#f59e0b", bg: "#fffbeb", range: "41–60", label: "Moderate" },
  "Low": { color: "#10b981", bg: "#ecfdf5", range: "21–40", label: "Low" },
  "Very Low": { color: "#059669", bg: "#f0fdf4", range: "0–20", label: "Very Low" },
  "Not Analyzed": { color: "#64748b", bg: "#f8fafc", range: "Pending Phase 3", label: "Not Analyzed" }
};

export default function MapLegend() {
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="gis-map-legend">
      <div className="legend-header" onClick={() => setIsCollapsed(!isCollapsed)}>
        <div className="legend-title-wrap">
          <Layers size={14} className="text-emerald-600" />
          <span className="legend-heading">Restoration Priority Legend</span>
        </div>
        <button className="legend-toggle-btn" aria-label="Toggle Legend">
          {isCollapsed ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {!isCollapsed && (
        <div className="legend-body">
          <div className="legend-items-list">
            {Object.entries(PRIORITY_COLORS).map(([key, item]) => (
              <div key={key} className="legend-item-row">
                <span
                  className="legend-color-box"
                  style={{ backgroundColor: item.color }}
                  title={`${item.label}: ${item.range}`}
                />
                <span className="legend-item-name">{item.label}</span>
                <span className="legend-item-score">({item.range})</span>
              </div>
            ))}
          </div>

          <div className="legend-footer-note">
            <Info size={12} className="inline-icon text-muted" />
            <span>Polygon color represents AI restoration urgency index.</span>
          </div>
        </div>
      )}
    </div>
  );
}
