import webbrowser
import os

def generate_map_html(lat: float, lon: float, city: str):
    """Generates and opens a simple HTML map file."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Location: {city}</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>#map {{ height: 500px; width: 100%; }}</style>
    </head>
    <body>
        <h1>Location: {city}</h1>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{lat}, {lon}], 13);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '&copy; OpenStreetMap contributors'
            }}).addTo(map);
            L.marker([{lat}, {lon}]).addTo(map).bindPopup('{city}').openPopup();
        </script>
    </body>
    </html>
    """
    with open("map.html", "w") as f:
        f.write(html)
    
    webbrowser.open('file://' + os.path.realpath("map.html"))
