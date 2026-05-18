export interface Stop {
    id: string;
    name: string;
    lat: number;
    lon: number;
    type?: string;
}

export interface Vehicle {
    id: string;
    route: string;
    lat: number;
    lon: number;
    status: string;
    type?: string;
    timestamp?: number;
}

export interface RouteStep {
    from_stop: string;
    to_stop: string;
    from_name?: string;
    to_name?: string;
    mode: string;
    route?: string;
    route_short?: string;
    route_long?: string;
    duration: number;
    dep_time?: number;
    arr_time?: number;
    path_coordinates?: number[][];
    wait_time?: number;
    // Frontend computed properties
    count?: number;
    endTime?: number;
}

export interface RouteResponse {
    steps: RouteStep[];
    total_duration: number;
    transfers: number;
    cost?: number;
}

export interface UserLocation {
    lat: number;
    lon: number;
}
