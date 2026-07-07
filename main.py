<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV Map India</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; color: #334155; }
        #map { height: 100vh; width: 100vw; z-index: 1; }
        .ui-panel { position: absolute; z-index: 1000; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.5); border-radius: 16px; padding: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.08); }
        .filter-box { top: 20px; left: 20px; width: 300px; }
        .stats-box { top: 20px; right: 20px; width: 240px; }
        .logo { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #e2e8f0; }
        .logo-icon { background: #3b82f6; color: white; width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; }
        .logo-text { font-size: 18px; font-weight: 700; color: #0f172a; }
        .logo-sub { font-size: 11px; color: #64748b; font-weight: 600; text-transform: uppercase; }
        label { font-size: 11px; font-weight: 600; color: #64748b; display: block; margin-bottom: 6px; text-transform: uppercase; }
        select, button { width: 100%; padding: 10px 14px; border-radius: 10px; font-size: 14px; font-family: 'Inter', sans-serif; background-color: #f1f5f9; color: #1e293b; border: 1px solid #e2e8f0; outline: none; cursor: pointer; }
        button { background-color: #0f172a; color: white; font-weight: 600; margin-top: 12px; border: none; }
        .stat-group { margin-bottom: 16px; }
        .stat-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; }
        .stat-value { font-size: 28px; font-weight: 700; color: #0f172a; line-height: 1.2; }
        .legend { display: flex; gap: 12px; margin-top: 16px; padding-top: 16px; border-top: 1px solid #e2e8f0; }
        .legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; color: #475569; }
        .dot { width: 10px; height: 10px; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
        .marker-dc { width: 18px; height: 18px; background-color: #EF4444; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(239, 68, 68, 0.5); }
        .marker-ac { width: 14px; height: 14px; background-color: #3B82F6; border: 3px solid white; border-radius: 50%; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.5); }
        .leaflet-popup-content-wrapper { background: white; color: #334155; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); padding: 0; overflow: hidden; }
        .leaflet-popup-content { margin: 0; min-width: 220px; }
        .leaflet-popup-tip { background: white; }
        .popup-header { background: #f8fafc; padding: 12px 16px; border-bottom: 1px solid #f1f5f9; }
        .popup-title { font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 2px; }
        .popup-address { font-size: 12px; color: #64748b; }
        .popup-body { padding: 12px 16px; }
        .popup-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; }
        .popup-key { font-size: 12px; color: #94a3b8; }
        .popup-val { font-size: 13px; font-weight: 600; color: #334155; }
        .badge { padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
        .badge-dc { background: #FEE2E2; color: #DC2626; }
        .badge-ac { background: #DBEAFE; color: #2563EB; }
    </style>
</head>
<body>
    <div id="map"></div>
    <div class="ui-panel filter-box">
        <div class="logo">
            <div class="logo-icon">⚡</div>
            <div>
                <div class="logo-text">EV Map India</div>
                <div class="logo-sub">Live Infrastructure</div>
            </div>
        </div>
        <label>Charger Type</label>
        <select id="filter-type" onchange="applyFilters()">
            <option value="all">All Connector Types</option>
            <option value="dc">DC Fast Chargers</option>
            <option value="ac">AC Slow / Medium</option>
        </select>
        <label style="margin-top: 16px;">Operator Network</label>
        <select id="filter-operator" onchange="applyFilters()">
            <option value="all">All Operators</option>
        </select>
        <button onclick="resetFilters()">Reset Filters</button>
    </div>
    <div class="ui-panel stats-box">
        <div class="stat-group">
            <div class="stat-label">Stations Visible</div>
            <div class="stat-value" id="stat-count">0</div>
            <div class="stat-sub" style="font-size: 13px; color: #64748b;">Matching filters</div>
        </div>
        <div class="stat-group">
            <div class="stat-label">Total Plugs</div>
            <div class="stat-value" id="stat-plugs" style="color: #3b82f6;">0</div>
        </div>
        <div class="legend">
            <div class="legend-item"><div class="dot" style="background:#EF4444;"></div>DC Fast</div>
            <div class="legend-item"><div class="dot" style="background:#3B82F6;"></div>AC Slow</div>
        </div>
    </div>

    <script>
        let allStations = [];
        let map;
        let activeMarkers = [];

        function initMap() {
            map = L.map('map').setView([20.5937, 78.9629], 5);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
                attribution: 'OSM &copy; CARTO', maxZoom: 19
            }).addTo(map);
        }

        async function loadData() {
            try {
                let res = await fetch('/api/data');
                let data = await res.json();
                if (Array.isArray(data)) {
                    if (data.length === 0) { setTimeout(loadData, 3000); return; }
                    allStations = data;
                    populateOperatorFilter(data);
                    applyFilters();
                }
            } catch (e) { setTimeout(loadData, 3000); }
        }

        function populateOperatorFilter(data) {
            let operators = new Set();
            data.forEach(s => { if(s.OperatorInfo && s.OperatorInfo.Title) operators.add(s.OperatorInfo.Title); });
            let sorted = Array.from(operators).sort();
            let select = document.getElementById('filter-operator');
            sorted.forEach(op => { let opt = document.createElement('option'); opt.value = op; opt.innerText = op; select.appendChild(opt); });
        }

        function applyFilters() {
            let typeFilter = document.getElementById('filter-type').value;
            let opFilter = document.getElementById('filter-operator').value;
            
            // Clear old markers
            activeMarkers.forEach(m => map.removeLayer(m));
            activeMarkers = [];
            
            let visibleCount = 0; let plugCount = 0;

            allStations.forEach(station => {
                let lat = station.AddressInfo ? station.AddressInfo.Latitude : null;
                let lng = station.AddressInfo ? station.AddressInfo.Longitude : null;
                if (!lat || !lng) return;
                
                let operator = (station.OperatorInfo && station.OperatorInfo.Title) ? station.OperatorInfo.Title : 'Unknown';
                if (opFilter !== 'all' && operator !== opFilter) return;
                
                let hasDC = false; 
                let plugs = station.Connections || [];
                plugs.forEach(c => { plugCount++; if (c.LevelID === 3 || (c.PowerKW && c.PowerKW > 20)) hasDC = true; });
                
                if (typeFilter === 'dc' && !hasDC) return;
                if (typeFilter === 'ac' && hasDC) return;

                let iconClass = hasDC ? 'marker-dc' : 'marker-ac';
                let icon = L.divIcon({ html: '<div class="'+iconClass+'"></div>', className: '', iconSize: hasDC ? [18, 18] : [14, 14], iconAnchor: [hasDC ? 9 : 7, hasDC ? 9 : 7] });
                let marker = L.marker([lat, lng], { icon: icon });
                
                let powerKW = hasDC ? (plugs.find(c=>c.PowerKW)?plugs.find(c=>c.PowerKW).PowerKW:'>20') : (plugs.find(c=>c.PowerKW)?plugs.find(c=>c.PowerKW).PowerKW:'<20');
                let badgeClass = hasDC ? 'badge-dc' : 'badge-ac'; 
                let badgeText = hasDC ? 'DC Fast' : 'AC Slow';
                
                let title = station.AddressInfo ? (station.AddressInfo.Title || 'Unknown') : 'Unknown';
                let address = station.AddressInfo ? (station.AddressInfo.AddressLine1 || '') : '';
                let state = station.AddressInfo ? (station.AddressInfo.StateOrProvince || '') : '';

                let popupContent = '<div><div class="popup-header"><div class="popup-title">'+title+'</div><div class="popup-address">'+address+', '+state+'</div></div><div class="popup-body"><div class="popup-row"><span class="popup-key">Network</span><span class="popup-val">'+operator+'</span></div><div class="popup-row" style="border-top: 1px solid #f1f5f9; padding-top: 10px; margin-top: 4px;"><span class="popup-key">Connectors</span><span class="popup-val"><span class="badge '+badgeClass+'">'+plugs.length+'x '+badgeText+'</span></span></div><div class="popup-row"><span class="popup-key">Power</span><span class="popup-val">'+powerKW+' kW</span></div></div></div>';
                
                marker.bindPopup(popupContent, { closeButton: false });
                marker.addTo(map); // Add directly to map, NO CLUSTERS
                activeMarkers.push(marker);
                visibleCount++;
            });
            document.getElementById('stat-count').innerText = visibleCount.toLocaleString();
            document.getElementById('stat-plugs').innerText = plugCount.toLocaleString();
        }

        function resetFilters() { 
            document.getElementById('filter-type').value = 'all'; 
            document.getElementById('filter-operator').value = 'all'; 
            applyFilters(); 
        }
        
        initMap(); 
        loadData();
    </script>
</body>
</html>
