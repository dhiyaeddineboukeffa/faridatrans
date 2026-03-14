import json
import logging
import requests
import math

logger = logging.getLogger(__name__)

class ProximityEngine:
    def __init__(self, stations_file="stations.json"):
        logger.info(f"Loading stations database from {stations_file}...")
        try:
            with open(stations_file, 'r') as f:
                self.stations_list = json.load(f)
            self.stations = {s['id']: s for s in self.stations_list}
            logger.info(f"Loaded {len(self.stations)} stations.")
        except Exception as e:
            logger.error(f"Failed to load stations: {e}")
            self.stations = {}
            self.stations_list = []

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        return 2 * R * math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))

    def nearest_stop(self, lat, lon):
        min_dist = float('inf')
        nearest = None
        for stop_id, data in self.stations.items():
            dist = self._haversine(lat, lon, data['lat'], data['lon'])
            if dist < min_dist:
                min_dist = dist
                nearest = stop_id
        return nearest, min_dist

    def _point_to_segment_dist(self, px, py, p1x, p1y, p2x, p2y):
        l2 = (p1x - p2x)**2 + (p1y - p2y)**2
        if l2 == 0:
            return math.hypot(px - p1x, py - p1y), 0
        t = max(0, min(1, ((px - p1x) * (p2x - p1x) + (py - p1y) * (p2y - p1y)) / l2))
        proj_x = p1x + t * (p2x - p1x)
        proj_y = p1y + t * (p2y - p1y)
        return math.hypot(px - proj_x, py - proj_y), t

    def compute_route(self, origin_id, dest_id, departure_time_sec=0):
        if origin_id not in self.stations or dest_id not in self.stations:
            logger.error(f"Cannot route. Unknown stations: {origin_id} or {dest_id}")
            return None

        origin = self.stations[origin_id]
        dest = self.stations[dest_id]

        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{origin['lon']},{origin['lat']};{dest['lon']},{dest['lat']}?geometries=geojson&overview=full"
        try:
            resp = requests.get(osrm_url)
            data = resp.json()
            if data['code'] != 'Ok':
                logger.error(f"OSRM returned error: {data['code']}")
                return None
            
            route = data['routes'][0]
            path_coords = route['geometry']['coordinates'] # [lon, lat]
            total_duration_sec = route['duration']
            total_distance_m = route['distance']
            
        except Exception as e:
            logger.error(f"Failed OSRM Request: {e}")
            return None

        TOLERANCE_DEG = 0.0018 
        
        selected_stations = []
        
        for s in self.stations_list:
            if s['id'] == origin_id or s['id'] == dest_id:
                continue
                
            px, py = s['lon'], s['lat']
            min_dist = float('inf')
            best_progression = 0
            
            # Find the closest segment on the polyline to this point
            for i in range(len(path_coords) - 1):
                p1x, p1y = path_coords[i]
                p2x, p2y = path_coords[i+1]
                
                dist, t = self._point_to_segment_dist(px, py, p1x, p1y, p2x, p2y)
                if dist < min_dist:
                    min_dist = dist
                    best_progression = i + t
                    
            if min_dist <= TOLERANCE_DEG:
                selected_stations.append({
                    'station': s,
                    'progression': best_progression,
                    'distance_to_line': min_dist
                })
                
        # Sort nodes by progression order from Origin to Destination
        selected_stations.sort(key=lambda x: x['progression'])
        
        route_sequence = [origin] + [x['station'] for x in selected_stations] + [dest]
        
        # Build array of progression indices to slice the OSRM path
        progressions = [0] + [int(x['progression']) for x in selected_stations] + [len(path_coords) - 1]
        
        legs = []
        for i in range(len(route_sequence) - 1):
            curr_s = route_sequence[i]
            next_s = route_sequence[i+1]
            
            # Slice the OSRM path using the progression indices we collected
            start_idx = progressions[i]
            end_idx = progressions[i+1]
            
            # Ensure at least two points (start and end) exist if they mapped to the same segment index
            if start_idx >= end_idx:
                sliced_coords = [[curr_s['lat'], curr_s['lon']], [next_s['lat'], next_s['lon']]]
            else:
                # OSRM path is [lon, lat], but our UI expects [lat, lon]
                sliced_coords = [[lat, lon] for lon, lat in path_coords[start_idx:end_idx+1]]
                # Force the first and last point to snap exactly to the station coordinates to prevent gaps
                sliced_coords[0] = [curr_s['lat'], curr_s['lon']]
                sliced_coords[-1] = [next_s['lat'], next_s['lon']]
            
            leg = {
                'from_stop': curr_s['id'],
                'to_stop': next_s['id'],
                'from_name': curr_s['name'],
                'to_name': next_s['name'],
                'mode': 'bus',
                'route_short': "PROXIMITY",
                'route_long': "Geometric Directed Trace",
                'dep_time': departure_time_sec + int((i/len(route_sequence)) * total_duration_sec),
                'arr_time': departure_time_sec + int(((i+1)/len(route_sequence)) * total_duration_sec),
                'duration': int(total_duration_sec / max(1, len(route_sequence))),
                'path_coordinates': sliced_coords
            }
            legs.append(leg)

        return {
            'legs': legs,
            'total_duration': total_duration_sec,
            'transfers': 0 
        }
