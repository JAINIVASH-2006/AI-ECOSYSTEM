import React, { useState } from "react";
import {
  X,
  Activity,
  Trees,
  Sliders,
  CloudSun,
  ShieldAlert,
  Droplets,
  Sprout,
  TrendingUp,
  MapPin,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { PRIORITY_TIERS } from "../data/zonesData";

export default function ZoneDetailsPanel({ zone, onClose }) {
  const [activeTab, setActiveTab] = useState("diagnostics");

  // Simulation Sliders State
  const [afforestationDensity, setAfforestationDensity] = useState(65); // %
  const [waterHarvestingUnits, setWaterHarvestingUnits] = useState(12); // units
  const [biocharTreatment, setBiocharTreatment] = useState(40); // %

  if (!zone) return null;

  const tier = PRIORITY_TIERS[zone.priorityTier] || PRIORITY_TIERS.MODERATE;

  // Real-time What-If Dynamic Calculation
  const simGainHealth = Math.round(
    afforestationDensity * 0.22 +
    waterHarvestingUnits * 0.85 +
    biocharTreatment * 0.15
  );
  const simProjectedHealth = Math.min(98, zone.healthScore + simGainHealth);
  const simGainNdvi = ((afforestationDensity * 0.0035) + (waterHarvestingUnits * 0.006)).toFixed(2);
  const simProjectedNdvi = (Math.min(0.92, zone.ndvi + parseFloat(simGainNdvi))).toFixed(2);
  const simExtraCarbon = Math.round((afforestationDensity / 100) * zone.carbonOffsetEstimate * 0.45);
  const simTotalCarbon = zone.carbonOffsetEstimate + simExtraCarbon;

  return (
    <div className="zone-details-card">
      {/* Header */}
      <div className="zone-panel-header">
        <div>
          <div className="flex-center-gap">
            <span
              className="tier-pill"
              style={{ background: tier.bg, color: tier.color, borderColor: tier.border }}
            >
              {tier.label} Priority ({zone.priorityScore}/100)
            </span>
            <span className="coord-text">
              <MapPin size={13} /> {zone.lat.toFixed(4)}° N, {zone.lng.toFixed(4)}° E
            </span>
          </div>
          <h2 className="zone-panel-title">{zone.name}</h2>
          <p className="zone-panel-subtitle">{zone.region}</p>
        </div>

        <button className="btn-close" onClick={onClose} aria-label="Close Panel">
          <X size={18} />
        </button>
      </div>

      {/* Quick Summary Highlights */}
      <div className="zone-quick-stats">
        <div className="quick-stat-box">
          <span className="qs-label">Ecosystem Health</span>
          <span className="qs-val font-accent">{zone.healthScore}%</span>
        </div>
        <div className="quick-stat-box">
          <span className="qs-label">Total Land Area</span>
          <span className="qs-val">{zone.areaHa.toLocaleString()} Ha</span>
        </div>
        <div className="quick-stat-box">
          <span className="qs-label">NDVI Canopy</span>
          <span className="qs-val font-green">{zone.ndvi}</span>
        </div>
        <div className="quick-stat-box">
          <span className="qs-label">Est. Budget</span>
          <span className="qs-val">₹{zone.estCostLakhs} L</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="panel-tabs">
        <button
          className={`panel-tab-btn ${activeTab === "diagnostics" ? "active" : ""}`}
          onClick={() => setActiveTab("diagnostics")}
        >
          <Activity size={15} />
          <span>AI Diagnostics</span>
        </button>
        <button
          className={`panel-tab-btn ${activeTab === "species" ? "active" : ""}`}
          onClick={() => setActiveTab("species")}
        >
          <Trees size={15} />
          <span>Interventions & Flora</span>
        </button>
        <button
          className={`panel-tab-btn ${activeTab === "simulation" ? "active" : ""}`}
          onClick={() => setActiveTab("simulation")}
        >
          <Sliders size={15} />
          <span>What-If Simulation</span>
        </button>
        <button
          className={`panel-tab-btn ${activeTab === "weather" ? "active" : ""}`}
          onClick={() => setActiveTab("weather")}
        >
          <CloudSun size={15} />
          <span>Live Weather</span>
        </button>
      </div>

      {/* TAB CONTENT */}
      <div className="panel-tab-content">
        {/* TAB 1: AI DIAGNOSTICS */}
        {activeTab === "diagnostics" && (
          <div className="tab-pane">
            <h4 className="pane-title">Environmental Factor Breakdown (SHAP Weights)</h4>
            <div className="factors-list">
              <div className="factor-row">
                <div className="factor-header">
                  <span>Vegetation Density (NDVI Index)</span>
                  <span className="font-bold">{zone.ndvi} / 1.00</span>
                </div>
                <div className="factor-bar-track">
                  <div className="factor-bar-fill bg-green" style={{ width: `${zone.ndvi * 100}%` }} />
                </div>
              </div>

              <div className="factor-row">
                <div className="factor-header">
                  <span>Soil Organic Carbon (SOC %)</span>
                  <span className="font-bold">{zone.soilOrganicCarbon}%</span>
                </div>
                <div className="factor-bar-track">
                  <div className="factor-bar-fill bg-amber" style={{ width: `${(zone.soilOrganicCarbon / 2.5) * 100}%` }} />
                </div>
              </div>

              <div className="factor-row">
                <div className="factor-header">
                  <span>Soil Moisture Content</span>
                  <span className="font-bold">{zone.soilMoisture}%</span>
                </div>
                <div className="factor-bar-track">
                  <div className="factor-bar-fill bg-blue" style={{ width: `${zone.soilMoisture}%` }} />
                </div>
              </div>

              <div className="factor-row">
                <div className="factor-header">
                  <span>Biodiversity & Species Richness</span>
                  <span className="font-bold">{zone.biodiversityIndex} / 100</span>
                </div>
                <div className="factor-bar-track">
                  <div className="factor-bar-fill bg-purple" style={{ width: `${zone.biodiversityIndex}%` }} />
                </div>
              </div>

              <div className="factor-row">
                <div className="factor-header">
                  <span>Human Pressure & Encroachment</span>
                  <span className="font-bold font-danger">{zone.humanPressureIndex} / 100</span>
                </div>
                <div className="factor-bar-track">
                  <div className="factor-bar-fill bg-rose" style={{ width: `${zone.humanPressureIndex}%` }} />
                </div>
              </div>
            </div>

            <div className="threats-summary-box">
              <h5 className="threat-header-title">
                <ShieldAlert size={16} className="text-rose" /> Identified Ecological Threats
              </h5>
              <div className="threats-tags-container">
                {zone.threats.map((threat, idx) => (
                  <span key={idx} className="threat-pill">
                    <AlertCircle size={12} /> {threat}
                  </span>
                ))}
              </div>
              <p className="threat-description-text">
                <b>Erosion Hazard:</b> {zone.erosionHazard}. <b>Primary concern:</b> {zone.primaryThreat}.
              </p>
            </div>
          </div>
        )}

        {/* TAB 2: INTERVENTIONS & FLORA */}
        {activeTab === "species" && (
          <div className="tab-pane">
            <div className="intervention-highlight-card">
              <div className="int-badge">
                <Sprout size={16} /> Recommended Master Plan
              </div>
              <h4 className="int-title">{zone.recommendedIntervention}</h4>
              <p className="int-desc">{zone.interventionDetails}</p>
            </div>

            <h4 className="pane-title" style={{ marginTop: "16px" }}>
              Native Keystone Species Recommendations
            </h4>
            <div className="species-list-grid">
              {zone.recommendedSpecies.map((sp, idx) => (
                <div key={idx} className="species-card">
                  <div className="species-name-row">
                    <CheckCircle2 size={16} className="text-emerald" />
                    <div>
                      <h5 className="species-title">{sp.name}</h5>
                      <span className="species-type">{sp.type}</span>
                    </div>
                  </div>
                  <div className="species-metrics">
                    <span className="badge-survival">Survival Rate: <b>{sp.survivalRate}</b></span>
                    <span className="badge-water">Water: {sp.waterNeed}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: WHAT-IF SIMULATION */}
        {activeTab === "simulation" && (
          <div className="tab-pane">
            <div className="sim-intro-box">
              <Sliders size={16} className="text-emerald" />
              <span>
                Simulate environmental interventions in real-time to preview projected ecological recovery.
              </span>
            </div>

            <div className="sim-sliders-container">
              <div className="slider-item">
                <div className="slider-label-row">
                  <span>Afforestation / Tree Planting Density</span>
                  <span className="slider-val">{afforestationDensity}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={afforestationDensity}
                  onChange={(e) => setAfforestationDensity(Number(e.target.value))}
                  className="custom-range"
                />
              </div>

              <div className="slider-item">
                <div className="slider-label-row">
                  <span>Water Harvesting Check-Dams & Swales</span>
                  <span className="slider-val">{waterHarvestingUnits} Structures</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="30"
                  value={waterHarvestingUnits}
                  onChange={(e) => setWaterHarvestingUnits(Number(e.target.value))}
                  className="custom-range"
                />
              </div>

              <div className="slider-item">
                <div className="slider-label-row">
                  <span>Biochar & Soil Microbial Conditioning</span>
                  <span className="slider-val">{biocharTreatment}% Coverage</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={biocharTreatment}
                  onChange={(e) => setBiocharTreatment(Number(e.target.value))}
                  className="custom-range"
                />
              </div>
            </div>

            {/* Projected Simulation Results */}
            <div className="sim-results-card">
              <h5 className="sim-results-title">
                <TrendingUp size={16} /> 5-Year AI Projected Outcomes
              </h5>
              <div className="sim-results-grid">
                <div className="sim-stat-box">
                  <span className="sim-label">Projected Health</span>
                  <span className="sim-big-val font-emerald">
                    {simProjectedHealth}% <small className="font-positive">(+{simGainHealth}%)</small>
                  </span>
                </div>

                <div className="sim-stat-box">
                  <span className="sim-label">Projected NDVI</span>
                  <span className="sim-big-val font-green">
                    {simProjectedNdvi} <small className="font-positive">(+{simGainNdvi})</small>
                  </span>
                </div>

                <div className="sim-stat-box">
                  <span className="sim-label">5-Yr Total Carbon</span>
                  <span className="sim-big-val font-purple">
                    {(simTotalCarbon / 1000).toFixed(1)}k <small>tCO₂e</small>
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: LIVE WEATHER */}
        {activeTab === "weather" && (
          <div className="tab-pane">
            <div className="weather-overview-card">
              <div className="weather-top-row">
                <div>
                  <h3 className="weather-temp">{zone.weather.temp}°C</h3>
                  <p className="weather-cond">{zone.weather.condition}</p>
                </div>
                <CloudSun size={48} className="weather-icon-sun" />
              </div>

              <div className="weather-details-grid">
                <div className="w-box">
                  <Droplets size={16} className="text-blue" />
                  <div>
                    <span className="w-label">Relative Humidity</span>
                    <span className="w-val">{zone.weather.humidity}%</span>
                  </div>
                </div>

                <div className="w-box">
                  <TrendingUp size={16} className="text-emerald" />
                  <div>
                    <span className="w-label">Wind Speed</span>
                    <span className="w-val">{zone.weather.windSpeed} km/h</span>
                  </div>
                </div>

                <div className="w-box">
                  <Droplets size={16} className="text-blue" />
                  <div>
                    <span className="w-label">Annual Precipitation</span>
                    <span className="w-val">{zone.annualRainfall} mm/yr</span>
                  </div>
                </div>

                <div className="w-box">
                  <Activity size={16} className="text-amber" />
                  <div>
                    <span className="w-label">OpenWeather Sync</span>
                    <span className="w-val">Live Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
