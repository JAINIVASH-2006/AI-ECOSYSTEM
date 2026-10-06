import React from "react";
import { Sparkles, MapPin, ArrowUpRight } from "lucide-react";
import { PRIORITY_TIERS } from "../data/zonesData";

export default function ZonesTable({ zones = [], selectedZone = null, onSelectZone = () => {} }) {
  return (
    <div className="table-wrapper-card">
      <div className="table-header-row">
        <div>
          <h3 className="table-title">Ecological Zones Priority Registry</h3>
          <p className="table-subtitle">Showing {zones.length} monitored spatial zones across selected region</p>
        </div>
      </div>

      <div className="table-container">
        <table className="zones-data-table">
          <thead>
            <tr>
              <th>Zone / Location</th>
              <th>Priority Tier</th>
              <th>Health</th>
              <th>NDVI</th>
              <th>Area (Ha)</th>
              <th>Top Ecological Threat</th>
              <th>Recommended Intervention</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {zones.map((zone) => {
              const tier = PRIORITY_TIERS[zone.priorityTier] || PRIORITY_TIERS.MODERATE;
              const isSelected = selectedZone?.id === zone.id;

              return (
                <tr
                  key={zone.id}
                  className={`table-row ${isSelected ? "selected" : ""}`}
                  onClick={() => onSelectZone(zone)}
                >
                  <td className="cell-zone-name">
                    <b>{zone.name}</b>
                    <span className="cell-sub">{zone.region}</span>
                  </td>
                  <td>
                    <span
                      className="table-tier-badge"
                      style={{ background: tier.bg, color: tier.color, borderColor: tier.border }}
                    >
                      {tier.label} ({zone.priorityScore})
                    </span>
                  </td>
                  <td>
                    <div className="health-bar-cell">
                      <span>{zone.healthScore}%</span>
                      <div className="micro-bar-track">
                        <div
                          className="micro-bar-fill"
                          style={{
                            width: `${zone.healthScore}%`,
                            backgroundColor: zone.healthScore < 40 ? "#ef4444" : zone.healthScore < 70 ? "#f59e0b" : "#10b981"
                          }}
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="font-green font-bold">{zone.ndvi}</span>
                  </td>
                  <td>{zone.areaHa.toLocaleString()}</td>
                  <td>
                    <span className="cell-threat-text">{zone.primaryThreat}</span>
                  </td>
                  <td>
                    <span className="cell-intervention-text">{zone.recommendedIntervention}</span>
                  </td>
                  <td>
                    <button
                      className="btn-table-view"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectZone(zone);
                      }}
                    >
                      <span>Inspect</span>
                      <ArrowUpRight size={13} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
