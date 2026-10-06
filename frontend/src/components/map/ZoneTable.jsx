import React, { useState, useMemo } from "react";
import { Filter, ArrowUpRight, Trash2, Search, SlidersHorizontal, ShieldCheck } from "lucide-react";
import { PRIORITY_COLORS } from "./MapLegend";

export default function ZoneTable({
  zones = [],
  selectedZone = null,
  onSelectZone = () => {},
  onDeleteZone = () => {},
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [priorityFilter, setPriorityFilter] = useState("ALL");

  const filteredList = useMemo(() => {
    return zones.filter((z) => {
      const p = z.properties || z;
      const matchSearch =
        !searchTerm ||
        p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.zone_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.region?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.district?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchStatus =
        statusFilter === "ALL" || p.analysis_status === statusFilter;

      const matchPriority =
        priorityFilter === "ALL" || p.priority_class === priorityFilter;

      return matchSearch && matchStatus && matchPriority;
    });
  }, [zones, searchTerm, statusFilter, priorityFilter]);

  return (
    <div className="gis-table-card">
      <div className="gis-table-header-bar">
        <div>
          <h3 className="gis-table-title">Restoration Study Areas Registry</h3>
          <p className="gis-table-subtitle">
            Synchronized PostGIS Spatial Database • {filteredList.length} of {zones.length} Zones Displayed
          </p>
        </div>

        <div className="gis-table-filters">
          <div className="search-field-wrapper">
            <Search size={14} className="search-icon-sm" />
            <input
              type="text"
              placeholder="Filter by name, code, district..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="table-search-input"
            />
          </div>

          <div className="filter-select-wrap">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="table-filter-select"
            >
              <option value="ALL">All Analysis Status</option>
              <option value="ANALYZED">Analyzed</option>
              <option value="NOT_ANALYZED">Not Analyzed</option>
            </select>
          </div>

          <div className="filter-select-wrap">
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="table-filter-select"
            >
              <option value="ALL">All Priority Tiers</option>
              <option value="Critical">Critical (81–100)</option>
              <option value="High">High (61–80)</option>
              <option value="Moderate">Moderate (41–60)</option>
              <option value="Low">Low (21–40)</option>
              <option value="Not Analyzed">Not Analyzed</option>
            </select>
          </div>
        </div>
      </div>

      <div className="gis-table-scroll-container">
        <table className="gis-data-table">
          <thead>
            <tr>
              <th>Zone Code</th>
              <th>Study Area Name</th>
              <th>Location / District</th>
              <th>Area (km²)</th>
              <th>Scale</th>
              <th>Priority Class</th>
              <th>Analysis Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredList.length === 0 ? (
              <tr>
                <td colSpan="8" className="empty-table-cell">
                  No spatial study areas match your filter criteria.
                </td>
              </tr>
            ) : (
              filteredList.map((feature) => {
                const p = feature.properties || feature;
                const isSelected = selectedZone && selectedZone.id === p.id;
                const pClass = p.priority_class || "Not Analyzed";
                const tier = PRIORITY_COLORS[pClass] || PRIORITY_COLORS["Not Analyzed"];

                return (
                  <tr
                    key={p.id || p.zone_code}
                    className={`gis-table-row ${isSelected ? "selected-row" : ""}`}
                    onClick={() => onSelectZone(p, feature.geometry)}
                  >
                    <td className="font-bold text-emerald-800">{p.zone_code}</td>
                    <td>
                      <b>{p.name}</b>
                    </td>
                    <td>
                      <span className="text-secondary">{p.district ? `${p.district}, ` : ""}{p.state || p.region}</span>
                    </td>
                    <td>{p.area_sq_km} km²</td>
                    <td>
                      <span className="scale-tag">{p.analysis_scale || "Local"}</span>
                    </td>
                    <td>
                      <span
                        className="table-tier-pill"
                        style={{ backgroundColor: tier.bg, color: tier.color, borderColor: tier.color }}
                      >
                        {tier.label} {p.priority_score !== null && `(${p.priority_score})`}
                      </span>
                    </td>
                    <td>
                      <span className={`status-badge-sm ${p.analysis_status === "ANALYZED" ? "analyzed" : "pending"}`}>
                        {p.analysis_status === "ANALYZED" ? "Analyzed" : "Not Synchronized"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn-table-inspect"
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectZone(p, feature.geometry);
                        }}
                      >
                        <span>Focus</span>
                        <ArrowUpRight size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
