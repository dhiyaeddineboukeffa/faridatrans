import requests
import json

API_URL = "http://localhost:8000"

def test_telemetry():
    # 1. Get stops to find a valid edge
    print("Fetching stops...")
    try:
        stops_res = requests.get(f"{API_URL}/stops")
        stops = stops_res.json()
        if not stops:
            print("No stops found.")
            return
        
        # Assume there is at least one edge. 
        # For this test, we'll try to find an edge or just use two stops and hope an edge exists or create one.
        # Actually, the telemetry endpoint updates an edge weight. If the edge doesn't exist, it might fail or just do nothing depending on implementation.
        # Let's check the code in main.py... 
        # It checks `if G.has_edge(data.u, data.v):`.
        
        # Let's create an edge first to be sure.
        u = stops[0]['id']
        v = stops[1]['id']
        
        print(f"Creating/Ensuring edge between {u} and {v}...")
        requests.post(f"{API_URL}/edges", json={
            "u": u, 
            "v": v, 
            "mode": "bus", 
            "duration": 120
        })
        
        # 2. Send telemetry
        print(f"Sending telemetry for edge {u} -> {v}...")
        telemetry_data = {
            "u": u,
            "v": v,
            "speed_mps": 15.0 # 15 m/s
        }
        
        res = requests.post(f"{API_URL}/telemetry", json=telemetry_data)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.json()}")
        
        if res.status_code == 200:
            print("Telemetry test PASSED")
        else:
            print("Telemetry test FAILED")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_telemetry()
