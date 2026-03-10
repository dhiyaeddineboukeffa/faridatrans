from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import networkx as nx
import uvicorn
from geopy.distance import geodesic
import json
import os
import threading
import logging
import asyncio
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = 'vehicle_positions'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
DATA_FILE = "network_data.json"
# Restrict to localhost:3000 by default, but allow override
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# --- State ---
class AppState:
    G: nx.DiGraph = nx.DiGraph()
    vehicle_positions: Dict[str, Dict[str, Any]] = {}
    kafka_thread: Optional[threading.Thread] = None

state = AppState()

# --- Kafka Consumer ---
def consume_vehicle_positions():
    # Placeholder for Kafka consumer - would require additional setup
    # For now, simulating vehicle position updates with mock data
    try:
        logger.info("Vehicle position consumer started (mock mode)")
        # In a real app, this would consume from Kafka
        # consumer = KafkaConsumer(TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, ...)
        # for msg in consumer: ...
        pass
    except Exception as e:
        logger.error(f"Consumer error: {e}")

# --- Persistence ---
def save_data(graph: nx.DiGraph):
    data = {
        "nodes": {n: graph.nodes[n] for n in graph.nodes},
        "edges": []
    }
    for u, v, d in graph.edges(data=True):
        edge = d.copy()
        edge["u"] = u
        edge["v"] = v
        data["edges"].append(edge)
    
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_data():
    abs_path = os.path.abspath(DATA_FILE)
    logger.info(f"[load_data] Looking for data file at: {abs_path}")
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            
            G = nx.DiGraph()
            for n, attrs in data.get("nodes", {}).items():
                G.add_node(n, **attrs)
            
            for edge in data.get("edges", []):
                u = edge.pop("u")
                v = edge.pop("v")
                if "weight" not in edge:
                    edge["weight"] = edge.get("duration", 120)
                G.add_edge(u, v, **edge)
            logger.info(f"[load_data] Loaded {len(G.nodes)} nodes, {len(G.edges)} edges")
            return G
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return load_mock_data()
    else:
        logger.warning(f"[load_data] File not found, using mock data")
        G = load_mock_data()
        save_data(G)
        return G

def load_mock_data():
    """Load empty data as requested"""
    G = nx.DiGraph()
    # Mock data removed to ensure empty database
    return G

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        state.G = load_data()
        state.kafka_thread = threading.Thread(target=consume_vehicle_positions, daemon=True)
        state.kafka_thread.start()
        logger.info("Application started, data loaded, background threads running")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        # Shutdown (if needed)
        logger.info("Application shutting down")

app = FastAPI(title="Transit Navigator Routing Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class RouteRequest(BaseModel):
    origin: Optional[str] = None
    destination: str
    origin_lat: Optional[float] = None
    origin_lon: Optional[float] = None

class RouteStep(BaseModel):
    from_stop: str
    to_stop: str
    mode: str
    route: Optional[str] = None
    duration: float
    path_coordinates: Optional[List[List[float]]] = None

class RouteResponse(BaseModel):
    steps: List[RouteStep]
    total_duration: float
    transfers: int

class StopCreate(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    type: str = "bus"

class EdgeCreate(BaseModel):
    u: str
    v: str
    mode: str
    route: Optional[str] = None
    duration: int

# --- API Endpoints ---

@app.get("/vehicles")
async def get_vehicles():
    return list(state.vehicle_positions.values())

@app.get("/stops")
async def get_stops():
    return [{"id": n, **state.G.nodes[n]} for n in state.G.nodes]

# Admin Authentication
def verify_admin(x_admin_password: str = Header(...)):
    if x_admin_password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid admin password")
    return True

@app.post("/admin/stops", dependencies=[Depends(verify_admin)])
async def create_stop(stop: StopCreate):
    if stop.id in state.G:
        raise HTTPException(status_code=400, detail="Stop already exists")
    state.G.add_node(stop.id, name=stop.name, lat=stop.lat, lon=stop.lon, type=stop.type)
    save_data(state.G)
    return {"status": "success", "stop": stop}

@app.post("/admin/edges", dependencies=[Depends(verify_admin)])
async def create_edge(edge: EdgeCreate):
    if edge.u not in state.G or edge.v not in state.G:
        raise HTTPException(status_code=404, detail="One or both stops not found")
    
    state.G.add_edge(edge.u, edge.v, weight=edge.duration, mode=edge.mode, route=edge.route)
    save_data(state.G)
    return {"status": "success", "edge": edge}

# --- Routing Logic ---
def find_nearest_stop(lat: float, lon: float) -> Tuple[Optional[str], float]:
    min_dist = float('inf')
    nearest_stop = None
    
    for node in state.G.nodes:
        node_pos = (state.G.nodes[node]['lat'], state.G.nodes[node]['lon'])
        dist = geodesic((lat, lon), node_pos).meters
        if dist < min_dist:
            min_dist = dist
            nearest_stop = node
            
    return nearest_stop, min_dist

def heuristic(u, v):
    try:
        pos_u = (state.G.nodes[u]['lat'], state.G.nodes[u]['lon'])
        pos_v = (state.G.nodes[v]['lat'], state.G.nodes[v]['lon'])
        dist_m = geodesic(pos_u, pos_v).meters
        return dist_m / 22.0 # Assume fast travel
    except:
        return 0

def calculate_path_blocking(start_node, destination):
    """Blocking wrapping of nx.astar_path for executor"""
    try:
        # Create a subgraph view or copy if needed for thread safety during heavy reads
        # But for A* read-only on DiGraph is mostly fine in GIL if not mutating
        return nx.astar_path(state.G, source=start_node, target=destination, heuristic=heuristic, weight="weight")
    except nx.NetworkXNoPath:
        return None

@app.post("/route", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    start_node = request.origin
    
    # Handle coordinate-based origin
    initial_walk_step = None
    total_duration = 0.0
    
    if request.origin_lat is not None and request.origin_lon is not None:
        nearest_node, dist_m = find_nearest_stop(request.origin_lat, request.origin_lon)
        if not nearest_node:
            raise HTTPException(status_code=404, detail="No stops found in network")
            
        start_node = nearest_node
        walk_duration = dist_m / 1.4 # 1.4 m/s walking speed
        total_duration += walk_duration
        
        initial_walk_step = RouteStep(
            from_stop="Current Location",
            to_stop=nearest_node,
            mode="walk",
            duration=walk_duration,
            path_coordinates=[
                [request.origin_lat, request.origin_lon],
                [state.G.nodes[nearest_node]['lat'], state.G.nodes[nearest_node]['lon']]
            ]
        )

    if not start_node or start_node not in state.G:
        raise HTTPException(status_code=404, detail="Origin not found")
        
    if request.destination not in state.G:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    # Run blocking pathfinding in thread pool
    loop = asyncio.get_event_loop()
    path = await loop.run_in_executor(None, calculate_path_blocking, start_node, request.destination)
    
    if path is None:
        raise HTTPException(status_code=404, detail="No route found")
        
    steps = []
    if initial_walk_step:
        steps.append(initial_walk_step)
        
    transfers = 0
    last_mode = "walk" if initial_walk_step else None
    
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i+1]
        edge_data = state.G.get_edge_data(u, v)
        
        mode = edge_data.get("mode")
        if last_mode and mode != last_mode and mode != "walk":
            transfers += 1
        last_mode = mode
        
        duration = edge_data.get("weight")
        total_duration += duration
        
        # Get coordinates for path visualization
        u_pos = [state.G.nodes[u]['lat'], state.G.nodes[u]['lon']]
        v_pos = [state.G.nodes[v]['lat'], state.G.nodes[v]['lon']]
        
        steps.append(RouteStep(
            from_stop=u,
            to_stop=v,
            mode=mode,
            route=edge_data.get("route"),
            duration=duration,
            path_coordinates=[u_pos, v_pos]
        ))
        
    return RouteResponse(steps=steps, total_duration=total_duration, transfers=transfers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
