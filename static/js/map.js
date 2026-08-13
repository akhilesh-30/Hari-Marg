/* ============================================
   HARI MARG — Leaflet Map Module
   ============================================ */

let routeMap = null;
let routeLayers = {};
let markerLayers = {};
let userMarker = null;

const MAP_CONFIG = {
  center: [18.0, 74.5],
  zoom: 8,
  minZoom: 7,
  maxZoom: 16,
  tileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  tileAttribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
};

// Custom marker icons
function createStopIcon(type, color) {
  const icons = {
    origin: '🚩',
    destination: '🛕',
    halt: '📍',
    current: '🧡',
  };
  return L.divIcon({
    html: `<div style="
      font-size: 1.6rem;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: white;
      border: 3px solid ${color};
      border-radius: 50%;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);">${icons[type] || '📍'}</div>`,
    className: '',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -22],
  });
}

function createFacilityIcon(category) {
  const map = {
    medical: { emoji: '🏥', color: '#C0392B' },
    food: { emoji: '🍛', color: '#E8703A' },
    water: { emoji: '💧', color: '#2980B9' },
    rest: { emoji: '🛏️', color: '#2E8B57' },
    sanitation: { emoji: '🚻', color: '#7F8C8D' },
    temple: { emoji: '🛕', color: '#8B2E1F' },
  };
  const cfg = map[category] || { emoji: '📌', color: '#E8703A' };
  return L.divIcon({
    html: `<div style="
      font-size: 1.2rem;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: white;
      border: 2px solid ${cfg.color};
      border-radius: 8px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.15);">${cfg.emoji}</div>`,
    className: '',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
    popupAnchor: [0, -18],
  });
}

// Initialize the map
function initRouteMap(containerId) {
  if (routeMap) return routeMap;

  routeMap = L.map(containerId, {
    center: MAP_CONFIG.center,
    zoom: MAP_CONFIG.zoom,
    minZoom: MAP_CONFIG.minZoom,
    maxZoom: MAP_CONFIG.maxZoom,
    zoomControl: false,
  });

  L.tileLayer(MAP_CONFIG.tileUrl, {
    attribution: MAP_CONFIG.tileAttribution,
  }).addTo(routeMap);

  // Zoom control on right side
  L.control.zoom({ position: 'topright' }).addTo(routeMap);

  return routeMap;
}

// Load and render a route
async function loadRoute(routeKey) {
  try {
    const res = await fetch('/static/data/route_coordinates.json');
    const data = await res.json();
    const route = data.routes[routeKey];
    if (!route) return;

    // Clear previous layers for this route
    if (routeLayers[routeKey]) {
      routeMap.removeLayer(routeLayers[routeKey]);
    }
    if (markerLayers[routeKey]) {
      markerLayers[routeKey].forEach(m => routeMap.removeLayer(m));
    }

    const coords = route.stops.map(s => [s.lat, s.lng]);
    const polyline = L.polyline(coords, {
      color: route.color,
      weight: 4,
      opacity: 0.8,
      dashArray: '8, 6',
      lineJoin: 'round',
    }).addTo(routeMap);

    routeLayers[routeKey] = polyline;
    markerLayers[routeKey] = [];

    route.stops.forEach((stop, idx) => {
      const marker = L.marker([stop.lat, stop.lng], {
        icon: createStopIcon(stop.type, route.color),
      }).addTo(routeMap);

      const lang = HariMarg.lang || 'en';
      const name = lang === 'mr' ? stop.name_mr : stop.name;
      marker.bindPopup(`
        <div style="font-family: 'Mukta', sans-serif; text-align: center; min-width: 120px;">
          <strong style="font-size: 1rem; color: #8B2E1F;">${name}</strong><br>
          <span style="font-size: 0.8rem; color: #7A5C46;">Day ${stop.day}</span>
        </div>
      `);

      markerLayers[routeKey].push(marker);
    });

    routeMap.fitBounds(polyline.getBounds(), { padding: [30, 30] });

    return route;
  } catch (err) {
    console.error('Error loading route:', err);
  }
}

// Load facilities onto map
async function loadFacilities(category = null) {
  try {
    const res = await fetch('/static/data/facilities.json');
    const data = await res.json();

    // Remove existing facility markers
    if (window._facilityMarkers) {
      window._facilityMarkers.forEach(m => routeMap.removeLayer(m));
    }
    window._facilityMarkers = [];

    let facilities = data.facilities;
    if (category) {
      facilities = facilities.filter(f => f.category === category);
    }

    const lang = HariMarg.lang || 'en';

    facilities.forEach(f => {
      const marker = L.marker([f.lat, f.lng], {
        icon: createFacilityIcon(f.category),
      }).addTo(routeMap);

      const name = lang === 'mr' ? f.name_mr : f.name;
      const phoneHtml = f.phone ? `<br><a href="tel:${f.phone}" style="color: #E8703A;">📞 ${f.phone}</a>` : '';

      marker.bindPopup(`
        <div style="font-family: 'Mukta', sans-serif; min-width: 150px;">
          <strong style="color: #8B2E1F;">${name}</strong><br>
          <span style="font-size: 0.85rem; color: #7A5C46;">${f.description}</span>
          ${phoneHtml}
        </div>
      `);

      window._facilityMarkers.push(marker);
    });
  } catch (err) {
    console.error('Error loading facilities:', err);
  }
}

// Show user location on the map
async function showUserLocation() {
  try {
    const loc = await HariMarg.getLocation();
    if (loc && routeMap) {
      if (userMarker) routeMap.removeLayer(userMarker);

      userMarker = L.marker([loc.lat, loc.lng], {
        icon: L.divIcon({
          html: `<div style="
            width: 20px; height: 20px;
            background: #2980B9;
            border: 3px solid white;
            border-radius: 50%;
            box-shadow: 0 0 12px rgba(41,128,185,0.5);
          "></div>`,
          className: '',
          iconSize: [20, 20],
          iconAnchor: [10, 10],
        }),
      }).addTo(routeMap);

      userMarker.bindPopup('<strong>📍 You are here</strong>');
    }
  } catch (err) {
    console.error('Could not get user location:', err);
  }
}

// Focus map on a specific stop
function focusOnStop(lat, lng, zoom = 13) {
  if (routeMap) {
    routeMap.flyTo([lat, lng], zoom, { duration: 1.0 });
  }
}
