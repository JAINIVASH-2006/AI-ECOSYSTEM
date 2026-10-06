import React, { useRef } from "react";
import { GeoJSON, Marker, Tooltip } from "react-leaflet";
import L from "leaflet";
import { PRIORITY_COLORS } from "./MapLegend";

export default function ZoneLayer({
  geojsonData,
  selectedZone,
  onZoneClick,
  onInspectZone,
  onAnalyzeZone,
  showPriorityColors = true,
}) {
  const geoJsonRef = useRef(null);

  if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) {
    return null;
  }

  // Styling function for each polygon feature
  const styleFeature = (feature) => {
    const props = feature.properties || {};
    const isSelected = selectedZone && selectedZone.id === props.id;
    const pClass = props.priority_class || "Not Analyzed";
    const tier = PRIORITY_COLORS[pClass] || PRIORITY_COLORS["Not Analyzed"];

    const color = showPriorityColors ? tier.color : "#0284c7";

    return {
      color: isSelected ? "#312e81" : color,
      weight: isSelected ? 4 : 2.5,
      fillColor: color,
      fillOpacity: isSelected ? 0.55 : 0.35,
      dashArray: isSelected ? "5, 5" : undefined,
    };
  };

  // Event handlers for each polygon feature
  const onEachFeature = (feature, layer) => {
    const props = feature.properties || {};

    layer.on({
      click: () => {
        onZoneClick(props, feature.geometry);
      },
      mouseover: (e) => {
        const l = e.target;
        l.setStyle({
          fillOpacity: 0.65,
          weight: 3.5,
        });
      },
      mouseout: (e) => {
        if (geoJsonRef.current) {
          geoJsonRef.current.resetStyle(e.target);
        }
      },
    });

    layer.bindTooltip(
      `<div style="font-family:Inter,sans-serif;padding:2px 4px">
        <strong style="color:${PRIORITY_COLORS[props.priority_class || "Not Analyzed"]?.color}">${props.zone_code}</strong>: ${props.name}
        <br/><span style="font-size:11px;color:#475569">Area: ${props.area_sq_km} km² • ${props.priority_class} Priority</span>
       </div>`,
      { sticky: true, direction: "top", opacity: 0.95 }
    );
  };

  // Calculate centroids for pin markers
  const centroidFeatures = geojsonData.features.map((feature) => {
    const props = feature.properties || {};
    const coords = feature.geometry?.coordinates?.[0] || [];
    if (coords.length === 0) return null;

    let sumLat = 0, sumLon = 0;
    for (let i = 0; i < coords.length - 1; i++) {
      sumLon += coords[i][0];
      sumLat += coords[i][1];
    }
    const count = coords.length - 1;
    const cLat = sumLat / count;
    const cLon = sumLon / count;

    const pClass = props.priority_class || "Not Analyzed";
    const tier = PRIORITY_COLORS[pClass] || PRIORITY_COLORS["Not Analyzed"];
    const isSelected = selectedZone && selectedZone.id === props.id;

    // Custom HTML DivIcon for prominent visible pins
    const icon = L.divIcon({
      className: "custom-zone-marker-pin",
      html: `
        <div style="
          background:${tier.color};
          color:white;
          font-weight:700;
          font-size:11px;
          font-family:Inter,sans-serif;
          padding:3px 8px;
          border-radius:12px;
          box-shadow:0 2px 6px rgba(0,0,0,0.3);
          border:${isSelected ? "3px solid #312e81" : "2px solid white"};
          white-space:nowrap;
          display:flex;
          align-items:center;
          gap:4px;
          transform:translate(-50%, -50%);
          cursor:pointer;
        ">
          <span>📍</span>
          <span>${props.zone_code}</span>
        </div>
      `,
      iconSize: [80, 24],
      iconAnchor: [40, 12]
    });

    return {
      id: props.id,
      lat: cLat,
      lon: cLon,
      icon,
      props,
      geometry: feature.geometry
    };
  }).filter(Boolean);

  return (
    <>
      <GeoJSON
        key={JSON.stringify(geojsonData.features.map((f) => f.properties.id)) + (selectedZone?.id || "")}
        ref={geoJsonRef}
        data={geojsonData}
        style={styleFeature}
        onEachFeature={onEachFeature}
      />

      {centroidFeatures.map((item) => (
        <Marker
          key={item.id}
          position={[item.lat, item.lon]}
          icon={item.icon}
          eventHandlers={{
            click: () => onZoneClick(item.props, item.geometry),
          }}
        >
          <Tooltip direction="bottom" offset={[0, 10]} opacity={0.95}>
            <div style={{ fontFamily: "Inter, sans-serif", fontSize: "12px" }}>
              <b>{item.props.name}</b> ({item.props.area_sq_km} km²)
              <br />
              <span>Priority: <b>{item.props.priority_class}</b></span>
            </div>
          </Tooltip>
        </Marker>
      ))}
    </>
  );
}
