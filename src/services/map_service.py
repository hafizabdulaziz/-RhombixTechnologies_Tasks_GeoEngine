import webbrowser
import os

def get_map_html(lat: float, lon: float, city: str) -> str:
    """Generates Leaflet HTML code as a string for a given location."""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Location: {city}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        html, body, #map {{ height: 100%; width: 100%; margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([{lat}, {lon}], 13);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);
        L.marker([{lat}, {lon}]).addTo(map).bindPopup('{city}').openPopup();
    </script>
</body>
</html>"""

def generate_map_html(lat: float, lon: float, city: str) -> None:
    """Generates and opens a simple HTML map file."""
    html = get_map_html(lat, lon, city)
    with open("map.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    webbrowser.open('file://' + os.path.realpath("map.html"))
