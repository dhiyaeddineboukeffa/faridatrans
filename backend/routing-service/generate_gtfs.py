import pandas as pd
import openpyxl
import os
import zipfile
import re
from math import radians, cos, sin, asin, sqrt
import datetime
from osrm_helper import get_osrm_route
import time

EXCEL_PATH = r"../../BUS DE CONSTANTINE.xlsx"
OUTPUT_DIR = r"gtfs"

def parse_coords(raw):
    if pd.isna(raw) or not raw:
        return None, None
    parts = re.split(r'[,\s]+', str(raw).strip())
    parts = [p for p in parts if p]
    if len(parts) >= 2:
        try:
            return float(parts[0]), float(parts[1])
        except ValueError:
            return None, None
    return None, None

def slugify(name):
    return str(name).strip().upper().replace(" ", "_").replace("'", "").replace("-", "_")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

def format_time(seconds_since_midnight):
    h = int(seconds_since_midnight // 3600)
    m = int((seconds_since_midnight % 3600) // 60)
    s = int(seconds_since_midnight % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_excel(EXCEL_PATH)
    
    agency = [{"agency_id": "farida", "agency_name": "Farida Transit", "agency_url": "http://farida.dz", "agency_timezone": "Africa/Algiers"}]
    
    stops = {}
    routes = []
    trips = []
    stop_times = []
    shapes = []
    shape_ids = {} # (dep_id, arr_id) -> shape_id
    calendar = [{"service_id": "everyday", "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1, "saturday": 1, "sunday": 1, "start_date": "20240101", "end_date": "20301231"}]
    
    for index, row in df.iterrows():
        line_num = row['Numero DE LIGNE']
        dep_name = row['Depart']
        dep_coords = row['Localisation']
        arr_name = row['Arrive']
        arr_coords = row['Localisation.1']
        
        if pd.isna(dep_name) or pd.isna(arr_name):
            continue
            
        dep_lat, dep_lon = parse_coords(dep_coords)
        arr_lat, arr_lon = parse_coords(arr_coords)
        
        if dep_lat is None or arr_lat is None:
            continue
            
        dep_id = slugify(dep_name)
        arr_id = slugify(arr_name)
        route_id = f"L{line_num}"
        
        if dep_id not in stops:
            stops[dep_id] = {"stop_id": dep_id, "stop_name": str(dep_name).strip(), "stop_lat": dep_lat, "stop_lon": dep_lon}
        if arr_id not in stops:
            stops[arr_id] = {"stop_id": arr_id, "stop_name": str(arr_name).strip(), "stop_lat": arr_lat, "stop_lon": arr_lon}
            
        routes.append({
            "route_id": route_id,
            "agency_id": "farida",
            "route_short_name": str(line_num),
            "route_long_name": f"{dep_name} - {arr_name}",
            "route_type": 3 # Bus
        })
        
        # Calculate duration
        dist_m = haversine(dep_lat, dep_lon, arr_lat, arr_lon)
        duration_sec = int(dist_m / (30 * 1000 / 3600)) # 30 km/h

        # Generate Shapes via OSRM
        fwd_shape_id = f"shape_{dep_id}_{arr_id}"
        bwd_shape_id = f"shape_{arr_id}_{dep_id}"
        
        if (dep_id, arr_id) not in shape_ids:
            # Fetch shape from OSRM
            print(f"Fetching OSRM route: {dep_id} -> {arr_id}")
            route_coords = get_osrm_route(dep_lat, dep_lon, arr_lat, arr_lon)
            for seq, (lat, lon) in enumerate(route_coords):
                shapes.append({"shape_id": fwd_shape_id, "shape_pt_lat": lat, "shape_pt_lon": lon, "shape_pt_sequence": seq + 1})
            shape_ids[(dep_id, arr_id)] = fwd_shape_id
            time.sleep(0.2) # Rate limiting
            
        if (arr_id, dep_id) not in shape_ids:
            print(f"Fetching OSRM route: {arr_id} -> {dep_id}")
            route_coords = get_osrm_route(arr_lat, arr_lon, dep_lat, dep_lon)
            for seq, (lat, lon) in enumerate(route_coords):
                shapes.append({"shape_id": bwd_shape_id, "shape_pt_lat": lat, "shape_pt_lon": lon, "shape_pt_sequence": seq + 1})
            shape_ids[(arr_id, dep_id)] = bwd_shape_id
            time.sleep(0.2)

        
        # Synthetic Trips: Every 15 minutes from 06:00 to 20:00
        start_time_sec = 6 * 3600
        end_time_sec = 20 * 3600
        freq_sec = 15 * 60
        
        trip_idx = 1
        for t in range(start_time_sec, end_time_sec, freq_sec):
            # Forward trip
            fwd_trip_id = f"{route_id}_F_{trip_idx}"
            trips.append({"route_id": route_id, "service_id": "everyday", "trip_id": fwd_trip_id, "direction_id": 0, "shape_id": fwd_shape_id})
            
            stop_times.append({"trip_id": fwd_trip_id, "arrival_time": format_time(t), "departure_time": format_time(t), "stop_id": dep_id, "stop_sequence": 1})
            stop_times.append({"trip_id": fwd_trip_id, "arrival_time": format_time(t + duration_sec), "departure_time": format_time(t + duration_sec), "stop_id": arr_id, "stop_sequence": 2})
            
            # Backward trip
            bwd_trip_id = f"{route_id}_B_{trip_idx}"
            trips.append({"route_id": route_id, "service_id": "everyday", "trip_id": bwd_trip_id, "direction_id": 1, "shape_id": bwd_shape_id})
            
            stop_times.append({"trip_id": bwd_trip_id, "arrival_time": format_time(t), "departure_time": format_time(t), "stop_id": arr_id, "stop_sequence": 1})
            stop_times.append({"trip_id": bwd_trip_id, "arrival_time": format_time(t + duration_sec), "departure_time": format_time(t + duration_sec), "stop_id": dep_id, "stop_sequence": 2})
            
            trip_idx += 1

    # Write CSVs
    pd.DataFrame(agency).to_csv(os.path.join(OUTPUT_DIR, "agency.txt"), index=False)
    pd.DataFrame(list(stops.values())).to_csv(os.path.join(OUTPUT_DIR, "stops.txt"), index=False)
    pd.DataFrame(routes).drop_duplicates("route_id").to_csv(os.path.join(OUTPUT_DIR, "routes.txt"), index=False)
    pd.DataFrame(trips).to_csv(os.path.join(OUTPUT_DIR, "trips.txt"), index=False)
    pd.DataFrame(stop_times).to_csv(os.path.join(OUTPUT_DIR, "stop_times.txt"), index=False)
    pd.DataFrame(calendar).to_csv(os.path.join(OUTPUT_DIR, "calendar.txt"), index=False)
    pd.DataFrame(shapes).to_csv(os.path.join(OUTPUT_DIR, "shapes.txt"), index=False)
    
    print("GTFS files created successfully in gtfs/")

if __name__ == "__main__":
    main()
