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
    mode: string;
    route?: string;
    duration: number;
    path_coordinates?: number[][];
    // Frontend computed properties
    count?: number;
    endTime?: number;
}

export interface RouteResponse {
    steps: RouteStep[];
    total_duration: number;
    transfers: number;
}

export interface UserLocation {
    lat: number;
    lon: number;
}
