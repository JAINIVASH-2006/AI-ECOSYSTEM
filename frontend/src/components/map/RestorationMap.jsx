import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  Polygon,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import {
  Layers,
  MapPin,
  Sparkles,
  MousePointerClick,
  SquareDashed,
  RotateCcw,
  Check,
  Compass,
  Eye,
  Crosshair,
  Maximize2
} from "lucide-react";

import ZoneLayer from "./ZoneLayer";
import MapLegend from "./MapLegend";
import LocationSearch from "./LocationSearch";
import ZoneDetailsPanel from "./ZoneDetailsPanel";
import ZoneTable from "./ZoneTable";
import DrawAreaModal from "./DrawAreaModal";
import { findZoneForPoint, deleteZone } from "../../services/zoneService";

// Fix Leaflet marker icons in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Map Controller for smooth flyTo bounds/coordinates and auto-fit initial zones
function MapFlyController({ targetCoordinates, targetBounds, geojsonData, initialFitDone, setInitialFitDone }) {
  const map = useMap();

  useEffect(() => {
    // Initial auto-fit on data load
    if (geojsonData?.features?.length > 0 && !initialFitDone) {
      try {
        const layer = L.geoJSON(geojsonData);
        const bounds = layer.getBounds();
        if (bounds.isValid()) {
          map.fitBounds(bounds, { padding: [50, 50], duration: 1.0 });
          setInitialFitDone(true);
        }
      } catch (e) {
        console.warn("Could not fit initial bounds:", e);
      }
    }
  }, [geojsonData, initialFitDone, setInitialFitDone, map]);

  useEffect(() => {
    if (targetBounds) {
      map.fitBounds(targetBounds, { padding: [60, 60], duration: 1.2 });
    } else if (targetCoordinates) {
      map.flyTo([targetCoordinates.lat, targetCoordinates.lon || targetCoordinates.lng], 11, {
        animate: true,
        duration: 1.2,
      });
    }
  }, [targetCoordinates, targetBounds, map]);

  return null;
}

// Click & Draw Event Handler on Leaflet Canvas
function MapInteractionHandler({
  mode,
  onPointClicked,
  onAddDrawPoint,
}) {
  useMapEvents({
    click(e) {
      if (mode === "point") {
        onPointClicked(e.latlng);
      } else if (mode === "draw") {
        onAddDrawPoint([e.latlng.lng, e.latlng.lat]); // [lon, lat] for GeoJSON
      }
    },
  });
  return null;
}

const BASE_MAPS = {
  osm: {
    name: "OpenStreetMap",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  },
  satellite: {
    name: "Satellite (ESRI)",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS",
  },
  topo: {
    name: "Topographic",
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: '&copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)',
  },
};

export default function RestorationMap({
  geojsonData,
  onRefreshZones,
  onSelectZoneForAnalysis,
}) {
  const [selectedBaseMap, setSelectedBaseMap] = useState("osm");
  const [showZonesLayer, setShowZonesLayer] = useState(true);
  const [showPriorityColors, setShowPriorityColors] = useState(true);
  const [initialFitDone, setInitialFitDone] = useState(false);

  const [selectedZone, setSelectedZone] = useState(null);
  const [targetCoords, setTargetCoords] = useState(null);
  const [targetBounds, setTargetBounds] = useState(null);

  // Interaction Modes: "default" | "point" | "draw"
  const [interactionMode, setInteractionMode] = useState("default");
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [pointContainingZone, setPointContainingZone] = useState(null);

  // Polygon Drawing state: array of [lon, lat]
  const [drawPoints, setDrawPoints] = useState([]);
  const [isDrawModalOpen, setIsDrawModalOpen] = useState(false);

  // Quick Region Focus list
  const QUICK_REGIONS = [
    { label: "🎯 Fit All Zones", bounds: null, fitAll: true },
    { label: "📍 Cauvery Delta", coords: { lat: 10.96, lon: 78.08 } },
    { label: "📍 Nilgiris Biosphere", coords: { lat: 11.41, lon: 76.70 } },
    { label: "📍 Agasthyamalai", coords: { lat: 8.62, lon: 77.25 } },
    { label: "📍 Rayalaseema", coords: { lat: 14.68, lon: 77.60 } },
    { label: "📍 Perambalur", coords: { lat: 11.23, lon: 78.88 } },
  ];

  const handleQuickFocus = (item) => {
    if (item.fitAll && geojsonData?.features?.length > 0) {
      try {
        const layer = L.geoJSON(geojsonData);
        setTargetBounds(layer.getBounds());
      } catch (e) {
        setTargetCoords({ lat: 11.5, lon: 78.0 });
      }
    } else if (item.coords) {
      setTargetBounds(null);
      setTargetCoords(item.coords);
    }
  };

  // Handler for Location Search
  const handleLocationSelect = (loc) => {
    setTargetBounds(null);
    setTargetCoords({ lat: loc.lat, lon: loc.lon });
    setSelectedPoint({ lat: loc.lat, lng: loc.lon, name: loc.name });
  };

  // Handler for Zone Selection (from Map polygon or Table)
  const handleZoneSelect = (props, geometry) => {
    setSelectedZone(props);
    setSelectedPoint(null);

    if (geometry && geometry.coordinates) {
      try {
        const coords = geometry.type === "Polygon" ? geometry.coordinates[0] : geometry.coordinates[0][0];
        const latLngs = coords.map((c) => [c[1], c[0]]);
        const bounds = L.latLngBounds(latLngs);
        setTargetBounds(bounds);
      } catch (err) {
        if (props.centroid) {
          setTargetCoords({ lat: props.centroid.latitude, lon: props.centroid.longitude });
        }
      }
    }
  };

  // Handler for Point Click Mode
  const handlePointClick = async (latlng) => {
    setSelectedPoint(latlng);
    try {
      const containing = await findZoneForPoint(latlng.lat, latlng.lng);
      setPointContainingZone(containing);
    } catch (err) {
      setPointContainingZone(null);
    }
  };

  // Handler for Drawing Polygon Points
  const handleAddDrawPoint = (pt) => {
    setDrawPoints((prev) => [...prev, pt]);
  };

  const handleFinishDrawing = () => {
    if (drawPoints.length >= 3) {
      setIsDrawModalOpen(true);
    }
  };

  const handleResetDrawing = () => {
    setDrawPoints([]);
    setInteractionMode("default");
  };

  const handleZoneCreated = (newZone) => {
    setDrawPoints([]);
    setInteractionMode("default");
    onRefreshZones();
    setSelectedZone(newZone);
  };

  const handleDeleteZone = async (zoneId) => {
    if (window.confirm("Are you sure you want to delete this study area?")) {
      try {
        await deleteZone(zoneId);
        setSelectedZone(null);
        onRefreshZones();
      } catch (err) {
        alert("Failed to delete zone.");
      }
    }
  };

  const drawPolylineLatLngs = drawPoints.map((p) => [p[1], p[0]]);

  return (
    <div className="gis-master-container">
      {/* Top Search & Actions Bar */}
      <div className="gis-topbar-panel">
        <LocationSearch onLocationSelect={handleLocationSelect} />

        <div className="gis-mode-toggles">
          <button
            className={`btn-mode-toggle ${interactionMode === "point" ? "active-mode" : ""}`}
            onClick={() => {
              setInteractionMode(interactionMode === "point" ? "default" : "point");
              setSelectedPoint(null);
            }}
          >
            <MousePointerClick size={15} />
            <span>{interactionMode === "point" ? "Cancel Point Mode" : "📍 Analyze Location"}</span>
          </button>

          <button
            className={`btn-mode-toggle ${interactionMode === "draw" ? "active-mode" : ""}`}
            onClick={() => {
              setInteractionMode(interactionMode === "draw" ? "default" : "draw");
              setDrawPoints([]);
            }}
          >
            <SquareDashed size={15} />
            <span>{interactionMode === "draw" ? "Cancel Draw Mode" : "⬡ Draw Analysis Area"}</span>
          </button>
        </div>
      </div>

      {/* Quick Region Jump Bar */}
      <div className="quick-focus-toolbar">
        <span className="qf-label"><Crosshair size={13} /> Quick Zoom:</span>
        {QUICK_REGIONS.map((r, idx) => (
          <button
            key={idx}
            className="btn-quick-focus"
            onClick={() => handleQuickFocus(r)}
          >
            {r.label}
          </button>
        ))}
      </div>

      {/* Active Mode Notification Banner */}
      {interactionMode === "point" && (
        <div className="mode-alert-banner point-mode">
          <MousePointerClick size={16} />
          <span>Click anywhere on the map to inspect coordinates and query containing restoration zones.</span>
        </div>
      )}

      {interactionMode === "draw" && (
        <div className="mode-alert-banner draw-mode">
          <div className="flex-align-gap">
            <SquareDashed size={16} />
            <span>Click sequential vertices on map. Vertices: <b>{drawPoints.length}</b></span>
          </div>
          <div className="flex-align-gap">
            {drawPoints.length >= 3 && (
              <button className="btn-finish-draw" onClick={handleFinishDrawing}>
                <Check size={14} /> Finish & Register Study Area
              </button>
            )}
            <button className="btn-reset-draw" onClick={handleResetDrawing}>
              <RotateCcw size={14} /> Clear
            </button>
          </div>
        </div>
      )}

      {/* Main Map Workspace Layout */}
      <div className={`gis-map-workspace ${selectedZone ? "with-details-panel" : ""}`}>
        <div className="gis-map-canvas-wrapper">
          {/* Map Layer Controls Bar */}
          <div className="map-floating-controls">
            <div className="layer-pill-group">
              <span className="ctrl-title">Basemap:</span>
              {Object.entries(BASE_MAPS).map(([key, provider]) => (
                <button
                  key={key}
                  className={`btn-layer-switch ${selectedBaseMap === key ? "active" : ""}`}
                  onClick={() => setSelectedBaseMap(key)}
                >
                  {provider.name}
                </button>
              ))}
            </div>

            <div className="layer-pill-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={showZonesLayer}
                  onChange={(e) => setShowZonesLayer(e.target.checked)}
                />
                <span>Restoration Zones</span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={showPriorityColors}
                  onChange={(e) => setShowPriorityColors(e.target.checked)}
                  disabled={!showZonesLayer}
                />
                <span>Priority Colors</span>
              </label>
            </div>
          </div>

          <MapContainer
            center={[11.5, 78.0]}
            zoom={7}
            scrollWheelZoom={true}
            className="leaflet-gis-viewport"
          >
            <MapFlyController
              targetCoordinates={targetCoords}
              targetBounds={targetBounds}
              geojsonData={geojsonData}
              initialFitDone={initialFitDone}
              setInitialFitDone={setInitialFitDone}
            />

            <MapInteractionHandler
              mode={interactionMode}
              onPointClicked={handlePointClick}
              onAddDrawPoint={handleAddDrawPoint}
            />

            <TileLayer
              attribution={BASE_MAPS[selectedBaseMap].attribution}
              url={BASE_MAPS[selectedBaseMap].url}
            />

            {/* GeoJSON Restoration Zones Layer */}
            {showZonesLayer && (
              <ZoneLayer
                geojsonData={geojsonData}
                selectedZone={selectedZone}
                onZoneClick={handleZoneSelect}
                onInspectZone={handleZoneSelect}
                onAnalyzeZone={onSelectZoneForAnalysis}
                showPriorityColors={showPriorityColors}
              />
            )}

            {/* In-progress User Drawing Preview */}
            {drawPoints.length > 0 && (
              <>
                <Polyline
                  positions={drawPolylineLatLngs}
                  pathOptions={{ color: "#059669", weight: 3, dashArray: "5, 5" }}
                />
                {drawPoints.length >= 3 && (
                  <Polygon
                    positions={drawPolylineLatLngs}
                    pathOptions={{ color: "#059669", fillColor: "#10b981", fillOpacity: 0.35 }}
                  />
                )}
                {drawPoints.map((pt, idx) => (
                  <Marker
                    key={idx}
                    position={[pt[1], pt[0]]}
                    icon={L.divIcon({
                      className: "draw-vertex-marker",
                      html: `<div style="background:#059669;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>`,
                    })}
                  />
                ))}
              </>
            )}

            {/* Point Selection Marker & Popup */}
            {selectedPoint && (
              <Marker position={[selectedPoint.lat, selectedPoint.lng || selectedPoint.lon]}>
                <Popup autoPan={true}>
                  <div className="point-popup-content">
                    <h4 className="point-popup-title">📍 Selected Geographic Point</h4>
                    <p className="point-coords">
                      <b>Latitude:</b> {selectedPoint.lat.toFixed(5)}° N<br />
                      <b>Longitude:</b> {(selectedPoint.lng || selectedPoint.lon).toFixed(5)}° E
                    </p>

                    {pointContainingZone ? (
                      <div className="containing-zone-alert">
                        <span>Inside Study Area: <b>{pointContainingZone.name}</b> ({pointContainingZone.zone_code})</span>
                        <button
                          className="btn-btn-xs-primary mt-2"
                          onClick={() => handleZoneSelect(pointContainingZone, pointContainingZone.geometry)}
                        >
                          View Containing Zone
                        </button>
                      </div>
                    ) : (
                      <div className="unregistered-point-box">
                        <span className="text-secondary text-xs">Unregistered Point. Ready for custom study area or environmental telemetry.</span>
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            )}
          </MapContainer>

          {/* Floating Map Legend */}
          <MapLegend />
        </div>

        {/* Selected Zone Side Panel */}
        {selectedZone && (
          <ZoneDetailsPanel
            zone={selectedZone}
            onClose={() => setSelectedZone(null)}
            onAnalyze={onSelectZoneForAnalysis}
            onDelete={handleDeleteZone}
          />
        )}
      </div>

      {/* Synchronized Spatial Registry Table */}
      <ZoneTable
        zones={geojsonData?.features || []}
        selectedZone={selectedZone}
        onSelectZone={handleZoneSelect}
        onDeleteZone={handleDeleteZone}
      />

      {/* Draw Polygon Modal */}
      <DrawAreaModal
        isOpen={isDrawModalOpen}
        onClose={() => setIsDrawModalOpen(false)}
        drawnCoordinates={drawPoints}
        onZoneCreated={handleZoneCreated}
      />
    </div>
  );
}
