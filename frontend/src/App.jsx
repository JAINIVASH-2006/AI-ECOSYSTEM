import React, { useEffect } from 'react'
import './index.css'

export default function App() {
  useEffect(() => {
    // Dynamically load Plotly and Leaflet CDN scripts if not already present
    const loadScript = (src) => {
      return new Promise((resolve, reject) => {
        if (document.querySelector(`script[src="${src}"]`)) {
          resolve()
          return
        }
        const s = document.createElement('script')
        s.src = src
        s.onload = resolve
        s.onerror = reject
        document.body.appendChild(s)
      })
    }

    const loadCSS = (href) => {
      if (!document.querySelector(`link[href="${href}"]`)) {
        const l = document.createElement('link')
        l.rel = 'stylesheet'
        l.href = href
        document.head.appendChild(l)
      }
    }

    loadCSS('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css')

    Promise.all([
      loadScript('https://cdn.plot.ly/plotly-2.27.0.min.js'),
      loadScript('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'),
    ]).then(() => {
      return loadScript('/data.js')
    }).then(() => {
      return loadScript('/app.js')
    }).then(() => {
      if (window.generateData) {
        window.generateData()
      }
    }).catch(err => {
      console.error('Error loading scripts:', err)
    })
  }, [])

  return (
    <>
      {/* ── Sidebar Navigation ── */}
      <aside className="sidebar" id="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">🌿</span>
            <div>
              <div className="logo-title">EcoRestore AI</div>
              <div className="logo-version">Decision Support v2.0</div>
            </div>
          </div>
        </div>
        <nav className="sidebar-nav">
          <button className="nav-item active" data-page="dashboard" onClick={() => window.navigate && window.navigate('dashboard')}><span className="nav-icon">🏠</span><span>Dashboard</span></button>
          <button className="nav-item" data-page="map" onClick={() => window.navigate && window.navigate('map')}><span className="nav-icon">🗺️</span><span>Priority Map</span></button>
          <button className="nav-item" data-page="analysis" onClick={() => window.navigate && window.navigate('analysis')}><span className="nav-icon">📊</span><span>Zone Analysis</span></button>
          <button className="nav-item" data-page="biodiversity" onClick={() => window.navigate && window.navigate('biodiversity')}><span className="nav-icon">🐾</span><span>Biodiversity</span></button>
          <button className="nav-item" data-page="interventions" onClick={() => window.navigate && window.navigate('interventions')}><span className="nav-icon">🌱</span><span>Interventions</span></button>
          <button className="nav-item" data-page="simulation" onClick={() => window.navigate && window.navigate('simulation')}><span className="nav-icon">🔬</span><span>What-If Simulator</span></button>
          <button className="nav-item" data-page="scenarios" onClick={() => window.navigate && window.navigate('scenarios')}><span className="nav-icon">⚖️</span><span>Scenario Comparison</span></button>
          <button className="nav-item" data-page="budget" onClick={() => window.navigate && window.navigate('budget')}><span className="nav-icon">💰</span><span>Budget Planner</span></button>
          <button className="nav-item" data-page="tracker" onClick={() => window.navigate && window.navigate('tracker')}><span className="nav-icon">📈</span><span>Progress Tracker</span></button>
          <button className="nav-item" data-page="ai" onClick={() => window.navigate && window.navigate('ai')}><span className="nav-icon">🤖</span><span>AI & ML Evaluation</span></button>
          <button className="nav-item" data-page="reports" onClick={() => window.navigate && window.navigate('reports')}><span className="nav-icon">📋</span><span>Reports</span></button>
          <button className="nav-item" data-page="upload" onClick={() => window.navigate && window.navigate('upload')}><span className="nav-icon">📤</span><span>Data Upload</span></button>
        </nav>
        <div className="sidebar-footer">
          <p>🌿 AI Decision-Support Platform<br /><span style={{ color: '#059669', fontWeight: 600 }}>● Live Environment</span></p>
        </div>
      </aside>

      {/* ── Main Application Content ── */}
      <main className="main-content" id="main-content">
        <header className="topbar">
          <button className="menu-toggle" onClick={() => window.toggleSidebar && window.toggleSidebar()} aria-label="Toggle navigation">☰</button>
          <div className="topbar-title" id="topbar-title">Dashboard</div>
          <div className="topbar-actions">
            <button className="btn btn-secondary" onClick={() => window.openWeatherModal && window.openWeatherModal()} style={{ padding: '5px 12px', fontSize: '0.78rem' }} id="weather-api-btn">☁️ OpenWeather API</button>
            <span className="data-badge" id="data-badge">No Data</span>
            <button className="btn btn-primary" onClick={() => window.generateData && window.generateData()} id="gen-btn">⚡ Generate Dataset</button>
          </div>
        </header>

        {/* OpenWeather API Configuration Modal */}
        <div id="weather-modal" className="loading-overlay hidden" style={{ background: 'rgba(15,23,42,0.6)' }}>
          <div className="card" style={{ maxWidth: '480px', width: '90%', margin: '20px auto', boxShadow: 'var(--shadow-lg)' }}>
            <div className="flex-between mb-2">
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>☁️ OpenWeather API Configuration</h3>
              <button className="btn btn-secondary" style={{ padding: '2px 8px' }} onClick={() => window.closeWeatherModal && window.closeWeatherModal()}>✕</button>
            </div>
            <p className="text-secondary text-sm mb-4">
              Connect your free <strong>OpenWeatherMap API key</strong> to enrich zones with real-time temperature, precipitation (rainfall mm), humidity, and satellite atmospheric data.
            </p>
            <div className="form-group">
              <label className="form-label">OpenWeather API Key (AppID)</label>
              <input type="password" id="openweather-api-key-input" className="form-input" placeholder="e.g. 1a2b3c4d5e6f7g8h9i0j..." />
              <small className="text-muted mt-2" style={{ display: 'block' }}>
                Don't have a key? Get one for free at <a href="https://home.openweathermap.org/api_keys" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)', fontWeight: 600 }}>openweathermap.org</a>.
              </small>
            </div>
            <div id="weather-test-status" className="mb-4 text-sm" style={{ display: 'none' }}></div>
            <div className="flex-row">
              <button className="btn btn-secondary" onClick={() => window.testWeatherApiKey && window.testWeatherApiKey()}>🧪 Test Connection</button>
              <button className="btn btn-primary ml-auto" onClick={() => window.saveWeatherApiKey && window.saveWeatherApiKey()}>💾 Save API Key</button>
            </div>
          </div>
        </div>

        {/* Page Containers */}
        <section id="page-dashboard" className="page active"></section>
        <section id="page-map" className="page"></section>
        <section id="page-analysis" className="page"></section>
        <section id="page-biodiversity" className="page"></section>
        <section id="page-interventions" className="page"></section>
        <section id="page-simulation" className="page"></section>
        <section id="page-scenarios" className="page"></section>
        <section id="page-budget" className="page"></section>
        <section id="page-tracker" className="page"></section>
        <section id="page-ai" className="page"></section>
        <section id="page-reports" className="page"></section>
        <section id="page-upload" className="page"></section>
      </main>

      {/* ── Loading Overlay ── */}
      <div className="loading-overlay hidden" id="loading-overlay">
        <div className="loading-content">
          <div className="spinner"></div>
          <p id="loading-text" style={{ fontWeight: 600, fontSize: '0.95rem' }}>Processing Environmental Data...</p>
        </div>
      </div>

      {/* ── Toast Notifications ── */}
      <div className="toast" id="toast"></div>
    </>
  )
}
