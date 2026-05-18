from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Tuple
import uvicorn
import json
import os
import datetime
import logging
from contextlib import asynccontextmanager

from route_engine import GraphEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ALLOWED_ORIGINS = ["*"]

# --- State ---
class AppState:
    engine: Optional[GraphEngine] = None

state = AppState()

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state.engine = GraphEngine(network_file="network_data.json")
        logger.info("Application started, Graph engine loaded.")
        yield
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        logger.info("Application shutting down")

app = FastAPI(title="Farida Transit CSA API", lifespan=lifespan)

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
    departure_time: Optional[str] = None # format "HH:MM:SS"

class RouteStep(BaseModel):
    from_stop: str
    to_stop: str
    from_name: Optional[str] = None
    to_name: Optional[str] = None
    mode: str
    route_short: Optional[str] = None
    route_long: Optional[str] = None
    duration: float
    dep_time: Optional[int] = None
    arr_time: Optional[int] = None
    path_coordinates: Optional[List[List[float]]] = None

class RouteResponse(BaseModel):
    steps: List[RouteStep]
    total_duration: float
    transfers: int
    cost: Optional[int] = None

# --- Endpoints ---
@app.get("/stops")
async def get_stops():
    if not state.engine:
        return []
    return [
        {"id": stop_id, **data}
        for stop_id, data in state.engine.stations.items()
    ]

@app.post("/route", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    if not state.engine:
        raise HTTPException(status_code=500, detail="Routing engine not initialized")
        
    start_stop = request.origin
    total_walk_time = 0
    initial_leg = None
    
    departure_sec = 0
    if request.departure_time:
        try:
            h, m, s = map(int, request.departure_time.split(':'))
            departure_sec = h * 3600 + m * 60 + s
        except:
             departure_sec = 8 * 3600 # Default to 08:00:00
    else:
        # Default to 08:00:00 AM for simulated timetable
        departure_sec = 8 * 3600

    if request.origin_lat is not None and request.origin_lon is not None:
        nearest_stop, dist_m = state.engine.nearest_stop(request.origin_lat, request.origin_lon)
        if not nearest_stop:
            raise HTTPException(status_code=404, detail="No stops found near origin")
            
        start_stop = nearest_stop
        walk_duration = int(dist_m / 1.4)
        total_walk_time += walk_duration
        
        initial_leg = RouteStep(
            from_stop="origin",
            to_stop=nearest_stop,
            from_name="Your Location",
            to_name=state.engine.stations[nearest_stop]['name'],
            mode="walk",
            duration=walk_duration,
            dep_time=departure_sec,
            arr_time=departure_sec + walk_duration,
            path_coordinates=[
                [request.origin_lat, request.origin_lon],
                [state.engine.stations[nearest_stop]['lat'], state.engine.stations[nearest_stop]['lon']]
            ]
        )
        departure_sec += walk_duration

    if not start_stop or start_stop not in state.engine.stations:
        raise HTTPException(status_code=404, detail="Origin not found")
        
    if request.destination not in state.engine.stations:
        raise HTTPException(status_code=404, detail="Destination not found")
        
    result = state.engine.compute_route(start_stop, request.destination, departure_sec)
    
    if not result:
        raise HTTPException(status_code=404, detail="No route found between these locations")
        
    steps_data = result['legs']
    steps = []
    if initial_leg:
        steps.append(initial_leg)
        
    for leg in steps_data:
        steps.append(RouteStep(
            from_stop=leg['from_stop'],
            to_stop=leg['to_stop'],
            from_name=leg['from_name'],
            to_name=leg['to_name'],
            mode=leg['mode'],
            route_short=leg.get('route_short'),
            route_long=leg.get('route_long'),
            duration=leg['duration'],
            dep_time=leg['dep_time'],
            arr_time=leg['arr_time'],
            path_coordinates=leg['path_coordinates']
        ))
        
    return RouteResponse(
        steps=steps,
        total_duration=result['total_duration'] + total_walk_time,
        transfers=result['transfers'],
        cost=result.get('cost', 0)
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
