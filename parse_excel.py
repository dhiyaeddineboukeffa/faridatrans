"""
ETL Script: Parse BUS DE CONSTANTINE.xlsx → network_data.json
"""
import openpyxl
import json
import re

EXCEL_PATH = r"BUS DE CONSTANTINE.xlsx"
OUTPUT_PATH = r"backend/routing-service/network_data.json"

def parse_coords(raw):
    """Parse a string like '36.5663 , 6.7369' into (lat, lon)."""
    if not raw:
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
    """Create a simple stop ID from a name."""
    return name.strip().upper().replace(" ", "_").replace("'", "").replace("-", "_")

wb = openpyxl.load_workbook(EXCEL_PATH)
ws = wb.active

nodes = {}  # id -> {name, lat, lon, type}
edges = []  # {u, v, mode, route, duration, weight}

for row in ws.iter_rows(min_row=2, values_only=True):
    line_num, dep_name, dep_coords, arr_name, arr_coords = row[0], row[1], row[2], row[3], row[4]

    if not dep_name or not arr_name:
        continue

    dep_lat, dep_lon = parse_coords(dep_coords)
    arr_lat, arr_lon = parse_coords(arr_coords)

    if dep_lat is None or arr_lat is None:
        print(f"  [SKIP] Missing coords on line {line_num}: {dep_name} -> {arr_name}")
        continue

    dep_id = slugify(str(dep_name))
    arr_id = slugify(str(arr_name))
    route_id = f"L{line_num}"

    # Add nodes (stops) — deduplicate by ID
    if dep_id not in nodes:
        nodes[dep_id] = {"name": str(dep_name).strip(), "lat": dep_lat, "lon": dep_lon, "type": "bus"}
    if arr_id not in nodes:
        nodes[arr_id] = {"name": str(arr_name).strip(), "lat": arr_lat, "lon": arr_lon, "type": "bus"}

    # Estimate duration based on straight-line distance (avg bus speed ~30 km/h)
    from math import radians, cos, sin, asin, sqrt
    R = 6371000  # Earth radius in meters
    lat1, lon1 = radians(dep_lat), radians(dep_lon)
    lat2, lon2 = radians(arr_lat), radians(arr_lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    dist_m = 2 * R * asin(sqrt(a))
    duration_sec = int(dist_m / (30 * 1000 / 3600))  # 30 km/h in m/s

    # Add edges forwards and backwards (bus routes are usually bidirectional)
    edges.append({"u": dep_id, "v": arr_id, "mode": "bus", "route": route_id, "duration": duration_sec, "weight": duration_sec})
    edges.append({"u": arr_id, "v": dep_id, "mode": "bus", "route": route_id, "duration": duration_sec, "weight": duration_sec})

# Add walking edges between stops that are close (< 400m)
from math import radians, cos, sin, asin, sqrt
stop_list = list(nodes.items())
walk_added = 0
for i in range(len(stop_list)):
    for j in range(i + 1, len(stop_list)):
        id_a, s_a = stop_list[i]
        id_b, s_b = stop_list[j]
        lat1, lon1 = radians(s_a['lat']), radians(s_a['lon'])
        lat2, lon2 = radians(s_b['lat']), radians(s_b['lon'])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        dist_m = 2 * 6371000 * asin(sqrt(a))
        if dist_m < 400:
            walk_sec = int(dist_m / 1.4)  # 1.4 m/s walking
            edges.append({"u": id_a, "v": id_b, "mode": "walk", "route": None, "duration": walk_sec, "weight": walk_sec})
            edges.append({"u": id_b, "v": id_a, "mode": "walk", "route": None, "duration": walk_sec, "weight": walk_sec})
            walk_added += 1

output = {"nodes": nodes, "edges": edges}
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Done!")
print(f"   Stops (nodes):  {len(nodes)}")
print(f"   Route edges:    {len([e for e in edges if e['mode'] == 'bus'])}")
print(f"   Walk edges:     {len([e for e in edges if e['mode'] == 'walk'])} (from {walk_added} pairs)")
print(f"   Output:         {OUTPUT_PATH}")
