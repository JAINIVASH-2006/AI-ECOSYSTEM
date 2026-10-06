import React from "react";
import { Trees, Sparkles, SlidersHorizontal, FileSpreadsheet, ShieldAlert } from "lucide-react";
import { REGIONS, PRIORITY_TIERS } from "../data/zonesData";

export default function Navbar({
  selectedRegion,
  setSelectedRegion,
  selectedTier,
  setSelectedTier,
  searchQuery,
  setSearchQuery,
  onOpenReport,
  onRunDiagnostics
}) {
  return (
    <header className="navbar-container">
      <div className="navbar-top">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <Trees className="icon-main" />
          </div>
          <div>
            <div className="brand-title-row">
              <h1 className="brand-title">EcoRestore AI</h1>
              <span className="badge-live">
                <span className="pulse-dot"></span> AI Engine v2.4 Active
              </span>
              <span className="badge-satellite">Sentinel-2 & Landsat Data</span>
            </div>
            <p className="brand-subtitle">
              AI-Powered Ecological Restoration Priority Mapping & Spatial Decision Support System
            </p>
          </div>
        </div>

        <div className="navbar-actions">
          <button className="btn btn-outline" onClick={onRunDiagnostics}>
            <Sparkles size={16} />
            <span>AI Quick Diagnostic</span>
          </button>
          <button className="btn btn-primary" onClick={onOpenReport}>
            <FileSpreadsheet size={16} />
            <span>Generate Action Plan</span>
          </button>
        </div>
      </div>

      <div className="navbar-filter-bar">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search zones, riverbeds, coordinates, species..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-search"
          />
        </div>

        <div className="filter-group">
          <label className="filter-label">
            <SlidersHorizontal size={14} /> Region:
          </label>
          <select
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
            className="select-custom"
          >
            {REGIONS.map((reg) => (
              <option key={reg} value={reg}>
                {reg}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">
            <ShieldAlert size={14} /> Priority:
          </label>
          <select
            value={selectedTier}
            onChange={(e) => setSelectedTier(e.target.value)}
            className="select-custom"
          >
            <option value="ALL">All Tiers (0 - 100)</option>
            {Object.entries(PRIORITY_TIERS).map(([key, tier]) => (
              <option key={key} value={key}>
                {tier.label} ({tier.min}-{tier.max})
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
}
