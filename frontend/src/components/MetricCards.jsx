import React from "react";
import { Activity, AlertTriangle, Leaf, Flame, ShieldCheck } from "lucide-react";

export default function MetricCards({ stats }) {
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">Average Ecosystem Health</span>
          <div className="metric-icon-bg bg-emerald">
            <Activity size={18} className="text-emerald" />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{stats.avgHealth}%</span>
          <span className={`metric-tag ${stats.avgHealth < 40 ? "tag-danger" : stats.avgHealth < 70 ? "tag-warning" : "tag-success"}`}>
            {stats.avgHealth < 40 ? "Vulnerable" : stats.avgHealth < 70 ? "Moderate" : "Resilient"}
          </span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: `${stats.avgHealth}%`,
              background: stats.avgHealth < 40 ? "#ef4444" : stats.avgHealth < 70 ? "#f59e0b" : "#10b981"
            }}
          />
        </div>
        <span className="metric-subtext">Aggregated across {stats.totalZones} monitored eco-zones</span>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">Critical & High Priority Areas</span>
          <div className="metric-icon-bg bg-rose">
            <AlertTriangle size={18} className="text-rose" />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{stats.criticalCount} <small className="metric-denom">/ {stats.totalZones}</small></span>
          <span className="metric-tag tag-danger">Needs Immediate Action</span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: `${(stats.criticalCount / (stats.totalZones || 1)) * 100}%`,
              background: "#ef4444"
            }}
          />
        </div>
        <span className="metric-subtext">{((stats.criticalCount / (stats.totalZones || 1)) * 100).toFixed(0)}% of sites under urgent restoration threat</span>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">Mean Vegetation NDVI Index</span>
          <div className="metric-icon-bg bg-green">
            <Leaf size={18} className="text-green" />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{stats.avgNdvi}</span>
          <span className="metric-tag tag-info">Target: &gt; 0.65</span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: `${Math.min(100, (parseFloat(stats.avgNdvi) / 0.8) * 100)}%`,
              background: "#059669"
            }}
          />
        </div>
        <span className="metric-subtext">Total area: {stats.totalHa.toLocaleString()} Hectares mapped</span>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-label">Est. 5-Yr Carbon Offset Potential</span>
          <div className="metric-icon-bg bg-purple">
            <Flame size={18} className="text-purple" />
          </div>
        </div>
        <div className="metric-value-row">
          <span className="metric-value">{(stats.totalCarbon / 1000).toFixed(1)}k <small className="metric-denom">tCO₂e</small></span>
          <span className="metric-tag tag-purple">₹{stats.totalCost} L Budget</span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill"
            style={{
              width: "74%",
              background: "#7c3aed"
            }}
          />
        </div>
        <span className="metric-subtext">High sequestration return upon ANR intervention</span>
      </div>
    </div>
  );
}
