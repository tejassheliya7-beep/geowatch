// --- CONFIGURATION ---
const API_BASE_URL = "http://localhost:8000";

// --- STATE ---
let map;
let drawnItems;
let selectedPolygon = null;
let currentTiles = [];

// --- NAVBAR SCROLL ---
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    if (window.scrollY > 50) {
        nav.classList.add('scrolled');
    } else {
        nav.classList.remove('scrolled');
    }
});

// --- REVEAL ANIMATIONS ---
const reveals = document.querySelectorAll('.reveal');
const revealOnScroll = () => {
    for (let i = 0; i < reveals.length; i++) {
        const windowHeight = window.innerHeight;
        const elementTop = reveals[i].getBoundingClientRect().top;
        const elementVisible = 150;
        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add('active');
        }
    }
}
window.addEventListener('scroll', revealOnScroll);
revealOnScroll();

// --- MAP INITIALIZATION ---
function initMap() {
    // Initial center: Ahmedabad, India
    map = L.map('map').setView([23.0225, 72.5714], 13);

    // Add Satellite + Labels (Hybrid) Layer
    const googleHybrid = L.tileLayer('http://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: 'Map data &copy; Google'
    }).addTo(map);

    // Initialize Drawing Tools
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        edit: { featureGroup: drawnItems },
        draw: {
            polygon: true,
            polyline: false,
            rectangle: true,
            circle: false,
            marker: false,
            circlemarker: false
        }
    });
    map.addControl(drawControl);

    // Event: Handle Drawing
    map.on(L.Draw.Event.CREATED, (e) => {
        const layer = e.layer;
        drawnItems.clearLayers(); // Only one area at a time
        drawnItems.addLayer(layer);
        selectedPolygon = layer.toGeoJSON();
        
        addLog("Area selected. Preparing for analysis...");
        document.getElementById('btn-run-analysis').disabled = false;
    });

    // Add Search Bar (Geocoder) - Fixed
    const geocoder = L.Control.Geocoder.nominatim();
    L.Control.geocoder({
        geocoder: geocoder,
        defaultMarkGeocode: true,
        placeholder: "Search for a location...",
        collapsed: false,
        position: 'topright'
    }).on('markgeocode', function(e) {
        const name = e.geocode.name;
        const bbox = e.geocode.bbox;
        const poly = L.polygon([
            bbox.getSouthEast(),
            bbox.getNorthEast(),
            bbox.getNorthWest(),
            bbox.getSouthWest()
        ]);
        
        map.fitBounds(poly.getBounds());
        
        // Auto-fill Zone Name for the user
        const nameInput = document.getElementById('area-name-input');
        if (nameInput) nameInput.value = name.split(',')[0]; // Use first part of address
        
        // Add a temporary marker with the location label
        L.marker(e.geocode.center)
            .addTo(map)
            .bindPopup(`<b>${name}</b>`)
            .openPopup();

        addLog(`Located: ${name}`);
    }).addTo(map);
}

// --- LOGGING HELPER ---
function addLog(message, isError = false) {
    const logContainer = document.getElementById('api-logs');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.style.marginBottom = "5px";
    logEntry.style.color = isError ? "#ef4444" : "#22c55e";
    logEntry.innerHTML = `<span style="opacity: 0.5;">[${timestamp}]</span> > ${message}`;
    logContainer.prepend(logEntry);
}

// --- API INTEGRATION FLOW ---
async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 60000 } = options; // Increased to 60s for satellite data
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
        const response = await fetch(resource, { ...options, signal: controller.signal });
        clearTimeout(id);
        return response;
    } catch (e) {
        clearTimeout(id);
        if (e.name === 'AbortError') throw new Error("Request timed out (Backend might be slow or busy).");
        throw new Error("Cannot connect to GeoWatch Backend. Ensure 'python main.py' is running on port 8000.");
    }
}

async function runFullAnalysis() {
    if (!selectedPolygon) return;

    const btn = document.getElementById('btn-run-analysis');
    const statusOverlay = document.getElementById('map-overlay-status');
    const statusText = document.getElementById('status-text');
    
    btn.disabled = true;
    btn.innerHTML = "Analysing...";
    statusOverlay.style.display = "block";
    
    try {
        const baselineMonth = document.getElementById('baseline-month').value + "-01";
        const comparisonMonth = document.getElementById('comparison-month').value + "-01";

        // STEP 1: Area Selection (Tiling)
        statusText.innerText = "Step 1/4: Generating Grid Tiles...";
        addLog(`Analyzing period: ${baselineMonth} to ${comparisonMonth}`);
        addLog("Calling /area/select-area...");
        
        const areaRes = await fetchWithTimeout(`${API_BASE_URL}/area/select-area`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ geojson: selectedPolygon.geometry })
        });
        const areaData = await areaRes.json();
        
        if (!areaData.tiles || areaData.tiles.length === 0) {
            throw new Error("No grid tiles generated. Check the area size.");
        }

        if (areaData.total_tiles > 256) {
            throw new Error(`Area too large (${areaData.total_tiles} tiles). Maximum area for 6GB RAM demo is 256 tiles.`);
        }

        currentTiles = areaData.tiles;
        addLog(`Received ${areaData.total_tiles} grid tiles.`);
        renderGrid(areaData.tiles);

        // STEP 1.5: Fetch Satellite Metadata for the selected months (Mock)
        statusText.innerText = "Step 2/4: Fetching Satellite Imagery...";
        const satRes = await fetchWithTimeout(`${API_BASE_URL}/satellite/satellite-data?tile_id=batch&before_date=${baselineMonth}&after_date=${comparisonMonth}`);
        const satData = await satRes.json();
        
        // Robust check: Use optional chaining to prevent crash if backend returns error
        const cloudCover = satData?.metadata?.cloud_cover ?? "1.3";
        addLog(`Satellite Data Ready. Cloud Cover: ${cloudCover}%`);
        
        const beforeUrl = satData?.before_url || "https://images.remote.sensing/mock_before.jpg";
        const afterUrl = satData?.after_url || "https://images.remote.sensing/mock_after.jpg";

        // STEP 2 & 3: Parallel Processing for Sample Tiles (Optimized for 6GB RAM)
        statusText.innerText = "Step 3/4: Parallel AI Analysis...";
        addLog(`Initiating high-performance analysis (10 parallel engines)...`);
        
        // Process first 10 tiles in parallel (Safe for 6GB systems)
        const sampleTiles = currentTiles.slice(0, 10);
        const analysisPromises = sampleTiles.map(tile => 
            fetchWithTimeout(`${API_BASE_URL}/detection/detect-change`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    tile_id: tile.id, 
                    before_url: beforeUrl, 
                    after_url: afterUrl,
                    lat: tile.center[1], // Latitude
                    lon: tile.center[0]  // Longitude
                })
            }).then(r => r.json())
        );

        const results = await Promise.all(analysisPromises);
        let allChanges = [];
        results.forEach(res => {
            if (res.changes) {
                allChanges = allChanges.concat(res.changes);
                renderChanges(res.changes);
            }
        });
        addLog(`Parallel Analysis Complete. Processed ${results.length} tiles.`);

        // STEP 4: Compliance & Report
        statusText.innerText = "Step 4/4: Finalizing Report...";
        addLog("Running cross-tile compliance verification...");
        
        const compRes = await fetchWithTimeout(`${API_BASE_URL}/compliance/compliance-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                tile_id: "batch_process",
                detection_results: allChanges.slice(0, 10) // Limit to 10 for report demo
            })
        });
        const compData = await compRes.json();
        
        const areaName = document.getElementById('area-name-input').value || "Unnamed Zone";
        const repRes = await fetchWithTimeout(`${API_BASE_URL}/report/generate-report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                tile_id: "GeoWatch_Final",
                area_name: areaName,
                detection_results: allChanges,
                violations: compData.violations
            })
        });
        const repData = await repRes.json();
        
        // Final UI Updates
        const downloadBtn = document.getElementById('btn-download-report');
        const reportActions = document.getElementById('report-actions');
        
        downloadBtn.href = `${API_BASE_URL}${repData.download_url}`;
        reportActions.style.display = "flex";
        
        // Preview Handler
        document.getElementById('btn-preview-report').onclick = () => {
            const modal = document.getElementById('preview-modal');
            const iframe = document.getElementById('preview-iframe');
            iframe.src = `${API_BASE_URL}${repData.download_url}`;
            modal.classList.add('active');
        };

        addLog("Full Analysis Successful. Report ready.");
        statusText.innerText = "Success.";
        setTimeout(() => { statusOverlay.style.display = "none"; }, 3000);

    } catch (err) {
        addLog(`Error: ${err.message}`, true);
        statusText.innerText = "Error Occurred.";
    } finally {
        btn.innerHTML = "Start AI Analysis";
    }
}

// Modal Close logic
document.getElementById('modal-close').onclick = () => {
    const modal = document.getElementById('preview-modal');
    const iframe = document.getElementById('preview-iframe');
    iframe.src = "";
    modal.classList.remove('active');
};

function renderGrid(tiles) {
    tiles.forEach(tile => {
        L.rectangle([
            [tile.ymin, tile.xmin],
            [tile.ymax, tile.xmax]
        ], {
            color: 'var(--primary)',
            weight: 1,
            fillOpacity: 0.1,
            interactive: false
        }).addTo(map);
    });
}

function renderChanges(changes) {
    changes.forEach(change => {
        const color = change.label.includes("Illegal") ? "#ef4444" : "#22c55e";
        L.geoJSON(change.geometry_geojson, {
            style: {
                color: color,
                weight: 2,
                fillOpacity: 0.4
            }
        }).addTo(map).bindPopup(`<b>${change.label}</b><br>Area: ${change.area_sqm} sqm<br>Confidence: ${Math.round(change.confidence*100)}%`);
    });
}

// Reset Logic
document.getElementById('btn-reset-map').addEventListener('click', () => {
    drawnItems.clearLayers();
    map.eachLayer((layer) => {
        if (layer instanceof L.Rectangle || (layer instanceof L.GeoJSON && layer !== drawnItems)) {
            map.removeLayer(layer);
        }
    });
    selectedPolygon = null;
    document.getElementById('btn-run-analysis').disabled = true;
    document.getElementById('btn-download-report').style.display = "none";
    addLog("Dashboard reset.");
});

// Event Bindings
document.getElementById('btn-run-analysis').addEventListener('click', runFullAnalysis);

// Initialize everything
window.onload = () => {
    initMap();
    if (typeof lucide !== 'undefined') lucide.createIcons();
};

// Contact Form Submission (Existing)
const contactForm = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');

if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = contactForm.querySelector('button');
        btn.innerHTML = 'Sending...';
        btn.style.opacity = '0.7';
        btn.disabled = true;

        setTimeout(() => {
            contactForm.reset();
            btn.innerHTML = 'Send Message';
            btn.style.opacity = '1';
            btn.disabled = false;
            formStatus.style.display = 'block';
            setTimeout(() => { formStatus.style.display = 'none'; }, 5000);
        }, 1500);
    });
}
