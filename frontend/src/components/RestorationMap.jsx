import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { Layers, Eye, ShieldAlert, Sparkles, MapPin, Compass } from "lucide-react";
import { PRIORITY_TIERS } from "../data/zonesData";

// Fix Leaflet default icon path issue in Vite bundler
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Map Controller component to smoothly fly to selected zone or reset center
function MapController({ selectedZone, defaultCenter = [15.0, 78.5], defaultZoom = 6 }) {
  const map = useMap();

  useEffect(() => {
    if (selectedZone && selectedZone.lat && selectedZone.lng) {
      map.flyTo([selectedZone.lat, selectedZone.lng], 10, {
        animate: true,
        duration: 1.2
      });
    }
  }, [selectedZone, map]);

  return null;
}

const TILE_PROVIDERS = {
  standard: {
    name: "OpenStreetMap",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
  },
  satellite: {
    name: "Satellite (ESRI)",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community"
  },
  topo: {
    name: "Topographic",
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: "Map data: &copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors, <a href='http://viewfinderpanoramas.org'>SRTM</a> | Map style: &copy; <a href='https://opentopomap.org'>OpenTopoMap</a>"
  },
  dark: {
    name: "Carto Dark",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors &copy; <a href='https://carto.com/attributions'>CARTO</a>"
  }
};

export default function RestorationMap({ zones = [], selectedZone = null, onSelectZone = () => {} }) {
  const [tileMode, setTileMode] = useState("standard");
  const [showRadius, setShowRadius] = useState(true);

  return (
    <div className="map-wrapper">
      {/* Map Control Floating Bar */}
      <div className="map-toolbar">
        <div className="map-tile-selector">
          <Layers size={15} className="text-muted" />
          <span className="map-tool-title">Map Layer:</span>
          {Object.entries(TILE_PROVIDERS).map(([key, provider]) => (
            <button
              key={key}
              className={`btn-tile-switch ${tileMode === key ? "active" : ""}`}
              onClick={() => setTileMode(key)}
            >
              {provider.name}
            </button>
          ))}
        </div>

        <div className="map-toolbar-actions">
          <button
            className={`btn-toolbar-toggle ${showRadius ? "active" : ""}`}
            onClick={() => setShowRadius(!showRadius)}
          >
            <Eye size={14} />
            <span>{showRadius ? "Hide Buffer Rings" : "Show Buffer Rings"}</span>
          </button>
        </div>
      </div>

      <MapContainer
        center={[15.0, 78.5]}
        zoom={5}
        scrollWheelZoom={true}
        className="leaflet-map-canvas"
      >
        <MapController selectedZone={selectedZone} />

        <TileLayer
          attribution={TILE_PROVIDERS[tileMode].attribution}
          url={TILE_PROVIDERS[tileMode].url}
        />

        {zones.map((zone) => {
          const tier = PRIORITY_TIERS[zone.priorityTier] || PRIORITY_TIERS.MODERATE;
          const isSelected = selectedZone?.id === zone.id;

          return (
            <React.Fragment key={zone.id}>
              {/* Circular Priority Radius Overlay */}
              {showRadius && (
                <CircleMarker
                  center={[zone.lat, zone.lng]}
                  radius={isSelected ? 26 : Math.max(14, zone.priorityScore / 4.5)}
                  pathOptions={{
                    color: tier.color,
                    fillColor: tier.color,
                    fillOpacity: isSelected ? 0.35 : 0.22,
                    weight: isSelected ? 3 : 1.5,
                    dashArray: isSelected ? "4, 4" : undefined
                  }}
                  eventHandlers={{
                    click: () => onSelectZone(zone)
                  }}
                />
              )}

              {/* Interactive Pin Marker with Popup */}
              <Marker
                position={[zone.lat, zone.lng]}
                eventHandlers={{
                  click: () => onSelectZone(zone)
                }}
              >
                <Popup className="custom-popup">
                  <div className="popup-card">
                    <div className="popup-header">
                      <span
                        className="popup-tier-badge"
                        style={{ background: tier.bg, color: tier.color, borderColor: tier.border }}
                      >
                        {tier.label} Priority ({zone.priorityScore}/100)
                      </span>
                      <span className="popup-health">Health: {zone.healthScore}%</span>
                    </div>

                    <h4 className="popup-title">{zone.name}</h4>
                    <p className="popup-region">{zone.region}</p>

                    <div className="popup-metrics-grid">
                      <div className="popup-metric-item">
                        <span className="p-label">NDVI Index</span>
                        <span className="p-val font-green">{zone.ndvi}</span>
                      </div>
                      <div className="popup-metric-item">
                        <span className="p-label">Soil Carbon</span>
                        <span className="p-val">{zone.soilOrganicCarbon}%</span>
                      </div>
                      <div className="popup-metric-item">
                        <span className="p-label">Rainfall</span>
                        <span className="p-val">{zone.annualRainfall} mm</span>
                      </div>
                      <div className="popup-metric-item">
                        <span className="p-label">Area</span>
                        <span className="p-val">{zone.areaHa.toLocaleString()} Ha</span>
                      </div>
                    </div>

                    <div className="popup-threat-box">
                      <span className="popup-threat-title">🚨 Primary Threat:</span>
                      <span className="popup-threat-text">{zone.primaryThreat}</span>
                    </div>

                    <div className="popup-action-box">
                      <span className="popup-rec-title">🌱 AI Recommendation:</span>
                      <p className="popup-rec-desc">{zone.recommendedIntervention}</p>
                    </div>

                    <button
                      className="btn-popup-inspect"
                      onClick={() => onSelectZone(zone)}
                    >
                      <Sparkles size={14} />
                      <span>Inspect Full AI Diagnostics</span>
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Floating Map Legend */}
      <div className="map-legend-card">
        <h5 className="legend-title">Restoration Priority Tiers</h5>
        <div className="legend-items">
          {Object.entries(PRIORITY_TIERS).map(([key, tier]) => (
            <div key={key} className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: tier.color }} />
              <span className="legend-label">{tier.label}</span>
              <span className="legend-range">({tier.min}-{tier.max})</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}