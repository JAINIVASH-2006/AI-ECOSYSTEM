import React, { useState } from "react";
import { X, Check, MapPin, Sparkles, AlertCircle, Compass, HelpCircle } from "lucide-react";
import { createZone } from "../../services/zoneService";

export default function DrawAreaModal({
  isOpen,
  onClose,
  drawnCoordinates,
  onZoneCreated,
}) {
  const [name, setName] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("Tamil Nadu");
  const [region, setRegion] = useState("Cauvery Basin & Tamil Nadu");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  // Approximate area preview
  const numPoints = drawnCoordinates ? drawnCoordinates.length : 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Please provide a name for this study area.");
      return;
    }
    if (!drawnCoordinates || drawnCoordinates.length < 3) {
      setError("Polygon must contain at least 3 points.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Ensure polygon is closed (first point == last point)
      const closedCoords = [...drawnCoordinates];
      const first = closedCoords[0];
      const last = closedCoords[closedCoords.length - 1];
      if (first[0] !== last[0] || first[1] !== last[1]) {
        closedCoords.push(first);
      }

      const payload = {
        name: name.trim(),
        district: district.trim() || undefined,
        state: state.trim() || undefined,
        region: region.trim() || undefined,
        geometry: {
          type: "Polygon",
          coordinates: [closedCoords], // GeoJSON Polygon exterior ring is [lon, lat]
        },
        created_by: "GIS Analyst",
      };

      const created = await createZone(payload);
      onZoneCreated(created);
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save zone. Ensure coordinates are valid.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="gis-modal-backdrop" onClick={onClose}>
      <div className="gis-modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="gis-modal-header">
          <div className="flex-align-gap">
            <div className="modal-icon-bg">
              <Compass size={18} className="text-emerald-600" />
            </div>
            <div>
              <h3 className="modal-heading">Register New Environmental Study Area</h3>
              <p className="modal-subheading">Save custom drawn polygon into PostGIS for spatial analysis</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="gis-modal-body">
          {error && (
            <div className="error-banner">
              <AlertCircle size={15} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-group mb-3">
            <label className="form-label">Study Area Name *</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Karur Riparian Buffer Study Zone"
              required
            />
          </div>

          <div className="grid-2-form mb-3">
            <div className="form-group">
              <label className="form-label">District / County</label>
              <input
                type="text"
                className="form-input"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                placeholder="e.g., Karur"
              />
            </div>
            <div className="form-group">
              <label className="form-label">State / Province</label>
              <input
                type="text"
                className="form-input"
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="e.g., Tamil Nadu"
              />
            </div>
          </div>

          <div className="form-group mb-3">
            <label className="form-label">Ecological Region</label>
            <select
              className="form-select"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
            >
              <option value="Cauvery Basin & Tamil Nadu">Cauvery Basin & Tamil Nadu</option>
              <option value="Western Ghats Biodiversity Hotspot">Western Ghats Biodiversity Hotspot</option>
              <option value="Nilgiris Biosphere Reserve">Nilgiris Biosphere Reserve</option>
              <option value="Deccan Plateau Drylands">Deccan Plateau Drylands</option>
              <option value="Eastern Ghats Escarpment">Eastern Ghats Escarpment</option>
              <option value="Custom Study Area">Other Custom Study Area</option>
            </select>
          </div>

          <div className="drawn-summary-box mb-4">
            <div className="summary-row">
              <span className="s-lbl">Drawn Polygon Vertices:</span>
              <span className="s-val font-bold">{numPoints} Points</span>
            </div>
            <div className="summary-row">
              <span className="s-lbl">Status:</span>
              <span className="s-val text-amber-700">Will be saved as "Not Analyzed"</span>
            </div>
          </div>

          <div className="modal-footer-btns">
            <button
              type="button"
              className="btn btn-outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Validating & Saving..." : "Save Zone to PostGIS"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
