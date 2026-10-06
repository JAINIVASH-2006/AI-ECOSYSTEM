import React, { useState, useEffect, useRef } from "react";
import { Search, MapPin, Loader2, X } from "lucide-react";
import { searchLocation } from "../../services/zoneService";

export default function LocationSearch({ onLocationSelect }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);

  // Debounced search query
  useEffect(() => {
    if (!query || query.trim().length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      const res = await searchLocation(query);
      setResults(res);
      setLoading(false);
      setIsOpen(res.length > 0);
    }, 400);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = (item) => {
    onLocationSelect({
      lat: item.lat,
      lon: item.lon,
      name: item.display_name,
      boundingbox: item.boundingbox,
    });
    setQuery(item.display_name.split(",")[0]);
    setIsOpen(false);
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setIsOpen(false);
  };

  return (
    <div className="location-search-wrapper" ref={wrapperRef}>
      <div className="search-input-container">
        <Search size={16} className="search-icon" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search location (e.g., Karur, Perambalur, Nilgiris, Chennai...)"
          className="search-text-input"
          onFocus={() => results.length > 0 && setIsOpen(true)}
        />
        {loading && <Loader2 size={16} className="search-spinner animate-spin" />}
        {query && !loading && (
          <button className="search-clear-btn" onClick={handleClear}>
            <X size={14} />
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <ul className="search-dropdown-menu">
          {results.map((item) => (
            <li
              key={item.place_id}
              className="search-result-item"
              onClick={() => handleSelect(item)}
            >
              <MapPin size={14} className="result-pin-icon" />
              <div className="result-text-wrap">
                <span className="result-main-title">{item.display_name.split(",")[0]}</span>
                <span className="result-sub-title">{item.display_name}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
