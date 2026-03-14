import pandas as pd
import math
from bisect import bisect_left
import json
import logging
import os

logger = logging.getLogger(__name__)

class CSAEngine:
    def __init__(self, gtfs_dir):
        logger.info(f"Loading GTFS data from {gtfs_dir}...")
        self.stops_df = pd.read_csv(f"{gtfs_dir}/stops.txt")
        self.stop_times_df = pd.read_csv(f"{gtfs_dir}/stop_times.txt")
        self.trips_df = pd.read_csv(f"{gtfs_dir}/trips.txt")
        self.routes_df = pd.read_csv(f"{gtfs_dir}/routes.txt")
        
        shapes_path = f"{gtfs_dir}/shapes.txt"
        if os.path.exists(shapes_path):
            self.shapes_df = pd.read_csv(shapes_path)
            self.shapes = {}
            for shape_id, group in self.shapes_df.groupby('shape_id'):
                group = group.sort_values(by='shape_pt_sequence')
                self.shapes[shape_id] = list(zip(group['shape_pt_lat'], group['shape_pt_lon']))
        else:
            self.shapes = {}
            
        self.stops = {}
        for _, row in self.stops_df.iterrows():
            self.stops[row['stop_id']] = {
                'name': row['stop_name'],
                'lat': row['stop_lat'],
                'lon': row['stop_lon']
            }
            
        self.trip_info = {}
        for _, row in self.trips_df.iterrows():
            self.trip_info[row['trip_id']] = {
                'route_id': row['route_id'],
                'shape_id': row.get('shape_id')
            }
            
        self.route_info = {
            row['route_id']: {
                'short_name': row['route_short_name'],
                'long_name': row['route_long_name']
            }
            for _, row in self.routes_df.iterrows()
        }
            
        self._build_connections()
        self._build_footpaths()
        
    def _time_to_seconds(self, t_str):
        h, m, s = map(int, t_str.split(':'))
        return h * 3600 + m * 60 + s
        
    def _build_connections(self):
        logger.info("Building vehicular connections array...")
        # Sort stop_times by trip and sequence
        st = self.stop_times_df.sort_values(by=['trip_id', 'stop_sequence'])
        
        self.connections = []
        
        # Iterate over trips
        for trip_id, group in st.groupby('trip_id'):
            route_id = self.trip_info[trip_id]['route_id']
            stops = group['stop_id'].tolist()
            arr_times = group['arrival_time'].tolist()
            dep_times = group['departure_time'].tolist()
            
            for i in range(len(stops) - 1):
                dep_sec = self._time_to_seconds(dep_times[i])
                arr_sec = self._time_to_seconds(arr_times[i+1])
                self.connections.append({
                    'dep_stop': stops[i],
                    'arr_stop': stops[i+1],
                    'dep_time': dep_sec,
                    'arr_time': arr_sec,
                    'trip_id': trip_id,
                    'route_id': route_id
                })
        
        # CSA requires connections sorted by departure time ascending
        self.connections.sort(key=lambda x: x['dep_time'])
        self.dep_times = [c['dep_time'] for c in self.connections]
        logger.info(f"Loaded {len(self.connections)} connections.")

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        return 2 * R * math.asin(math.sqrt(math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2))

    def _build_footpaths(self):
        logger.info("Building footpaths...")
        self.footpaths = {stop_id: [] for stop_id in self.stops}
        
        stop_ids = list(self.stops.keys())
        for i in range(len(stop_ids)):
            for j in range(i + 1, len(stop_ids)):
                s1, s2 = stop_ids[i], stop_ids[j]
                lat1, lon1 = self.stops[s1]['lat'], self.stops[s1]['lon']
                lat2, lon2 = self.stops[s2]['lat'], self.stops[s2]['lon']
                dist = self._haversine(lat1, lon1, lat2, lon2)
                
                if dist <= 400: # 400 meters max walking distance between stops
                    walk_time = int(dist / 1.4) # 1.4 m/s
                    self.footpaths[s1].append({'target': s2, 'duration': walk_time})
                    self.footpaths[s2].append({'target': s1, 'duration': walk_time})

    def nearest_stop(self, lat, lon):
        min_dist = float('inf')
        nearest = None
        for stop_id, data in self.stops.items():
            dist = self._haversine(lat, lon, data['lat'], data['lon'])
            if dist < min_dist:
                min_dist = dist
                nearest = stop_id
        return nearest, min_dist

    def compute_route(self, origin_stop, dest_stop, departure_time_sec):
        # 1. Initialization
        arrival_times = {stop_id: float('inf') for stop_id in self.stops}
        trip_reached = {trip_id: False for trip_id in self.trip_info}
        
        journey_pointers = {}
        
        arrival_times[origin_stop] = departure_time_sec
        # Expand origin with footpaths immediately
        for fp in self.footpaths[origin_stop]:
            arr = departure_time_sec + fp['duration']
            if arr < arrival_times[fp['target']]:
                arrival_times[fp['target']] = arr
                journey_pointers[fp['target']] = {
                    'mode': 'walk',
                    'prev_stop': origin_stop,
                    'arr_time': arr,
                    'dep_time': departure_time_sec
                }

        # 2. Find start index
        start_idx = bisect_left(self.dep_times, departure_time_sec)
        
        # 3. Connection Scan
        for c in self.connections[start_idx:]:
            if arrival_times[dest_stop] <= c['dep_time']:
                break # We already found a path that arrives before this connection even departs!
                
            if trip_reached[c['trip_id']] or arrival_times[c['dep_stop']] <= c['dep_time']:
                trip_reached[c['trip_id']] = True
                
                if c['arr_time'] < arrival_times[c['arr_stop']]:
                    # Better arrival time found!
                    arrival_times[c['arr_stop']] = c['arr_time']
                    journey_pointers[c['arr_stop']] = {
                        'mode': 'bus',
                        'prev_stop': c['dep_stop'],
                        'arr_time': c['arr_time'],
                        'dep_time': c['dep_time'],
                        'route_id': c['route_id'],
                        'trip_id': c['trip_id'],
                        'shape_id': self.trip_info[c['trip_id']]['shape_id']
                    }
                    
                    # Also evaluate footpaths from this new arrival
                    for fp in self.footpaths[c['arr_stop']]:
                        fp_arr = c['arr_time'] + fp['duration']
                        if fp_arr < arrival_times[fp['target']]:
                            arrival_times[fp['target']] = fp_arr
                            journey_pointers[fp['target']] = {
                                'mode': 'walk',
                                'prev_stop': c['arr_stop'],
                                'arr_time': fp_arr,
                                'dep_time': c['arr_time'] # Walk starts right after bus arrives
                            }
                            
        # 4. Reconstruct journey
        if arrival_times[dest_stop] == float('inf'):
            return None # No route found
            
        legs = []
        curr = dest_stop
        while curr != origin_stop:
            ptr = journey_pointers.get(curr)
            if not ptr:
                break
                
            prev = ptr['prev_stop']
            
            # Format leg
            leg = {
                'from_stop': prev,
                'to_stop': curr,
                'from_name': self.stops[prev]['name'],
                'to_name': self.stops[curr]['name'],
                'mode': ptr['mode'],
                'dep_time': ptr['dep_time'],
                'arr_time': ptr['arr_time'],
                'duration': ptr['arr_time'] - ptr['dep_time'],
                'path_coordinates': []
            }
            
            if ptr['mode'] == 'bus':
                leg['route_short'] = self.route_info[ptr['route_id']]['short_name']
                leg['route_long'] = self.route_info[ptr['route_id']]['long_name']
                
                shape_id = ptr.get('shape_id')
                if shape_id and shape_id in self.shapes:
                    # In a real system, we'd slice the shape array between prev and curr stops.
                    # Since generate_gtfs generates exactly one shape per pair of stops right now,
                    # we can just use the whole shape array for this connection!
                    # If this connection is just one segment:
                    leg['path_coordinates'] = self.shapes[shape_id]
                else:
                    leg['path_coordinates'] = [
                        [self.stops[prev]['lat'], self.stops[prev]['lon']],
                        [self.stops[curr]['lat'], self.stops[curr]['lon']]
                    ]
            else:
                 leg['path_coordinates'] = [
                    [self.stops[prev]['lat'], self.stops[prev]['lon']],
                    [self.stops[curr]['lat'], self.stops[curr]['lon']]
                ]
                
            legs.append(leg)
            curr = prev
            
        legs.reverse()
        
        # Merge consecutive walk legs or consecutive bus legs of same trip if needed
        merged_legs = []
        for leg in legs:
            if not merged_legs:
                merged_legs.append(leg)
                continue
                
            last = merged_legs[-1]
            if last['mode'] == 'bus' and leg['mode'] == 'bus' and last.get('route_short') == leg.get('route_short'):
                # Merge bus legs
                last['to_stop'] = leg['to_stop']
                last['to_name'] = leg['to_name']
                last['arr_time'] = leg['arr_time']
                last['duration'] += leg['duration']
                # Try to stitch coordinates end-to-end reasonably
                if last['path_coordinates'] and leg['path_coordinates']:
                    # Remove the first coordinate if it's identical to the last one
                    if last['path_coordinates'][-1] == leg['path_coordinates'][0]:
                        last['path_coordinates'].extend(leg['path_coordinates'][1:])
                    else:
                        last['path_coordinates'].extend(leg['path_coordinates'])
                else:
                    last['path_coordinates'].extend(leg['path_coordinates'][1:])
            elif last['mode'] == 'walk' and leg['mode'] == 'walk':
                # Merge walk legs
                last['to_stop'] = leg['to_stop']
                last['to_name'] = leg['to_name']
                last['arr_time'] = leg['arr_time']
                last['duration'] += leg['duration']
                if last['path_coordinates'] and leg['path_coordinates']:
                    last['path_coordinates'][-1] = leg['path_coordinates'][-1]
            else:
                merged_legs.append(leg)

        return {
            'legs': merged_legs,
            'total_duration': arrival_times[dest_stop] - departure_time_sec,
            'transfers': sum(1 for l in merged_legs if l['mode'] == 'bus') - 1
        }
