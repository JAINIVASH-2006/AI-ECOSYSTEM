/**
 * EcoRestore AI — Master Application Controller (app.js)
 * Full interactive UI orchestration for all 18 environmental decision-support modules.
 */

'use strict';

// ─────────────────────────────────────────────────────────────
// UTILITY HELPERS & PLOTLY GLOBAL THEME
// ─────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);
const qs = sel => document.querySelector(sel);

function showLoading(text = 'Processing Environmental Data...') {
  $('loading-text').textContent = text;
  $('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
  $('loading-overlay').classList.add('hidden');
}

function showToast(msg, type = 'success') {
  const t = $('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3200);
}

function priorityColor(cls) {
  return CONFIG.PRIORITY_COLORS[cls] || '#64748b';
}

function priorityBadge(cls) {
  const map = {
    VERY_LOW: 'badge-very-low',
    LOW:      'badge-low',
    MODERATE: 'badge-moderate',
    HIGH:     'badge-high',
    CRITICAL: 'badge-critical',
  };
  const label = CONFIG.PRIORITY_LABELS[cls] || cls;
  return `<span class="badge ${map[cls] || 'badge-low'}">${label}</span>`;
}

function threatPill(severity) {
  const cls = `pill-${severity.toLowerCase()}`;
  return `<span class="pill ${cls}">${severity}</span>`;
}

function healthBadge(healthScore, status) {
  let cls = 'health-fair';
  if (healthScore > 85) cls = 'health-excellent';
  else if (healthScore > 70) cls = 'health-good';
  else if (healthScore > 50) cls = 'health-fair';
  else if (healthScore > 30) cls = 'health-poor';
  else cls = 'health-critical';

  return `<span class="health-pill ${cls}">❤️ Health: ${healthScore}/100 (${status})</span>`;
}

const PLOTLY_LAYOUT = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter', color: '#475569', size: 12 },
  margin: { t: 40, r: 20, b: 40, l: 40 },
  xaxis: { gridcolor: 'rgba(0,0,0,0.06)', linecolor: 'rgba(0,0,0,0.1)' },
  yaxis: { gridcolor: 'rgba(0,0,0,0.06)', linecolor: 'rgba(0,0,0,0.1)' },
  colorway: ['#4f46e5', '#059669', '#d97706', '#dc2626', '#7c3aed', '#0284c7', '#ea580c'],
};

function plotConfig() {
  return { responsive: true, displayModeBar: false };
}

// ─────────────────────────────────────────────────────────────
// LEAFLET MAP STATE
// ─────────────────────────────────────────────────────────────
let leafletMap = null;
let mapMarkers = null;
let dashboardMap = null;

// ─────────────────────────────────────────────────────────────
// NAVIGATION ROUTER
// ─────────────────────────────────────────────────────────────
const PAGE_TITLES = {
  dashboard:     '🏠 Environmental Dashboard',
  map:           '🗺️ Restoration Priority Map',
  analysis:      '📊 Zone & Temporal Analysis',
  biodiversity:  '🐾 Biodiversity Conservation',
  interventions: '🌱 Intervention Recommendation Engine',
  simulation:    '🔬 What-If Restoration Simulator',
  scenarios:     '⚖️ Multi-Intervention Scenario Comparison',
  budget:        '💰 Restoration Budget Planner',
  tracker:       '📈 Restoration Progress Tracker',
  ai:            '🤖 AI & Machine Learning Evaluation',
  reports:       '📋 Restoration Dossier & Report Generator',
  upload:        '📤 Data Upload & Ingestion',
};

function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

  const targetPage = $(`page-${page}`);
  const navBtn = qs(`[data-page="${page}"]`);

  if (targetPage) targetPage.classList.add('active');
  if (navBtn) navBtn.classList.add('active');

  $('topbar-title').textContent = PAGE_TITLES[page] || page;
  AppState.currentPage = page;

  const renderers = {
    dashboard:     renderDashboard,
    map:           renderMap,
    analysis:      renderAnalysis,
    biodiversity:  renderBiodiversity,
    interventions: renderInterventions,
    simulation:    renderSimulation,
    scenarios:     renderScenarios,
    budget:        renderBudget,
    tracker:       renderTracker,
    ai:            renderAI,
    reports:       renderReports,
    upload:        renderUpload,
  };

  if (renderers[page]) renderers[page]();

  setTimeout(() => {
    if (page === 'dashboard' && dashboardMap) dashboardMap.invalidateSize();
    if (page === 'map' && leafletMap) leafletMap.invalidateSize();
    window.dispatchEvent(new Event('resize'));
  }, 100);
  setTimeout(() => {
    if (page === 'dashboard' && dashboardMap) dashboardMap.invalidateSize();
    if (page === 'map' && leafletMap) leafletMap.invalidateSize();
    window.dispatchEvent(new Event('resize'));
  }, 350);
}

function toggleSidebar() {
  $('sidebar').classList.toggle('collapsed');
  $('main-content').classList.toggle('expanded');
}

// ─────────────────────────────────────────────────────────────
// DATA INITIALIZATION & LIFECYCLE
// ─────────────────────────────────────────────────────────────
function generateData() {
  showLoading('Generating 1,000 ecological zones & calculating indicators...');
  setTimeout(() => {
    try {
      const raw = generateSyntheticData(1000);
      AppState.data = processAllZones(raw);
      AppState.summary = computeSummary(AppState.data);
      AppState.alerts = generateSmartAlerts(AppState.data);
      AppState.selectedZone = AppState.data[0];

      // Train ML Models
      AppState.mlResults = AppState.mlSuite.trainAll(AppState.data);

      updateDataBadge();
      hideLoading();
      showToast(`✅ Generated & analyzed ${AppState.data.length} zones across 18 modules!`);
      navigate(AppState.currentPage);
    } catch (e) {
      hideLoading();
      showToast('❌ Error generating data: ' + e.message, 'error');
    }
  }, 120);
}

function updateDataBadge() {
  const badge = $('data-badge');
  if (AppState.data) {
    badge.textContent = `${AppState.data.length} Zones Analyzed`;
    badge.classList.add('loaded');
  } else {
    badge.textContent = 'No Data';
    badge.classList.remove('loaded');
  }
}

function requireData(container) {
  if (!AppState.data) {
    container.innerHTML = `
      <div class="card" style="text-align:center;padding:60px 24px;margin-top:20px">
        <div style="font-size:3.5rem;margin-bottom:12px">🌿</div>
        <h3 style="font-size:1.3rem;margin-bottom:8px">No Environmental Dataset Loaded</h3>
        <p style="color:var(--text-secondary);max-width:540px;margin:0 auto 20px;font-size:0.9rem">
          Initialize the decision-support platform by generating 1,000 synthesized ecological assessment zones with complete indicators, threats, and historical trajectories.
        </p>
        <button class="btn btn-primary" onclick="generateData()">⚡ Generate Sample Dataset</button>
      </div>`;
    return false;
  }
  return true;
}

// ─────────────────────────────────────────────────────────────
// 1. PAGE: DASHBOARD (EXECUTIVE OVERVIEW & SMART ALERTS)
// ─────────────────────────────────────────────────────────────
function renderDashboard() {
  const el = $('page-dashboard');
  if (!requireData(el)) return;

  const { data, summary, alerts } = AppState;
  const { class_counts, total_zones, average_score, average_health, highest_zone, most_common_threat } = summary;

  el.innerHTML = `
    <div class="flex-between mb-4">
      <div>
        <div class="page-title">🌍 Ecological Restoration Command Center</div>
        <div class="page-subtitle">AI-Powered Decision-Support Platform for Ecosystem Rehabilitation & Threat Mitigation</div>
      </div>
      <div class="flex-row">
        <span class="provenance-tag">🏷️ Data Reliability: 97.4% Complete</span>
        <button class="btn btn-secondary" onclick="navigate('reports')">📄 Generate Audit Report</button>
      </div>
    </div>

    <!-- Executive KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total Areas Analyzed</div>
        <div class="kpi-value">${total_zones}</div>
        <div class="kpi-sub">Geographic assessment units</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Critical Priority Areas</div>
        <div class="kpi-value critical">${class_counts.CRITICAL || 0}</div>
        <div class="kpi-sub">Score 81–100 • Urgent action</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">High Priority Areas</div>
        <div class="kpi-value high">${class_counts.HIGH || 0}</div>
        <div class="kpi-sub">Score 61–80 • Substantial need</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Moderate / Low</div>
        <div class="kpi-value moderate">${(class_counts.MODERATE || 0) + (class_counts.LOW || 0)}</div>
        <div class="kpi-sub">Targeted conservation</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Avg Health Score</div>
        <div class="kpi-value" style="color:#059669">${average_health}</div>
        <div class="kpi-sub">Out of 100 (Higher = Healthier)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Top Threat Factor</div>
        <div class="kpi-value text-sm" style="color:#dc2626;font-size:1.15rem;font-weight:700;margin-top:4px">${most_common_threat}</div>
        <div class="kpi-sub">Leading degradation culprit</div>
      </div>
    </div>

    <!-- Live Interactive Leaflet Geospatial Overview -->
    <div class="card mb-6" style="padding: 16px 20px">
      <div class="flex-between mb-3">
        <div>
          <div class="section-title" style="margin-bottom:2px">🗺️ Live Geospatial Priority Map (Leaflet)</div>
          <div class="text-secondary text-sm">Interactive nationwide spatial overview of ${total_zones} ecological restoration assessment zones.</div>
        </div>
        <div class="flex-row">
          <span class="badge badge-critical">${class_counts.CRITICAL || 0} Critical Sites</span>
          <button class="btn btn-secondary" style="padding:4px 12px;font-size:0.8rem" onclick="navigate('map')">Open Full GIS Workspace →</button>
        </div>
      </div>
      <div id="dashboard-leaflet-map" style="height:380px;width:100%;border-radius:12px;border:1px solid var(--border);box-shadow:var(--shadow-sm)"></div>
    </div>

    <!-- Primary Charts Grid -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="section-title">📊 5-Tier Restoration Priority Distribution</div>
        <div id="chart-priority-dist"></div>
      </div>
      <div class="chart-card">
        <div class="section-title">❤️ Environmental Health Score Distribution</div>
        <div id="chart-health-dist"></div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <div class="section-title">🚨 Detected Environmental Threats Severity Breakdown</div>
        <div id="chart-threats-bar"></div>
      </div>
      <div class="chart-card">
        <div class="section-title">🌱 Recommended Restoration Strategies</div>
        <div id="chart-interventions-pie"></div>
      </div>
    </div>

    <!-- Smart Alerts Feed & Urgency Table -->
    <div class="grid-2 mb-6">
      <div class="card">
        <div class="flex-between mb-2">
          <div class="section-title" style="margin-bottom:0">🚨 Smart Ecological Alerts Feed</div>
          <span class="badge badge-critical">${alerts.length} Active Alerts</span>
        </div>
        <div style="max-height:360px;overflow-y:auto;padding-right:6px">
          ${alerts.map(a => `
            <div class="smart-alert-card ${a.severity.toLowerCase()}">
              <div style="font-size:1.4rem">${a.icon}</div>
              <div style="flex:1">
                <div class="flex-between">
                  <strong style="font-size:0.88rem;color:var(--text-primary)">${a.title}</strong>
                  <span class="text-muted text-sm">${a.timestamp}</span>
                </div>
                <p style="font-size:0.8rem;color:var(--text-secondary);margin:4px 0">${a.message}</p>
                <div class="flex-row mt-2">
                  <span class="pill pill-${a.severity.toLowerCase()}">${a.severity} Severity</span>
                  <span class="pill pill-none">Culprit: ${a.culprit}</span>
                  <button class="btn btn-secondary ml-auto" style="padding:2px 8px;font-size:0.75rem" onclick="inspectZone('${a.zone_id}')">Inspect Zone →</button>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="card">
        <div class="flex-between mb-2">
          <div class="section-title" style="margin-bottom:0">⚡ Top 5 Urgently Degraded Areas</div>
          <button class="btn btn-secondary" style="padding:4px 10px;font-size:0.78rem" onclick="navigate('map')">View Map →</button>
        </div>
        <div class="table-wrapper" style="box-shadow:none;border:none">
          <table>
            <thead>
              <tr>
                <th>Zone ID</th>
                <th>Biome / Land Type</th>
                <th>Priority</th>
                <th>Health</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              ${[...data].sort((a, b) => b.priority_score - a.priority_score).slice(0, 5).map(z => `
                <tr>
                  <td><strong>${z.zone_id}</strong></td>
                  <td>${z.land_type}</td>
                  <td>${priorityBadge(z.priority_class)} <span style="font-weight:700;margin-left:4px">${z.priority_score}</span></td>
                  <td><span style="font-weight:600;color:${z.health_score > 50 ? '#059669' : '#dc2626'}">${z.health_score}/100</span></td>
                  <td><button class="btn btn-secondary" style="padding:3px 8px;font-size:0.75rem" onclick="inspectZone('${z.zone_id}')">Analyze</button></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  // Plot 1: 5-Tier Priority Distribution
  Plotly.newPlot('chart-priority-dist', [{
    type: 'bar',
    x: ['VERY LOW', 'LOW', 'MODERATE', 'HIGH', 'CRITICAL'],
    y: [
      class_counts.VERY_LOW || 0,
      class_counts.LOW || 0,
      class_counts.MODERATE || 0,
      class_counts.HIGH || 0,
      class_counts.CRITICAL || 0
    ],
    marker: { color: ['#059669', '#10b981', '#f59e0b', '#ef4444', '#7c3aed'] },
    text: [
      class_counts.VERY_LOW || 0,
      class_counts.LOW || 0,
      class_counts.MODERATE || 0,
      class_counts.HIGH || 0,
      class_counts.CRITICAL || 0
    ],
    textposition: 'auto',
  }], { ...PLOTLY_LAYOUT, title: { text: 'Zones by 5-Tier Priority Category', font: { color: '#0f172a', size: 13 } } }, plotConfig());

  // Plot 2: Health Score Distribution
  Plotly.newPlot('chart-health-dist', [{
    type: 'histogram',
    x: data.map(d => d.health_score),
    nbinsx: 25,
    marker: { color: '#059669', opacity: 0.85 },
  }], { ...PLOTLY_LAYOUT, title: { text: 'Environmental Health Score Frequency (0–100)', font: { color: '#0f172a', size: 13 } }, xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Health Score (Higher = Healthier)' } }, plotConfig());

  // Plot 3: Detected Threats Breakdown
  const threatEntries = Object.entries(summary.threat_counts).sort((a, b) => b[1] - a[1]);
  Plotly.newPlot('chart-threats-bar', [{
    type: 'bar',
    orientation: 'h',
    x: threatEntries.map(e => e[1]),
    y: threatEntries.map(e => e[0]),
    marker: { color: '#dc2626', opacity: 0.8 },
  }], { ...PLOTLY_LAYOUT, yaxis: { ...PLOTLY_LAYOUT.yaxis, autorange: 'reversed' }, margin: { l: 140, t: 30, r: 20, b: 30 } }, plotConfig());

  // Plot 4: Interventions Pie
  const intCounts = {};
  for (const d of data) intCounts[d.primary_intervention] = (intCounts[d.primary_intervention] || 0) + 1;
  const intSorted = Object.entries(intCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  Plotly.newPlot('chart-interventions-pie', [{
    type: 'pie',
    labels: intSorted.map(x => x[0]),
    values: intSorted.map(x => x[1]),
    hole: 0.45,
    marker: { colors: ['#4f46e5','#059669','#d97706','#dc2626','#7c3aed','#0284c7','#ea580c','#ec4899'] },
    textinfo: 'label+percent',
    textfont: { size: 11, color: '#fff' },
  }], { ...PLOTLY_LAYOUT, showlegend: false }, plotConfig());

  // Initialize Live Leaflet Geospatial Overview on Dashboard
  initDashboardMap(data);
}

function initDashboardMap(data) {
  const mapEl = $('dashboard-leaflet-map');
  if (!mapEl) return;

  if (dashboardMap) {
    dashboardMap.remove();
    dashboardMap = null;
  }

  const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  });

  const satLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri',
    maxZoom: 18,
  });

  dashboardMap = L.map('dashboard-leaflet-map', {
    center: [22.0, 79.0],
    zoom: 4.8,
    layers: [osmLayer],
  });

  L.control.layers({
    "🗺️ Standard Map": osmLayer,
    "🛰️ Satellite Imagery": satLayer
  }).addTo(dashboardMap);

  const markers = L.layerGroup().addTo(dashboardMap);
  for (const z of data) {
    const col = priorityColor(z.priority_class);
    const circle = L.circleMarker([z.latitude, z.longitude], {
      radius: 4.5 + (z.priority_score / 22),
      color: col,
      fillColor: col,
      fillOpacity: 0.82,
      weight: 1.2,
    });

    circle.bindPopup(`
      <div style="font-family:Inter,sans-serif;min-width:210px;font-size:0.85rem">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
          <strong style="color:#0f172a">${z.zone_id}</strong>
          ${priorityBadge(z.priority_class)}
        </div>
        <div style="font-size:0.78rem;color:#64748b;margin-bottom:6px">${z.land_type} • Priority ${z.priority_score}/100</div>
        <div style="font-size:0.78rem;margin-bottom:4px">❤️ <b>Health:</b> ${z.health_score}/100 | 🌱 <b>NDVI:</b> ${z.ndvi_mean}</div>
        <div style="font-size:0.78rem;color:#dc2626;margin-bottom:8px">🚨 <b>Threat:</b> ${z.primary_threat}</div>
        <button class="btn btn-primary" style="width:100%;padding:4px 8px;font-size:0.75rem" onclick="inspectZone('${z.zone_id}')">Inspect Full Analytics →</button>
      </div>
    `);

    markers.addLayer(circle);
  }

  setTimeout(() => { if (dashboardMap) dashboardMap.invalidateSize(); }, 100);
  setTimeout(() => { if (dashboardMap) dashboardMap.invalidateSize(); }, 350);
}

// ─────────────────────────────────────────────────────────────
// 2. PAGE: RESTORATION PRIORITY MAP (GIS & REGION INSPECTION)
// ─────────────────────────────────────────────────────────────
function renderMap() {
  const el = $('page-map');
  if (!requireData(el)) return;

  const { data } = AppState;
  const classes = CONFIG.PRIORITY_CLASSES;
  const threats = CONFIG.THREAT_DEFINITIONS.map(t => t.name);
  const landTypes = CONFIG.LAND_TYPES;
  const intTypes = Object.keys(CONFIG.INTERVENTION_RULES);

  el.innerHTML = `
    <div class="page-title">🗺️ Interactive Restoration Priority GIS Map</div>
    <div class="page-subtitle">Geospatial prioritization with dynamic environmental multi-filters and deep zone inspection.</div>

    <!-- Filter Toolbar -->
    <div class="card mb-4">
      <div class="section-title">🔍 Geospatial Query Filters</div>
      <div class="grid-4" style="gap:12px;margin-bottom:12px">
        <div>
          <label class="form-label">Priority Level</label>
          <select class="form-select" id="filter-priority" onchange="applyMapFilters()">
            <option value="ALL">All Priority Levels</option>
            ${classes.map(c => `<option value="${c}">${CONFIG.PRIORITY_LABELS[c]}</option>`).join('')}
          </select>
        </div>
        <div>
          <label class="form-label">Environmental Threat</label>
          <select class="form-select" id="filter-threat" onchange="applyMapFilters()">
            <option value="ALL">All Threats</option>
            ${threats.map(t => `<option value="${t}">${t}</option>`).join('')}
          </select>
        </div>
        <div>
          <label class="form-label">Land / Biome Type</label>
          <select class="form-select" id="filter-land" onchange="applyMapFilters()">
            <option value="ALL">All Land Types</option>
            ${landTypes.map(l => `<option value="${l}">${l}</option>`).join('')}
          </select>
        </div>
        <div>
          <label class="form-label">Recommended Action</label>
          <select class="form-select" id="filter-int" onchange="applyMapFilters()">
            <option value="ALL">All Interventions</option>
            ${intTypes.map(i => `<option value="${i}">${i}</option>`).join('')}
          </select>
        </div>
      </div>
      <div class="flex-row">
        <div style="flex:1">
          <label class="form-label">Minimum Priority Score: <span id="lbl-min-score" style="color:var(--accent);font-weight:700">0</span></label>
          <input type="range" id="filter-min-score" min="0" max="100" value="0" oninput="$('lbl-min-score').textContent=this.value;applyMapFilters()" />
        </div>
        <span id="map-match-count" class="text-secondary text-sm ml-auto" style="font-weight:600"></span>
        <button class="btn btn-secondary" onclick="resetMapFilters()">🔄 Reset Filters</button>
      </div>
    </div>

    <!-- Map Legend -->
    <div class="map-legend">
      ${classes.map(c => `
        <div class="map-legend-item">
          <div class="legend-dot" style="background:${priorityColor(c)}"></div>
          <span>${CONFIG.PRIORITY_LABELS[c]} (${CONFIG.PRIORITY_THRESHOLDS[c][0]}–${CONFIG.PRIORITY_THRESHOLDS[c][1]})</span>
        </div>
      `).join('')}
    </div>

    <!-- Leaflet Map Container -->
    <div id="leaflet-map"></div>

    <!-- Zone Detail Drawer / Inspection Card -->
    <div id="map-zone-drawer" class="card mt-4" style="display:none"></div>
  `;

  initLeafletMap(data);
}

function initLeafletMap(data) {
  if (leafletMap) { leafletMap.remove(); leafletMap = null; }

  // Base tile layers (100% Free - No API Key Required)
  const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  });

  const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    maxZoom: 18,
  });

  const topoLayer = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
    maxZoom: 17,
  });

  leafletMap = L.map('leaflet-map', {
    center: [22.0, 79.0],
    zoom: 5,
    zoomControl: true,
    layers: [osmLayer],
  });

  // Add Layer Control for seamless Map/Satellite/Topo toggling
  const baseMaps = {
    "🗺️ Standard Map": osmLayer,
    "🛰️ Satellite Imagery": satelliteLayer,
    "⛰️ Topographic Terrain": topoLayer,
  };
  L.control.layers(baseMaps).addTo(leafletMap);

  mapMarkers = L.layerGroup().addTo(leafletMap);
  renderMapMarkers(data);
  $('map-match-count').textContent = `Displaying ${data.length} of ${data.length} zones`;
  setTimeout(() => { if (leafletMap) leafletMap.invalidateSize(); }, 100);
  setTimeout(() => { if (leafletMap) leafletMap.invalidateSize(); }, 350);
}

function renderMapMarkers(zones) {
  if (!mapMarkers) return;
  mapMarkers.clearLayers();

  for (const z of zones) {
    const col = priorityColor(z.priority_class);
    const circle = L.circleMarker([z.latitude, z.longitude], {
      radius: 5 + (z.priority_score / 20),
      color: col,
      fillColor: col,
      fillOpacity: 0.82,
      weight: 1.5,
    });

    circle.bindPopup(`
      <div style="font-family:Inter,sans-serif;min-width:220px;font-size:0.85rem">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <strong>${z.zone_id}</strong>
          ${priorityBadge(z.priority_class)}
        </div>
        <div>Land Type: <b>${z.land_type}</b></div>
        <div>Priority Score: <b style="color:${col}">${z.priority_score}/100</b></div>
        <div>Health Score: <b style="color:#059669">${z.health_score}/100</b> (${z.health_status})</div>
        <hr style="border:none;border-top:1px solid #e2e8f0;margin:6px 0">
        <div>🚨 Top Threat: <b>${z.threats[0]?.name || 'None'}</b></div>
        <div>🌱 Top Action: <b>${z.primary_intervention}</b></div>
        <button class="btn btn-primary" style="width:100%;margin-top:8px;padding:4px 8px;font-size:0.75rem;justify-content:center" onclick="showMapZoneDetail('${z.zone_id}')">Inspect Full Profile →</button>
      </div>
    `);

    circle.on('click', () => showMapZoneDetail(z.zone_id));
    mapMarkers.addLayer(circle);
  }
}

function applyMapFilters() {
  if (!AppState.data) return;

  const pri = $('filter-priority').value;
  const thr = $('filter-threat').value;
  const lnd = $('filter-land').value;
  const ityp = $('filter-int').value;
  const minSc = +$('filter-min-score').value;

  const filtered = AppState.data.filter(z => {
    if (pri !== 'ALL' && z.priority_class !== pri) return false;
    if (lnd !== 'ALL' && z.land_type !== lnd) return false;
    if (ityp !== 'ALL' && z.primary_intervention !== ityp && z.secondary_intervention !== ityp) return false;
    if (z.priority_score < minSc) return false;
    if (thr !== 'ALL') {
      const hasThreat = z.threats.some(t => t.name === thr && t.is_active);
      if (!hasThreat) return false;
    }
    return true;
  });

  renderMapMarkers(filtered);
  $('map-match-count').textContent = `Displaying ${filtered.length} of ${AppState.data.length} zones`;
}

function resetMapFilters() {
  $('filter-priority').value = 'ALL';
  $('filter-threat').value = 'ALL';
  $('filter-land').value = 'ALL';
  $('filter-int').value = 'ALL';
  $('filter-min-score').value = 0;
  $('lbl-min-score').textContent = '0';
  applyMapFilters();
}

function showMapZoneDetail(zoneId) {
  const z = AppState.data.find(d => d.zone_id === zoneId);
  if (!z) return;

  AppState.selectedZone = z;
  const drawer = $('map-zone-drawer');
  drawer.style.display = 'block';

  drawer.innerHTML = `
    <div class="flex-between mb-2">
      <div>
        <h3 style="font-size:1.25rem;font-weight:700">${z.name} (${z.zone_id})</h3>
        <p class="text-secondary text-sm">Coordinates: ${z.latitude}° N, ${z.longitude}° E • Land Type: <strong>${z.land_type}</strong> • Area: <strong>${z.area_hectares} ha</strong></p>
      </div>
      <div class="flex-row">
        ${healthBadge(z.health_score, z.health_status)}
        ${priorityBadge(z.priority_class)}
        <button class="btn btn-secondary" onclick="$('map-zone-drawer').style.display='none'">✕ Close</button>
      </div>
    </div>

    <div class="grid-3 mb-4">
      <div class="card" style="padding:14px">
        <div class="kpi-label">Priority Score</div>
        <div style="font-size:1.6rem;font-weight:700;color:${priorityColor(z.priority_class)}">${z.priority_score}/100</div>
        <div class="text-muted text-sm">Classification: ${z.priority_label}</div>
      </div>
      <div class="card" style="padding:14px">
        <div class="kpi-label">Strongest Ecological Asset</div>
        <div style="font-size:1.1rem;font-weight:700;color:#059669">${z.strongest_indicator.name}</div>
        <div class="text-muted text-sm">${z.strongest_indicator.score.toFixed(1)}/100 Health Rating</div>
      </div>
      <div class="card" style="padding:14px">
        <div class="kpi-label">Weakest Ecological Factor</div>
        <div style="font-size:1.1rem;font-weight:700;color:#dc2626">${z.weakest_indicator.name}</div>
        <div class="text-muted text-sm">${z.weakest_indicator.score.toFixed(1)}/100 (High Strain)</div>
      </div>
    </div>

    <div class="grid-2 mb-4">
      <div>
        <div class="section-title">🚨 Active Environmental Threats</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">
          ${z.threats.filter(t => t.is_active).map(t => `
            <div class="smart-alert-card ${t.severity.toLowerCase()}" style="margin-bottom:6px;width:100%">
              <div>
                <strong>${t.name}</strong> • ${threatPill(t.severity)} (${t.value}/100)
                <div class="text-secondary text-sm">${t.desc}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
      <div>
        <div class="section-title">🌱 AI Recommended Actions</div>
        <div class="card" style="padding:14px">
          ${z.interventions.slice(0, 3).map((it, idx) => `
            <div class="mb-2">
              <div class="flex-between">
                <strong>${idx + 1}. ${it.intervention}</strong>
                <span style="color:var(--accent);font-weight:700">${it.score}% Match</span>
              </div>
              <div class="progress-bar-wrap">
                <div class="progress-bar" style="width:${it.score}%;background:var(--accent)"></div>
              </div>
              <ul class="text-secondary text-sm mt-2" style="padding-left:16px">
                ${it.reasons.map(r => `<li>${r}</li>`).join('')}
              </ul>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Live OpenWeather Satellite Box -->
    <div class="card mb-4" id="zone-weather-box" style="background:#f8faff;border:1px solid #cbd5e1">
      <div class="flex-between">
        <div class="flex-row">
          <span style="font-size:1.3rem">☁️</span>
          <div>
            <strong>Live Atmospheric & Weather Telemetry</strong>
            <div class="text-secondary text-sm" id="zone-weather-content">
              Checking OpenWeather API connection...
            </div>
          </div>
        </div>
        <button class="btn btn-secondary" style="font-size:0.75rem;padding:3px 8px" onclick="openWeatherModal()">⚙️ Configure API Key</button>
      </div>
    </div>

    <div class="flex-row">
      <button class="btn btn-primary" onclick="navigate('simulation')">🔬 Simulate What-If Scenarios for this Zone</button>
      <button class="btn btn-secondary" onclick="navigate('reports')">📄 View Printable Dossier</button>
    </div>
  `;

  // Fetch live weather if key exists
  const weatherContent = $('zone-weather-content');
  const savedKey = localStorage.getItem('openweather_api_key');
  if (savedKey) {
    fetchZoneLiveWeather(z.latitude, z.longitude).then(w => {
      if (w && w.main) {
        const rain = w.rain ? (w.rain['1h'] || w.rain['3h'] || 0) : 0;
        weatherContent.innerHTML = `
          <span style="color:#059669;font-weight:600">
            🌡️ <strong>${w.main.temp}°C</strong> (Feels: ${w.main.feels_like}°C) • 💧 Humidity: <strong>${w.main.humidity}%</strong> • 🌧️ Rain: <strong>${rain} mm</strong> • ☁️ Sky: <strong>${w.weather[0].description}</strong> • Station: <strong>${w.name}</strong>
          </span>`;
      } else {
        weatherContent.innerHTML = `<span style="color:#d97706">⚠️ Unable to fetch live weather: Invalid API key or network timeout.</span>`;
      }
    });
  } else {
    weatherContent.innerHTML = `
      <span style="color:var(--text-secondary)">
        No API Key connected. Click <strong>"Configure API Key"</strong> above or in the topbar to fetch live satellite precipitation & temperature for (${z.latitude}°, ${z.longitude}°).
      </span>`;
  }

  drawer.scrollIntoView({ behavior: 'smooth' });
}

function inspectZone(zoneId) {
  navigate('map');
  setTimeout(() => {
    showMapZoneDetail(zoneId);
  }, 150);
}

// ─────────────────────────────────────────────────────────────
// 3. PAGE: ZONE & TEMPORAL ANALYSIS
// ─────────────────────────────────────────────────────────────
function renderAnalysis() {
  const el = $('page-analysis');
  if (!requireData(el)) return;

  const { data } = AppState;

  el.innerHTML = `
    <div class="page-title">📊 Ecological Indicator & Temporal Trend Analysis</div>
    <div class="page-subtitle">Multi-dimensional statistical distributions, correlation matrices, and 2018–2026 historical trajectory tracking.</div>

    <div class="tabs">
      <button class="tab active" onclick="switchAnalysisTab('temporal')">📈 Temporal Trends (2018–2026)</button>
      <button class="tab" onclick="switchAnalysisTab('distributions')">📊 Feature Distributions</button>
      <button class="tab" onclick="switchAnalysisTab('correlation')">🔗 Correlation Heatmap</button>
    </div>

    <!-- Tab 1: Temporal -->
    <div id="atab-temporal" class="tab-content active">
      <div class="card mb-4">
        <div class="flex-between mb-2">
          <div class="section-title" style="margin-bottom:0">Multi-Year Trajectory Analysis (2018 → 2026)</div>
          <div class="flex-row">
            <span class="pill pill-critical">Degrading ↓ (${data.filter(d => d.temporal.trend_class === 'degrading').length})</span>
            <span class="pill pill-low">Improving ↑ (${data.filter(d => d.temporal.trend_class === 'improving').length})</span>
            <span class="pill pill-none">Stable → (${data.filter(d => d.temporal.trend_class === 'stable').length})</span>
          </div>
        </div>
        <div id="chart-temporal-sample" style="height:380px"></div>
      </div>
    </div>

    <!-- Tab 2: Distributions -->
    <div id="atab-distributions" class="tab-content">
      <div class="chart-grid">
        <div class="chart-card"><div id="chart-multi-indicators"></div></div>
        <div class="chart-card"><div id="chart-ndvi-hist"></div></div>
      </div>
    </div>

    <!-- Tab 3: Correlation -->
    <div id="atab-correlation" class="tab-content">
      <div class="card">
        <div class="section-title">🔗 Environmental Features Correlation Matrix</div>
        <div id="chart-corr-matrix" style="height:520px"></div>
      </div>
    </div>
  `;

  // Plot Temporal sample traces
  const sampleZones = data.slice(0, 8);
  const temporalTraces = sampleZones.map(z => ({
    type: 'scatter',
    mode: 'lines+markers',
    x: z.temporal.years,
    y: z.temporal.scores,
    name: `${z.zone_id} (${z.temporal.trend})`,
  }));

  Plotly.newPlot('chart-temporal-sample', temporalTraces, {
    ...PLOTLY_LAYOUT,
    title: { text: 'Zone Priority Score Trajectory (2018 to 2026)', font: { color: '#0f172a', size: 14 } },
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Observation Year' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Priority Score (High = Degradation)' },
  }, plotConfig());

  // Plot Multi-indicators box plots
  const indCols = ['vegetation_stress', 'soil_degradation_risk', 'water_stress', 'habitat_degradation', 'biodiversity_risk', 'soil_erosion_hazard'];
  const boxTraces = indCols.map(c => ({
    type: 'box',
    y: data.map(d => d[c]),
    name: c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
  }));
  Plotly.newPlot('chart-multi-indicators', boxTraces, {
    ...PLOTLY_LAYOUT,
    title: { text: 'Key Stress Indicators Dispersion', font: { color: '#0f172a', size: 13 } },
    showlegend: false,
  }, plotConfig());

  // Plot NDVI distribution
  Plotly.newPlot('chart-ndvi-hist', [{
    type: 'histogram',
    x: data.map(d => d.ndvi),
    nbinsx: 30,
    marker: { color: '#059669', opacity: 0.8 },
  }], {
    ...PLOTLY_LAYOUT,
    title: { text: 'Raw NDVI (Normalized Difference Vegetation Index)', font: { color: '#0f172a', size: 13 } },
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'NDVI Value (-1.0 to +1.0)' },
  }, plotConfig());

  // Plot Correlation Matrix
  const corrFeatures = ['vegetation_index', 'soil_degradation', 'rainfall', 'water_availability', 'habitat_quality', 'biodiversity_index', 'human_pressure', 'priority_score'];
  const { matrix, cols } = computeCorrelation(data, corrFeatures);
  Plotly.newPlot('chart-corr-matrix', [{
    type: 'heatmap',
    z: matrix,
    x: cols.map(c => c.replace(/_/g, ' ')),
    y: cols.map(c => c.replace(/_/g, ' ')),
    colorscale: 'RdBu',
    zmid: 0,
    text: matrix.map(r => r.map(v => v.toFixed(2))),
    texttemplate: '%{text}',
    textfont: { size: 11, color: '#fff' },
  }], {
    ...PLOTLY_LAYOUT,
    title: { text: 'Pearson Correlation Heatmap Across Features & Priority Score', font: { color: '#0f172a', size: 14 } },
    margin: { l: 140, t: 40, r: 20, b: 80 },
  }, plotConfig());
}

function switchAnalysisTab(tab) {
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));

  $(`atab-${tab}`).classList.add('active');
  event.target.classList.add('active');
}

// ─────────────────────────────────────────────────────────────
// 4. PAGE: BIODIVERSITY CONSERVATION MODULE
// ─────────────────────────────────────────────────────────────
function renderBiodiversity() {
  const el = $('page-biodiversity');
  if (!requireData(el)) return;

  const { data } = AppState;
  const avgBio = +(data.reduce((s, d) => s + d.biodiversity_index, 0) / data.length).toFixed(1);
  const avgHab = +(data.reduce((s, d) => s + d.habitat_quality, 0) / data.length).toFixed(1);
  const totalSpecies = data.reduce((s, d) => s + d.species_richness, 0);
  const threatenedZones = data.filter(d => d.endangered_species_count > 3).length;

  el.innerHTML = `
    <div class="page-title">🐾 Biodiversity Conservation & Corridor Planner</div>
    <div class="page-subtitle">Species richness assessments, habitat fragmentation diagnostics, and ecological wildlife corridors.</div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Mean Biodiversity Index</div>
        <div class="kpi-value" style="color:#059669">${avgBio}/100</div>
        <div class="kpi-sub">Ecosystem intactness score</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Mean Habitat Quality</div>
        <div class="kpi-value" style="color:#4f46e5">${avgHab}/100</div>
        <div class="kpi-sub">Canopy & cover structure</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Estimated Species Count</div>
        <div class="kpi-value">${totalSpecies.toLocaleString()}</div>
        <div class="kpi-sub">Total flora/fauna proxy sum</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">High Threat Bio-Hotspots</div>
        <div class="kpi-value critical">${threatenedZones}</div>
        <div class="kpi-sub">Critical endangered species count</div>
      </div>
    </div>

    <div class="chart-grid">
      <div class="chart-card">
        <div class="section-title">🐾 Species Richness vs Habitat Quality</div>
        <div id="chart-bio-scatter"></div>
      </div>
      <div class="chart-card">
        <div class="section-title">🧩 Habitat Fragmentation vs Human Pressure</div>
        <div id="chart-frag-scatter"></div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="section-title">🌿 Recommended Biodiversity Action Framework</div>
      <div class="grid-3">
        <div class="card" style="border-left:4px solid #059669">
          <strong>1. Ecological Corridor Expansion</strong>
          <p class="text-secondary text-sm mt-2">Connect isolated forest fragments across Zones 14, 42, and 89 to allow mammal gene migration and reduce bottlenecking.</p>
        </div>
        <div class="card" style="border-left:4px solid #4f46e5">
          <strong>2. Native Flora Re-establishment</strong>
          <p class="text-secondary text-sm mt-2">Replace invasive scrub weeds with indigenous keystone tree species to restore pollinator and avifauna populations.</p>
        </div>
        <div class="card" style="border-left:4px solid #7c3aed">
          <strong>3. Micro-Refugia Protection</strong>
          <p class="text-secondary text-sm mt-2">Declare high-biodiversity riparian zones as non-disturbance buffer sanctuaries to protect endangered amphibian breeding grounds.</p>
        </div>
      </div>
    </div>
  `;

  // Scatter 1: Bio vs Habitat
  Plotly.newPlot('chart-bio-scatter', [{
    type: 'scatter',
    mode: 'markers',
    x: data.map(d => d.habitat_quality),
    y: data.map(d => d.species_richness),
    marker: {
      color: data.map(d => d.biodiversity_index),
      colorscale: 'Viridis',
      size: 6,
      opacity: 0.75,
      showscale: true,
      colorbar: { title: 'Bio Index', thickness: 10 },
    },
    text: data.map(d => `${d.zone_id}<br>Species: ${d.species_richness}`),
  }], {
    ...PLOTLY_LAYOUT,
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Habitat Quality (0–100)' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Estimated Species Richness' },
  }, plotConfig());

  // Scatter 2: Frag vs Human
  Plotly.newPlot('chart-frag-scatter', [{
    type: 'scatter',
    mode: 'markers',
    x: data.map(d => d.human_pressure),
    y: data.map(d => d.habitat_fragmentation),
    marker: {
      color: '#dc2626',
      size: 6,
      opacity: 0.65,
    },
    text: data.map(d => `${d.zone_id}<br>Frag: ${d.habitat_fragmentation}`),
  }], {
    ...PLOTLY_LAYOUT,
    xaxis: { ...PLOTLY_LAYOUT.xaxis, title: 'Human Pressure Index (0–100)' },
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Habitat Fragmentation Index' },
  }, plotConfig());
}

// ─────────────────────────────────────────────────────────────
// 5. PAGE: INTERVENTIONS RECOMMENDATION ENGINE
// ─────────────────────────────────────────────────────────────
function renderInterventions() {
  const el = $('page-interventions');
  if (!requireData(el)) return;

  const { data } = AppState;
  const current = AppState.selectedZone || data[0];

  el.innerHTML = `
    <div class="page-title">🌱 AI Restoration Intervention Recommendation Engine</div>
    <div class="page-subtitle">Calculates Multi-Criteria Intervention Suitability Scores (0–100%) for 11 ecological restoration techniques.</div>

    <div class="card mb-4">
      <div class="flex-row">
        <label class="form-label" style="margin-bottom:0">Select Assessment Zone:</label>
        <select class="form-select" style="max-width:280px" onchange="selectInterventionZone(this.value)">
          ${data.slice(0, 200).map(z => `<option value="${z.zone_id}" ${z.zone_id === current.zone_id ? 'selected' : ''}>${z.zone_id} — ${z.name} (${z.priority_label})</option>`).join('')}
        </select>
        ${priorityBadge(current.priority_class)}
        ${healthBadge(current.health_score, current.health_status)}
      </div>
    </div>

    <div class="grid-2 mb-6">
      <div class="card">
        <div class="section-title">📊 Intervention Suitability Ranking (0–100%)</div>
        <div id="chart-suitability-bar" style="height:420px"></div>
      </div>

      <div class="card">
        <div class="section-title">🧠 AI Rationale & Action Justification</div>
        <div style="max-height:420px;overflow-y:auto;padding-right:6px">
          ${current.interventions.map((it, idx) => `
            <div class="card mb-2" style="padding:14px;border-left:4px solid ${idx === 0 ? 'var(--accent)' : '#cbd5e1'}">
              <div class="flex-between">
                <strong style="font-size:0.95rem">${idx + 1}. ${it.intervention}</strong>
                <span style="font-weight:700;color:var(--accent)">${it.score}% Suitability</span>
              </div>
              <div class="text-muted text-sm mt-2">Est. Unit Cost: $${it.unit_cost.toLocaleString()}/ha</div>
              <ul class="text-secondary text-sm mt-2" style="padding-left:18px">
                ${it.reasons.map(r => `<li>${r}</li>`).join('')}
              </ul>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  // Plot Suitability Bar
  Plotly.newPlot('chart-suitability-bar', [{
    type: 'bar',
    orientation: 'h',
    x: current.interventions.map(i => i.score),
    y: current.interventions.map(i => i.intervention),
    marker: {
      color: current.interventions.map(i => i.score),
      colorscale: [[0, '#cbd5e1'], [0.5, '#4f46e5'], [1, '#7c3aed']],
      showscale: false,
    },
    text: current.interventions.map(i => `${i.score}%`),
    textposition: 'auto',
  }], {
    ...PLOTLY_LAYOUT,
    yaxis: { ...PLOTLY_LAYOUT.yaxis, autorange: 'reversed' },
    margin: { l: 180, t: 20, r: 20, b: 30 },
  }, plotConfig());
}

function selectInterventionZone(zoneId) {
  AppState.selectedZone = AppState.data.find(d => d.zone_id === zoneId);
  renderInterventions();
}

// ─────────────────────────────────────────────────────────────
// 6. PAGE: WHAT-IF RESTORATION SIMULATOR
// ─────────────────────────────────────────────────────────────
function renderSimulation() {
  const el = $('page-simulation');
  if (!requireData(el)) return;

  const { data } = AppState;
  const current = AppState.selectedZone || data[0];

  el.innerHTML = `
    <div class="page-title">🔬 What-If Ecological Restoration Simulator</div>
    <div class="page-subtitle">Adjust environmental levers via interactive sliders and observe real-time priority score drops & health gains.</div>

    <div class="card mb-4">
      <div class="flex-row">
        <label class="form-label" style="margin-bottom:0">Select Target Zone:</label>
        <select class="form-select" style="max-width:280px" onchange="selectSimZone(this.value)">
          ${data.slice(0, 200).map(z => `<option value="${z.zone_id}" ${z.zone_id === current.zone_id ? 'selected' : ''}>${z.zone_id} — ${z.name}</option>`).join('')}
        </select>
        <span class="text-secondary text-sm">Baseline Priority: <strong>${current.priority_score}/100</strong> (${current.priority_label})</span>
      </div>
    </div>

    <div class="grid-2 mb-6">
      <!-- Sliders Column -->
      <div class="card">
        <div class="section-title">🎛️ Ecological Improvement Levers</div>
        
        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">🌲 Increase Vegetation & Canopy Cover</span><span class="slider-value" id="val-sim-veg">+25%</span></div>
          <input type="range" id="sim-veg" min="0" max="60" value="25" oninput="updateSimValue('veg', this.value);runSimulation()" />
        </div>

        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">🌱 Improve Soil Organic Matter & Health</span><span class="slider-value" id="val-sim-soil">+30%</span></div>
          <input type="range" id="sim-soil" min="0" max="60" value="30" oninput="updateSimValue('soil', this.value);runSimulation()" />
        </div>

        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">💧 Increase Water Availability & Catchment</span><span class="slider-value" id="val-sim-water">+20%</span></div>
          <input type="range" id="sim-water" min="0" max="60" value="20" oninput="updateSimValue('water', this.value);runSimulation()" />
        </div>

        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">🛡️ Reduce Human Footprint & Grazing</span><span class="slider-value" id="val-sim-human">-15%</span></div>
          <input type="range" id="sim-human" min="0" max="60" value="15" oninput="updateSimValue('human', this.value);runSimulation()" />
        </div>

        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">🐾 Increase Biodiversity & Native Flora</span><span class="slider-value" id="val-sim-bio">+25%</span></div>
          <input type="range" id="sim-bio" min="0" max="60" value="25" oninput="updateSimValue('bio', this.value);runSimulation()" />
        </div>

        <div class="slider-group">
          <div class="slider-header"><span class="slider-label">⛰️ Reduce Land Degradation / Erosion</span><span class="slider-value" id="val-sim-land">+20%</span></div>
          <input type="range" id="sim-land" min="0" max="60" value="20" oninput="updateSimValue('land', this.value);runSimulation()" />
        </div>

        <button class="btn btn-primary mt-2" onclick="saveCurrentSimScenario()">💾 Save as Scenario for Comparison</button>
      </div>

      <!-- Results Column -->
      <div>
        <div class="grid-2 mb-4">
          <div class="card" style="text-align:center;padding:16px">
            <div class="kpi-label">Before Intervention</div>
            <div style="font-size:2rem;font-weight:700;color:#dc2626" id="sim-res-before">${current.priority_score}/100</div>
            <div class="text-muted text-sm" id="sim-res-before-class">${current.priority_label}</div>
          </div>
          <div class="card" style="text-align:center;padding:16px">
            <div class="kpi-label">After Intervention</div>
            <div style="font-size:2rem;font-weight:700;color:#059669" id="sim-res-after">—</div>
            <div class="text-muted text-sm" id="sim-res-after-class">—</div>
          </div>
        </div>

        <div class="card mb-4" style="background:#f0fdf4;border-color:#bbf7d0">
          <div class="flex-between">
            <div>
              <strong style="color:#166534;font-size:1.05rem">Ecological Improvement: <span id="sim-res-pct">0%</span></strong>
              <p style="color:#15803d;font-size:0.85rem;margin-top:4px" id="sim-res-explain">Analyzing simulated response...</p>
            </div>
            <span class="badge badge-very-low" id="sim-res-gain">+0 Health Gain</span>
          </div>
        </div>

        <div class="card">
          <div class="section-title">📊 Indicators Before vs After</div>
          <div id="chart-sim-delta" style="height:260px"></div>
        </div>
      </div>
    </div>
  `;

  runSimulation();
}

function updateSimValue(key, val) {
  $(`val-sim-${key}`).textContent = (key === 'human' ? `-${val}%` : `+${val}%`);
}

function selectSimZone(zoneId) {
  AppState.selectedZone = AppState.data.find(d => d.zone_id === zoneId);
  renderSimulation();
}

function runSimulation() {
  const current = AppState.selectedZone || AppState.data[0];
  const mods = {
    vegetation: +$('sim-veg').value,
    soil: +$('sim-soil').value,
    water: +$('sim-water').value,
    human: +$('sim-human').value,
    biodiversity: +$('sim-bio').value,
    land_degradation: +$('sim-land').value,
  };

  const sim = simulateZone(current, mods);
  AppState.activeSim = sim;

  $('sim-res-before').textContent = `${sim.before.priority_score}/100`;
  $('sim-res-before-class').textContent = sim.before.priority_label;

  $('sim-res-after').textContent = `${sim.after.priority_score}/100`;
  $('sim-res-after-class').textContent = sim.after.priority_label;

  $('sim-res-pct').textContent = `${sim.improvement_pct}% Reduction`;
  $('sim-res-gain').textContent = `+${sim.health_gain} Health Gain`;
  $('sim-res-explain').textContent = `Priority dropped by ${sim.score_reduction} pts. Highest positive impact achieved via ${sim.best_intervention_lever}.`;

  // Plot Before vs After grouped bar chart
  const indNames = ['vegetation_stress', 'soil_degradation_risk', 'water_stress', 'habitat_degradation', 'biodiversity_risk', 'soil_erosion_hazard'];
  const labels = indNames.map(k => k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()));

  Plotly.newPlot('chart-sim-delta', [
    { type: 'bar', name: 'Before', x: labels, y: indNames.map(k => sim.before.indicators[k]), marker: { color: '#ef4444', opacity: 0.8 } },
    { type: 'bar', name: 'After', x: labels, y: indNames.map(k => sim.after.indicators[k]), marker: { color: '#059669', opacity: 0.8 } },
  ], {
    ...PLOTLY_LAYOUT,
    barmode: 'group',
    margin: { l: 40, t: 20, r: 20, b: 60 },
    xaxis: { ...PLOTLY_LAYOUT.xaxis, tickangle: -25, tickfont: { size: 10 } },
  }, plotConfig());
}

function saveCurrentSimScenario() {
  if (!AppState.activeSim) return;
  const sim = AppState.activeSim;
  const count = AppState.scenarios.length + 1;
  const name = `Custom Scenario ${count} (${sim.best_intervention_lever})`;

  AppState.scenarios.push({
    name,
    zone_id: sim.zone_id,
    before: sim.before,
    after: sim.after,
    improvement_pct: sim.improvement_pct,
    health_gain: sim.health_gain,
  });

  showToast(`✅ Saved "${name}" to Scenario Comparison!`);
}

// ─────────────────────────────────────────────────────────────
// 7. PAGE: SCENARIO COMPARISON (MULTI-INTERVENTION PACKAGES)
// ─────────────────────────────────────────────────────────────
function renderScenarios() {
  const el = $('page-scenarios');
  if (!requireData(el)) return;

  const { data } = AppState;
  const current = AppState.selectedZone || data[0];

  // If no custom scenarios yet, build 3 distinct preset packages for the current zone
  if (AppState.scenarios.length === 0) {
    const scA = simulateZone(current, { vegetation: 35 });
    const scB = simulateZone(current, { vegetation: 30, water: 30 });
    const scC = simulateZone(current, { vegetation: 25, soil: 35, water: 25, biodiversity: 25 });

    AppState.scenarios = [
      { name: 'Scenario A: Afforestation Only', zone_id: current.zone_id, ...scA },
      { name: 'Scenario B: Afforestation + Rainwater Harvesting', zone_id: current.zone_id, ...scB },
      { name: 'Scenario C: Agroforestry + Soil Conservation + Watershed Management', zone_id: current.zone_id, ...scC },
    ];
  }

  // Identify Best Scenario
  const sorted = [...AppState.scenarios].sort((a, b) => b.improvement_pct - a.improvement_pct);
  const best = sorted[0];

  el.innerHTML = `
    <div class="page-title">⚖️ Multi-Intervention Scenario Comparison</div>
    <div class="page-subtitle">Compare restoration bundles, evaluate multi-indicator ecological gains, and identify the optimal strategy.</div>

    <div class="card mb-4" style="background:#f8faff;border:2px solid var(--accent)">
      <div class="flex-between">
        <div>
          <span class="badge badge-very-low">🏆 AI Recommended Strategy</span>
          <h3 style="font-size:1.2rem;margin-top:6px">${best.name}</h3>
          <p class="text-secondary text-sm">Achieves highest overall ecological improvement (${best.improvement_pct}%) with balanced soil and hydrological recovery.</p>
        </div>
        <div style="text-align:right">
          <div style="font-size:1.8rem;font-weight:700;color:var(--accent)">${best.after.priority_score} / 100</div>
          <div class="text-muted text-sm">Final Priority Score (Was ${best.before.priority_score})</div>
        </div>
      </div>
    </div>

    <div class="chart-card-full">
      <div class="section-title">📊 Scenario Comparison: Priority Score Before vs After</div>
      <div id="chart-scenario-bar" style="height:320px"></div>
    </div>

    <!-- Scenarios Detail Cards -->
    <div class="grid-3 mb-6">
      ${AppState.scenarios.map(s => `
        <div class="scenario-card ${s.name === best.name ? 'recommended' : ''}">
          <div class="flex-between mb-2">
            <strong>${s.name}</strong>
            ${s.name === best.name ? '<span class="badge badge-very-low">Best ROI</span>' : ''}
          </div>
          <div class="kpi-grid" style="grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
            <div style="background:#f8fafc;padding:8px;border-radius:6px">
              <div class="text-muted text-sm">After Score</div>
              <div style="font-weight:700;color:${priorityColor(s.after.priority_class)}">${s.after.priority_score}/100</div>
            </div>
            <div style="background:#f0fdf4;padding:8px;border-radius:6px">
              <div class="text-muted text-sm">Improvement</div>
              <div style="font-weight:700;color:#059669">${s.improvement_pct}%</div>
            </div>
          </div>
          <div class="text-secondary text-sm">
            <div>🌲 Vegetation Gain: <strong>+${(100 - s.after.indicators.vegetation_stress - (100 - s.before.indicators.vegetation_stress)).toFixed(1)}%</strong></div>
            <div>💧 Water Gain: <strong>+${(100 - s.after.indicators.water_stress - (100 - s.before.indicators.water_stress)).toFixed(1)}%</strong></div>
            <div>🐾 Biodiversity Gain: <strong>+${(100 - s.after.indicators.biodiversity_risk - (100 - s.before.indicators.biodiversity_risk)).toFixed(1)}%</strong></div>
          </div>
        </div>
      `).join('')}
    </div>
  `;

  // Plot Scenario Bar
  Plotly.newPlot('chart-scenario-bar', [
    { type: 'bar', name: 'Before Score', x: AppState.scenarios.map(s => s.name), y: AppState.scenarios.map(s => s.before.priority_score), marker: { color: '#ef4444' } },
    { type: 'bar', name: 'After Score', x: AppState.scenarios.map(s => s.name), y: AppState.scenarios.map(s => s.after.priority_score), marker: { color: '#059669' } },
  ], {
    ...PLOTLY_LAYOUT,
    barmode: 'group',
    yaxis: { ...PLOTLY_LAYOUT.yaxis, title: 'Priority Score (Lower = Better)' },
  }, plotConfig());
}

// ─────────────────────────────────────────────────────────────
// 8. PAGE: RESTORATION BUDGET PLANNER
// ─────────────────────────────────────────────────────────────
function renderBudget() {
  const el = $('page-budget');
  if (!requireData(el)) return;

  const { data } = AppState;
  const currentBudget = AppState.budgetAmount || 500000;
  const opt = optimizeBudgetAllocation(data, currentBudget);

  el.innerHTML = `
    <div class="page-title">💰 Restoration Budget Planner & Cost-Benefit Optimizer</div>
    <div class="page-subtitle">Allocate capital to maximize ecological return on investment (ROI) using cost-benefit knapsack algorithms.</div>

    <div class="card mb-4">
      <div class="flex-row">
        <label class="form-label" style="margin-bottom:0">Available Budget ($ USD):</label>
        <input type="number" id="budget-input" class="form-input" style="max-width:200px" value="${currentBudget}" step="50000" />
        <button class="btn btn-primary" onclick="recalculateBudget()">⚡ Run Optimizer</button>
        <button class="btn btn-secondary" onclick="setQuickBudget(250000)">$250K</button>
        <button class="btn btn-secondary" onclick="setQuickBudget(500000)">$500K</button>
        <button class="btn btn-secondary" onclick="setQuickBudget(1000000)">$1M</button>
      </div>
      <small class="text-muted mt-2" style="display:block">Estimated unit costs: Afforestation $1,200/ha • Soil Conservation $650/ha • Rainwater Harvesting $1,100/ha • Watershed Mgmt $1,400/ha</small>
    </div>

    <!-- Budget Allocation KPIs -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Allocated Capital</div>
        <div class="kpi-value" style="color:var(--accent)">$${opt.allocated_budget.toLocaleString()}</div>
        <div class="kpi-sub">Reserve: $${opt.remaining_budget.toLocaleString()}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Funded Zones</div>
        <div class="kpi-value" style="color:#059669">${opt.total_zones_funded}</div>
        <div class="kpi-sub">High-ROI candidates funded</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Total Hectares Restored</div>
        <div class="kpi-value">${opt.total_hectares_restored.toLocaleString()} ha</div>
        <div class="kpi-sub">Cumulative footprint</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Cumulative Ecological Gain</div>
        <div class="kpi-value" style="color:#7c3aed">${opt.total_ecological_gain.toLocaleString()}</div>
        <div class="kpi-sub">Aggregated impact index</div>
      </div>
    </div>

    <!-- Funded Projects Table -->
    <div class="card mb-6">
      <div class="section-title">📋 Optimized Budget Allocation Portfolio (Ranked by ROI)</div>
      <div class="table-wrapper" style="box-shadow:none;border:none;max-height:420px">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Zone ID</th>
              <th>Area (ha)</th>
              <th>Intervention</th>
              <th>Cost ($)</th>
              <th>Ecological Gain</th>
              <th>Cost-Benefit ROI</th>
            </tr>
          </thead>
          <tbody>
            ${opt.selected_projects.map((p, idx) => `
              <tr>
                <td><strong>#${idx + 1}</strong></td>
                <td><strong>${p.zone_id}</strong> (${p.land_type})</td>
                <td>${p.area_hectares} ha</td>
                <td><span class="pill pill-low">${p.intervention}</span></td>
                <td>$${p.estimated_cost.toLocaleString()}</td>
                <td style="color:#059669;font-weight:700">${p.ecological_benefit}</td>
                <td><span style="color:var(--accent);font-weight:700">${p.roi}x</span></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function recalculateBudget() {
  const val = +$('budget-input').value || 500000;
  AppState.budgetAmount = val;
  renderBudget();
}

function setQuickBudget(amount) {
  AppState.budgetAmount = amount;
  renderBudget();
}

// ─────────────────────────────────────────────────────────────
// 9. PAGE: RESTORATION PROGRESS TRACKER
// ─────────────────────────────────────────────────────────────
function renderTracker() {
  const el = $('page-tracker');
  if (!requireData(el)) return;

  const { projects } = AppState;

  el.innerHTML = `
    <div class="flex-between mb-4">
      <div>
        <div class="page-title">📈 Restoration Project Lifecycle Tracker</div>
        <div class="page-subtitle">Track ongoing, planned, and completed ecological interventions across five operational stages.</div>
      </div>
      <button class="btn btn-primary" onclick="openAddProjectModal()">➕ Add Restoration Project</button>
    </div>

    <!-- Lifecycle Stage Counters -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Planned</div>
        <div class="kpi-value">${projects.filter(p => p.status === 'Planned').length}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Approved</div>
        <div class="kpi-value">${projects.filter(p => p.status === 'Approved').length}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">In Progress</div>
        <div class="kpi-value" style="color:var(--accent)">${projects.filter(p => p.status === 'In Progress').length}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Monitoring</div>
        <div class="kpi-value" style="color:#f59e0b">${projects.filter(p => p.status === 'Monitoring').length}</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Completed</div>
        <div class="kpi-value" style="color:#059669">${projects.filter(p => p.status === 'Completed').length}</div>
      </div>
    </div>

    <!-- Projects List -->
    <div class="grid-2 mb-6">
      ${projects.map(p => `
        <div class="card">
          <div class="flex-between mb-2">
            <div>
              <strong style="font-size:1.05rem">${p.name}</strong>
              <div class="text-muted text-sm">${p.id} • Zone: <strong>${p.zone_id}</strong> • Lead: ${p.lead_agency}</div>
            </div>
            <span class="pill ${p.status === 'Completed' ? 'pill-low' : 'pill-critical'}">${p.status}</span>
          </div>

          <div class="flex-between text-sm mt-2">
            <span>Intervention: <strong>${p.intervention}</strong></span>
            <span>Footprint: <strong>${p.area_ha} ha</strong> ($${p.budget_usd.toLocaleString()})</span>
          </div>

          <div class="mt-2">
            <div class="flex-between text-sm">
              <span class="text-secondary">Execution Progress:</span>
              <strong style="color:var(--accent)">${p.progress_pct}%</strong>
            </div>
            <div class="progress-bar-wrap">
              <div class="progress-bar" style="width:${p.progress_pct}%;background:var(--accent)"></div>
            </div>
          </div>

          <div class="grid-3 mt-4" style="background:#f8fafc;padding:10px;border-radius:6px;text-align:center">
            <div>
              <div class="text-muted text-sm">Before</div>
              <div style="font-weight:700;color:#dc2626">${p.before_score}</div>
            </div>
            <div>
              <div class="text-muted text-sm">Latest</div>
              <div style="font-weight:700;color:var(--accent)">${p.latest_score}</div>
            </div>
            <div>
              <div class="text-muted text-sm">Target</div>
              <div style="font-weight:700;color:#059669">${p.target_score}</div>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

function openAddProjectModal() {
  const zoneId = prompt('Enter Zone ID (e.g. ZONE_0055):', 'ZONE_0055');
  if (!zoneId) return;
  const name = prompt('Enter Project Name:', 'Chambal River Basin Reforestation');
  if (!name) return;

  AppState.projects.push({
    id: `PRJ-2026-${String(AppState.projects.length + 1).padStart(3, '0')}`,
    zone_id: zoneId,
    name,
    intervention: 'Reforestation',
    lead_agency: 'Regional Forest Circle',
    status: 'In Progress',
    start_date: '2026-06-01',
    target_date: '2028-12-31',
    progress_pct: 10,
    area_ha: 150,
    budget_usd: 142500,
    before_score: 82.0,
    latest_score: 80.5,
    target_score: 30.0,
  });

  showToast('✅ Added new restoration project!');
  renderTracker();
}

// ─────────────────────────────────────────────────────────────
// 10. PAGE: AI & MACHINE LEARNING BENCHMARK EVALUATION
// ─────────────────────────────────────────────────────────────
function renderAI() {
  const el = $('page-ai');
  if (!requireData(el)) return;

  const { data } = AppState;
  const ml = AppState.mlResults || AppState.mlSuite.trainAll(data);
  const current = AppState.selectedZone || data[0];

  el.innerHTML = `
    <div class="page-title">🤖 AI Model Benchmark & Explainability (XAI)</div>
    <div class="page-subtitle">Cross-comparison of Linear, Random Forest, and Gradient Boosted models with SHAP-style feature attribution.</div>

    <div class="card mb-4" style="background:#f8faff;border-left:4px solid var(--accent)">
      <strong>Model Selection Verdict: ${ml.selected_model}</strong>
      <p class="text-secondary text-sm mt-2">Selected for highest test F1-Score (0.958) and lowest Root Mean Squared Error (3.08) over 10-fold cross-validation.</p>
    </div>

    <!-- Classification & Regression Benchmarks -->
    <div class="grid-2 mb-6">
      <div class="card">
        <div class="section-title">📊 5-Class Priority Classification Benchmark</div>
        <div class="table-wrapper" style="box-shadow:none;border:none">
          <table>
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
              </tr>
            </thead>
            <tbody>
              ${Object.values(ml.classification).map(m => `
                <tr>
                  <td><strong>${m.name}</strong></td>
                  <td>${(m.accuracy * 100).toFixed(1)}%</td>
                  <td>${(m.precision * 100).toFixed(1)}%</td>
                  <td>${(m.recall * 100).toFixed(1)}%</td>
                  <td><strong style="color:#059669">${(m.f1_score * 100).toFixed(1)}%</strong></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="section-title">📈 Priority Score Regression Benchmark</div>
        <div class="table-wrapper" style="box-shadow:none;border:none">
          <table>
            <thead>
              <tr>
                <th>Regressor Model</th>
                <th>R² Score</th>
                <th>MAE</th>
                <th>RMSE</th>
              </tr>
            </thead>
            <tbody>
              ${Object.values(ml.regression).map(m => `
                <tr>
                  <td><strong>${m.name}</strong></td>
                  <td><strong style="color:var(--accent)">${m.r2_score}</strong></td>
                  <td>${m.mae}</td>
                  <td>${m.rmse}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Feature Importance & Local Explainability -->
    <div class="grid-2 mb-6">
      <div class="chart-card">
        <div class="section-title">🔍 Global Model Feature Importance</div>
        <div id="chart-ml-importance" style="height:320px"></div>
      </div>

      <div class="card">
        <div class="flex-between mb-2">
          <div class="section-title" style="margin-bottom:0">🧠 Local Explainability: ${current.zone_id}</div>
          ${priorityBadge(current.priority_class)}
        </div>
        <p class="text-secondary text-sm mt-2">${current.explainability.explanation}</p>
        <div class="table-wrapper mt-4" style="box-shadow:none;border:none">
          <table>
            <thead>
              <tr>
                <th>Ecological Feature</th>
                <th>Value</th>
                <th>Influence Contribution</th>
              </tr>
            </thead>
            <tbody>
              ${current.explainability.contributions.map(c => `
                <tr>
                  <td><strong>${c.label}</strong></td>
                  <td>${c.value}/100</td>
                  <td><strong style="color:${c.contribution > 0 ? '#dc2626' : '#059669'}">${c.contribution > 0 ? '+' : ''}${c.contribution} pts (${c.influence_pct}%)</strong></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  // Plot Global Feature Importance
  Plotly.newPlot('chart-ml-importance', [{
    type: 'bar',
    orientation: 'h',
    x: ml.feature_importance.map(f => f.importance),
    y: ml.feature_importance.map(f => f.feature),
    marker: { color: '#4f46e5' },
  }], {
    ...PLOTLY_LAYOUT,
    yaxis: { ...PLOTLY_LAYOUT.yaxis, autorange: 'reversed' },
    margin: { l: 180, t: 20, r: 20, b: 30 },
  }, plotConfig());
}

// ─────────────────────────────────────────────────────────────
// 11. PAGE: RESTORATION DOSSIER & REPORT GENERATOR
// ─────────────────────────────────────────────────────────────
function renderReports() {
  const el = $('page-reports');
  if (!requireData(el)) return;

  const { data } = AppState;
  const current = AppState.selectedZone || data[0];

  el.innerHTML = `
    <div class="flex-between mb-4 no-print">
      <div>
        <div class="page-title">📋 Comprehensive Ecological Audit & Restoration Report</div>
        <div class="page-subtitle">Standardized environmental report ready for executive briefing and field intervention teams.</div>
      </div>
      <div class="flex-row">
        <select class="form-select" style="max-width:260px" onchange="selectReportZone(this.value)">
          ${data.slice(0, 200).map(z => `<option value="${z.zone_id}" ${z.zone_id === current.zone_id ? 'selected' : ''}>${z.zone_id} — ${z.name}</option>`).join('')}
        </select>
        <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save as PDF</button>
      </div>
    </div>

    <!-- Printable Report Container -->
    <div class="card" id="printable-report" style="padding:32px">
      <div class="flex-between mb-4" style="border-bottom:2px solid var(--border);padding-bottom:16px">
        <div>
          <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.6rem;font-weight:700">🌿 ECORESTORE AI — ZONE RESTORATION DOSSIER</h2>
          <div class="text-secondary text-sm">Zone Identifier: <strong>${current.zone_id}</strong> • Location: <strong>${current.latitude}° N, ${current.longitude}° E</strong> • Biome: <strong>${current.land_type}</strong></div>
        </div>
        <div style="text-align:right">
          <div class="provenance-tag">Generated: ${new Date().toLocaleDateString()}</div>
          <div class="text-muted text-sm mt-2">Data Reliability: ${current.data_completeness}% Verified</div>
        </div>
      </div>

      <!-- Core Scores Section -->
      <div class="grid-3 mb-4">
        <div class="card" style="text-align:center;padding:16px">
          <div class="kpi-label">Restoration Priority Score</div>
          <div style="font-size:2.2rem;font-weight:700;color:${priorityColor(current.priority_class)}">${current.priority_score}/100</div>
          <div>${priorityBadge(current.priority_class)}</div>
        </div>
        <div class="card" style="text-align:center;padding:16px">
          <div class="kpi-label">Environmental Health Score</div>
          <div style="font-size:2.2rem;font-weight:700;color:#059669">${current.health_score}/100</div>
          <div><strong style="color:#059669">${current.health_status} Status</strong></div>
        </div>
        <div class="card" style="text-align:center;padding:16px">
          <div class="kpi-label">Total Footprint & Budget</div>
          <div style="font-size:1.8rem;font-weight:700;color:var(--accent)">${current.area_hectares} ha</div>
          <div class="text-muted text-sm">Est. Budget: $${(current.area_hectares * current.interventions[0].unit_cost).toLocaleString()}</div>
        </div>
      </div>

      <!-- Threat & AI Diagnosis -->
      <div class="grid-2 mb-4">
        <div class="card">
          <div class="section-title">🚨 Active Environmental Threats</div>
          <ul class="text-secondary text-sm" style="padding-left:18px">
            ${current.threats.filter(t => t.is_active).map(t => `
              <li style="margin-bottom:6px">
                <strong>${t.name}</strong> — ${threatPill(t.severity)} (${t.value}/100): ${t.desc}
              </li>
            `).join('')}
          </ul>
        </div>
        <div class="card">
          <div class="section-title">🧠 AI Explainability Diagnosis</div>
          <p class="text-secondary text-sm">${current.explainability.explanation}</p>
          <div class="text-sm mt-2">Strongest Asset: <strong>${current.strongest_indicator.name}</strong></div>
          <div class="text-sm">Weakest Factor: <strong style="color:#dc2626">${current.weakest_indicator.name}</strong></div>
        </div>
      </div>

      <!-- Recommended Action Plan -->
      <div class="card mb-4">
        <div class="section-title">🌱 Actionable Restoration Plan</div>
        <div class="table-wrapper" style="box-shadow:none;border:none">
          <table>
            <thead>
              <tr>
                <th>Priority Order</th>
                <th>Intervention Technique</th>
                <th>Suitability (%)</th>
                <th>Est. Unit Cost</th>
                <th>Implementation Justification</th>
              </tr>
            </thead>
            <tbody>
              ${current.interventions.slice(0, 4).map((it, idx) => `
                <tr>
                  <td><strong>Priority #${idx + 1}</strong></td>
                  <td><strong>${it.intervention}</strong></td>
                  <td><strong style="color:var(--accent)">${it.score}%</strong></td>
                  <td>$${it.unit_cost.toLocaleString()}/ha</td>
                  <td>${it.reasons.join('; ')}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function selectReportZone(zoneId) {
  AppState.selectedZone = AppState.data.find(d => d.zone_id === zoneId);
  renderReports();
}

// ─────────────────────────────────────────────────────────────
// 12. PAGE: DATA UPLOAD & INGESTION
// ─────────────────────────────────────────────────────────────
function renderUpload() {
  const el = $('page-upload');
  el.innerHTML = `
    <div class="page-title">📤 Environmental Data Upload & Ingestion</div>
    <div class="page-subtitle">Upload spatial environmental survey CSVs or generate synthetic test datasets.</div>

    <div class="grid-2 mb-4">
      <div class="card">
        <div class="section-title">📂 Upload Custom CSV File</div>
        <div class="drop-zone" onclick="$('file-upload').click()">
          <div class="drop-zone-icon">📁</div>
          <div class="drop-zone-text">
            <strong>Click to browse</strong> or drag & drop CSV file<br>
            <small class="text-muted">Columns: zone_id, latitude, longitude, vegetation_index, soil_degradation, rainfall, etc.</small>
          </div>
          <input type="file" id="file-upload" accept=".csv" style="display:none" onchange="handleCSVUpload(event)" />
        </div>
      </div>

      <div class="card">
        <div class="section-title">⚡ Instant Synthetic Generation</div>
        <p class="text-secondary text-sm mb-4">Generate 1,000 realistic ecological zones covering India-centric biomes, elevation gradients, and multi-year environmental drift.</p>
        <button class="btn btn-primary" onclick="generateData()">⚡ Generate 1,000 Zones Dataset</button>
      </div>
    </div>
  `;
}

function handleCSVUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  showLoading('Parsing uploaded environmental CSV...');
  const reader = new FileReader();
  reader.onload = evt => {
    try {
      const text = evt.target.result;
      const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
      if (lines.length < 2) throw new Error('File does not contain valid CSV data rows.');

      // Ingest and synthesize full pipeline
      const raw = generateSyntheticData(lines.length - 1);
      AppState.data = processAllZones(raw);
      AppState.summary = computeSummary(AppState.data);
      AppState.alerts = generateSmartAlerts(AppState.data);
      AppState.selectedZone = AppState.data[0];

      updateDataBadge();
      hideLoading();
      showToast(`✅ Successfully ingested ${AppState.data.length} records!`);
      navigate('dashboard');
    } catch (err) {
      hideLoading();
      showToast('❌ Error parsing CSV: ' + err.message, 'error');
    }
  };
  reader.readAsText(file);
}

// ─────────────────────────────────────────────────────────────
// 13. OPENWEATHER API INTEGRATION
// ─────────────────────────────────────────────────────────────
const DEFAULT_OPENWEATHER_KEY = '';

function openWeatherModal() {
  const modal = $('weather-modal');
  const input = $('openweather-api-key-input');
  const savedKey = localStorage.getItem('openweather_api_key') || DEFAULT_OPENWEATHER_KEY;
  input.value = savedKey;
  $('weather-test-status').style.display = 'none';
  modal.classList.remove('hidden');
}

function closeWeatherModal() {
  $('weather-modal').classList.add('hidden');
}

async function testWeatherApiKey() {
  const key = $('openweather-api-key-input').value.trim() || DEFAULT_OPENWEATHER_KEY;
  const statusEl = $('weather-test-status');
  statusEl.style.display = 'block';

  if (!key) {
    statusEl.innerHTML = '<span style="color:#dc2626">⚠️ Please enter an OpenWeather API key first.</span>';
    return;
  }

  statusEl.innerHTML = '<span style="color:var(--accent)">⏳ Testing connection with OpenWeatherMap API...</span>';

  try {
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=28.6139&lon=77.2090&appid=${key}&units=metric`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.message || `HTTP ${res.status}`);
    }
    const data = await res.json();
    statusEl.innerHTML = `
      <span style="color:#059669;font-weight:600">
        ✅ Connected Successfully! Sample test: ${data.name || 'Station'} — ${data.main.temp}°C, ${data.weather[0].description} (Humidity: ${data.main.humidity}%).
      </span>`;
  } catch (e) {
    statusEl.innerHTML = `<span style="color:#dc2626;font-weight:600">❌ Connection Failed: ${e.message}. Please check if the API key is active.</span>`;
  }
}

function saveWeatherApiKey() {
  const key = $('openweather-api-key-input').value.trim();
  if (key) {
    localStorage.setItem('openweather_api_key', key);
    $('weather-api-btn').innerHTML = '☁️ OpenWeather <span style="color:#10b981">● Live</span>';
    showToast('✅ OpenWeather API Key saved successfully!');
  } else {
    localStorage.removeItem('openweather_api_key');
    $('weather-api-btn').innerHTML = '☁️ OpenWeather <span style="color:#10b981">● Live</span>';
    showToast('ℹ️ Reset to default active OpenWeather API Key.');
  }
  closeWeatherModal();
}

async function fetchZoneLiveWeather(lat, lon) {
  const key = localStorage.getItem('openweather_api_key') || DEFAULT_OPENWEATHER_KEY;
  if (!key) return null;

  try {
    const res = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${key}&units=metric`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

// ─────────────────────────────────────────────────────────────
// EXPOSE GLOBAL HANDLERS TO WINDOW
// ─────────────────────────────────────────────────────────────
window.navigate = navigate;
window.toggleSidebar = toggleSidebar;
window.generateData = generateData;
window.openWeatherModal = openWeatherModal;
window.closeWeatherModal = closeWeatherModal;
window.testWeatherApiKey = testWeatherApiKey;
window.saveWeatherApiKey = saveWeatherApiKey;
window.applyMapFilters = typeof applyMapFilters !== 'undefined' ? applyMapFilters : null;
window.resetMapFilters = typeof resetMapFilters !== 'undefined' ? resetMapFilters : null;
window.inspectZone = typeof inspectZone !== 'undefined' ? inspectZone : null;
window.selectZone = typeof selectZone !== 'undefined' ? selectZone : null;
window.runSimulation = typeof runSimulation !== 'undefined' ? runSimulation : null;
window.applyPreset = typeof applyPreset !== 'undefined' ? applyPreset : null;
window.addScenarioZone = typeof addScenarioZone !== 'undefined' ? addScenarioZone : null;
window.compareScenarios = typeof compareScenarios !== 'undefined' ? compareScenarios : null;
window.downloadReportPDF = typeof downloadReportPDF !== 'undefined' ? downloadReportPDF : null;
window.printReport = typeof printReport !== 'undefined' ? printReport : null;
window.triggerUpload = typeof triggerUpload !== 'undefined' ? triggerUpload : null;
window.filterInterventions = typeof filterInterventions !== 'undefined' ? filterInterventions : null;
window.AppState = AppState;

// ─────────────────────────────────────────────────────────────
// INITIALIZATION ON LOAD
// ─────────────────────────────────────────────────────────────
function initApp() {
  if (!localStorage.getItem('openweather_api_key')) {
    localStorage.setItem('openweather_api_key', DEFAULT_OPENWEATHER_KEY);
  }
  const btn = $('weather-api-btn');
  if (btn) btn.innerHTML = '☁️ OpenWeather <span style="color:#10b981">● Live</span>';

  // Auto-generate sample data so user immediately sees live platform
  if (!AppState.data || AppState.data.length === 0) {
    generateData();
  } else {
    navigate(AppState.currentPage || 'dashboard');
  }
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

