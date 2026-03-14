import requests
import time

def get_osrm_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?geometries=geojson&overview=full"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
            # OSRM returns coordinates as [lon, lat]
            # Convert to [lat, lon] for our use
            coords = data['routes'][0]['geometry']['coordinates']
            return [[lat, lon] for lon, lat in coords]
    except Exception as e:
        print(f"OSRM error for {lat1},{lon1} -> {lat2},{lon2}: {e}")
    # Fallback to straight line
    return [[lat1, lon1], [lat2, lon2]]
