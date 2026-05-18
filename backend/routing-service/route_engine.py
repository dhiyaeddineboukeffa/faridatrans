import json
import logging
import math
import heapq

logger = logging.getLogger(__name__)

class GraphEngine:
    def __init__(self, network_file="network_data.json"):
        logger.info(f"Loading network database from {network_file}...")
        try:
            with open(network_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.stations = data.get("nodes", {})
            self.edges = data.get("edges", [])
            logger.info(f"Loaded {len(self.stations)} stations and {len(self.edges)} edges.")
            self._build_graph()
        except Exception as e:
            logger.error(f"Failed to load network: {e}")
            self.stations = {}
            self.edges = []
            self.graph = {}

    def _build_graph(self):
        self.graph = {node_id: [] for node_id in self.stations}
        for edge in self.edges:
            u = edge['u']
            v = edge['v']
            if u in self.graph and v in self.graph:
                self.graph[u].append({
                    'to': v,
                    'mode': edge['mode'],
                    'route': edge.get('route'),
                    'duration': edge.get('duration', 0),
                    'weight': edge.get('weight', 0)
                })

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

    def compute_route(self, origin_id, dest_id, departure_time_sec=0):
        if origin_id not in self.stations or dest_id not in self.stations:
            logger.error(f"Cannot route. Unknown stations: {origin_id} or {dest_id}")
            return None

        # Dijkstra's Algorithm
        TRANSFER_PENALTY = 900 # 15 minutes penalty for transferring
        BOARDING_PENALTY = 300 # 5 minute penalty for getting on a bus/tram
        WALK_PENALTY_MULTIPLIER = 3.0 # Strongly discourage excessive walking

        # Priority Queue: (cost, current_node, current_route, path_length, visited_routes, path)
        import itertools
        counter = itertools.count()
        pq = [(0, next(counter), origin_id, None, 0, frozenset(), [])]
        best_cost = {}

        best_path = None
        min_final_cost = float('inf')

        while pq:
            cost, _, current_node, current_route, path_len, visited_routes, path = heapq.heappop(pq)

            if cost >= min_final_cost:
                continue

            state = (current_node, current_route, visited_routes)
            if state in best_cost and cost > best_cost[state]:
                continue
            best_cost[state] = cost

            if current_node == dest_id:
                if cost < min_final_cost:
                    min_final_cost = cost
                    best_path = path
                continue

            for edge in self.graph[current_node]:
                next_node = edge['to']
                next_route = edge['route']
                
                # Calculate cost and penalties
                edge_cost = edge['duration']
                if edge['mode'] == 'walk':
                    edge_cost *= WALK_PENALTY_MULTIPLIER

                penalty = 0
                wait_time = 0
                new_visited_routes = visited_routes
                if next_route is not None:
                    if next_route != current_route:
                        # Bus departs every 15 mins (900 seconds)
                        current_arrival_time = departure_time_sec + cost
                        remainder = current_arrival_time % 900
                        if remainder > 0:
                            wait_time = 900 - remainder

                        if next_route in visited_routes:
                            penalty += 999999
                        if current_route is not None:
                            penalty += TRANSFER_PENALTY
                        else:
                            penalty += BOARDING_PENALTY
                        new_visited_routes = visited_routes.union({next_route})
                else:
                    if current_route is not None:
                        penalty += BOARDING_PENALTY
                
                new_cost = cost + edge_cost + penalty + wait_time
                
                new_state = (next_node, next_route, new_visited_routes)
                if new_state not in best_cost or new_cost < best_cost[new_state]:
                    best_cost[new_state] = new_cost
                    new_step = {
                        'from_stop': current_node,
                        'to_stop': next_node,
                        'mode': edge['mode'],
                        'route_short': next_route if next_route else "WALK",
                        'route_long': f"Route {next_route}" if next_route else "Walk",
                        'duration': edge['duration'],
                        'wait_time': wait_time
                    }
                    heapq.heappush(pq, (new_cost, next(counter), next_node, next_route, path_len + 1, new_visited_routes, path + [new_step]))

        if not best_path:
            return None

        # Reconstruct legs
        legs = []
        current_time = departure_time_sec
        transfers = 0
        
        for i, step in enumerate(best_path):
            from_stop = step['from_stop']
            to_stop = step['to_stop']
            from_name = self.stations[from_stop]['name']
            to_name = self.stations[to_stop]['name']
            
            if i > 0 and step['route_short'] != best_path[i-1]['route_short'] and step['mode'] != 'walk':
                transfers += 1
                current_time += TRANSFER_PENALTY

            arr_time = current_time + step['duration']
            
            lat1, lon1 = self.stations[from_stop]['lat'], self.stations[from_stop]['lon']
            lat2, lon2 = self.stations[to_stop]['lat'], self.stations[to_stop]['lon']
            
            leg = {
                'from_stop': from_stop,
                'to_stop': to_stop,
                'from_name': from_name,
                'to_name': to_name,
                'mode': step['mode'],
                'route_short': step['route_short'],
                'route_long': step['route_long'],
                'dep_time': current_time,
                'arr_time': arr_time,
                'duration': step['duration'],
                'path_coordinates': [[lat1, lon1], [lat2, lon2]]
            }
            legs.append(leg)
            current_time = arr_time

        # Merge consecutive legs on the same route
        merged_legs = []
        for leg in legs:
            if not merged_legs:
                merged_legs.append(leg)
                continue
                
            last = merged_legs[-1]
            if last['mode'] == leg['mode'] and last['route_short'] == leg['route_short']:
                last['to_stop'] = leg['to_stop']
                last['to_name'] = leg['to_name']
                last['arr_time'] = leg['arr_time']
                last['duration'] += leg['duration']
                last['path_coordinates'].extend(leg['path_coordinates'][1:])
            else:
                merged_legs.append(leg)

        # Now fetch OSRM path for each merged leg
        import requests
        for m_leg in merged_legs:
            if m_leg['mode'] != 'walk' and len(m_leg['path_coordinates']) > 1:
                coords_str = ";".join([f"{lon},{lat}" for lat, lon in m_leg['path_coordinates']])
                url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?geometries=geojson&overview=full"
                try:
                    resp = requests.get(url, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get('code') == 'Ok' and len(data.get('routes', [])) > 0:
                            osrm_coords = data['routes'][0]['geometry']['coordinates']
                            m_leg['path_coordinates'] = [[lat, lon] for lon, lat in osrm_coords]
                except Exception as e:
                    logger.error(f"Failed to fetch OSRM multi-point route: {e}")

        total_cost_dzd = len(set(m['route_short'] for m in merged_legs if m['mode'] != 'walk')) * 40

        return {
            'legs': merged_legs,
            'total_duration': current_time - departure_time_sec,
            'transfers': transfers,
            'cost': total_cost_dzd
        }
