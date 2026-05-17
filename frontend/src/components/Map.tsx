'use client';

import { useMemo, useState } from 'react';
import Map, { Marker, Source, Layer, NavigationControl, FullscreenControl, GeolocateControl } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { Vehicle, Stop, RouteStep, UserLocation } from '@/types';

interface MapProps {
  vehicles: Vehicle[];
  stops: Stop[];
  routePath?: RouteStep[];
  userLocation?: UserLocation | null;
}

export default function TransitMap({ vehicles = [], stops = [], routePath, userLocation }: MapProps) {
  const [viewState, setViewState] = useState({
    longitude: 6.615,
    latitude: 36.365,
    zoom: 13,
    pitch: 45,
    bearing: 0
  });

  // Calculate GeoJSON for polylines using useMemo to avoid recalculation
  const routeGeojson = useMemo(() => {
    if (!routePath || routePath.length === 0) return null;

    const features: any[] = [];
    routePath.forEach((step, index) => {
      let coordinates: any[] = [];
      
      if (step.path_coordinates && step.path_coordinates.length > 0) {
        // MapLibre expects [lon, lat]
        coordinates = step.path_coordinates.map(([lat, lon]) => [lon, lat]);
      } else {
        // fallback to start and end
        const fromStop = stops.find(s => s.id === step.from_stop);
        const toStop = stops.find(s => s.id === step.to_stop);
        if (fromStop && toStop) {
          coordinates = [[fromStop.lon, fromStop.lat], [toStop.lon, toStop.lat]];
        }
      }

      if (coordinates.length > 0) {
        features.push({
          type: 'Feature',
          properties: {
            mode: step.mode,
            color: step.mode === 'walk' ? '#9CA3AF' : step.mode === 'tram' ? '#EF4444' : '#3B82F6',
          },
          geometry: {
            type: 'LineString',
            coordinates: coordinates
          }
        });
      }
    });

    return {
      type: 'FeatureCollection' as const,
      features
    };
  }, [routePath, stops]);

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <Map
        {...viewState}
        onMove={evt => setViewState(evt.viewState)}
        mapStyle={`https://basemaps.cartocdn.com/gl/positron-gl-style/style.json`}
        styleDiffing
      >
        <NavigationControl position="top-right" />
        <GeolocateControl position="top-right" />
        <FullscreenControl position="top-right" />

        {/* User Marker */}
        {userLocation && (
          <Marker longitude={userLocation.lon} latitude={userLocation.lat} color="#10B981" />
        )}

        {/* Stops Markers */}
        {stops.map((stop) => {
          const color =
            stop.type === 'tram' ? '#EF4444' :   // red
            stop.type === 'bus'  ? '#3B82F6' :   // blue
                                   '#6B7280';    // gray fallback

          return (
            <Marker key={`stop-${stop.id}`} longitude={stop.lon} latitude={stop.lat}>
              <div
                title={stop.name}
                style={{
                  width: 12,
                  height: 12,
                  backgroundColor: 'white',
                  border: `2.5px solid ${color}`,
                  borderRadius: '50%',
                  boxShadow: '0 1px 4px rgba(0,0,0,0.3)',
                  cursor: 'pointer',
                }}
              />
            </Marker>
          );
        })}

        {/* Vehicle Markers */}
        {vehicles.map((vehicle) => (
          <Marker key={`vehicle-${vehicle.id}`} longitude={vehicle.lon} latitude={vehicle.lat}>
            <div className="flex items-center justify-center w-8 h-8 text-white text-xs font-bold rounded-full shadow-lg"
                 style={{ backgroundColor: vehicle.type === 'tram' ? '#EF4444' : '#3B82F6' }}>
              {vehicle.type === 'tram' ? 'T' : 'B'}
            </div>
          </Marker>
        ))}

        {/* Route Polylines from GeoJSON */}
        {routeGeojson && (
          <Source id="route-source" type="geojson" data={routeGeojson}>
            {/* Walk dashed lines */}
            <Layer 
              id="route-walk-layer"
              type="line"
              filter={['==', 'mode', 'walk']}
              layout={{
                'line-join': 'round',
                'line-cap': 'round'
              }}
              paint={{
                'line-color': ['get', 'color'],
                'line-width': 4,
                'line-dasharray': [2, 2]
              }}
            />
            {/* Transit solid lines */}
            <Layer 
              id="route-transit-layer"
              type="line"
              filter={['!=', 'mode', 'walk']}
              layout={{
                'line-join': 'round',
                'line-cap': 'round'
              }}
              paint={{
                'line-color': ['get', 'color'],
                'line-width': 6
              }}
            />
          </Source>
        )}
      </Map>
    </div>
  );
}
