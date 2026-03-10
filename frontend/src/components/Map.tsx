'use client';

import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import { Vehicle, Stop, RouteStep, UserLocation } from '@/types';

// Import Leaflet only on client side
let L: any = null;
if (typeof window !== 'undefined') {
  L = require('leaflet');
}

// Fix for default marker icon
if (typeof window !== 'undefined' && L) {
  const icon = L.icon({
    iconUrl: '/images/marker-icon.png',
    shadowUrl: '/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
  });
}


interface MapProps {
  vehicles: Vehicle[];
  stops: Stop[];
  routePath?: RouteStep[];
  userLocation?: UserLocation | null;
}

export default function TransitMap({ vehicles = [], stops = [], routePath, userLocation }: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<any>(null);
  const markersRef = useRef<Map<string, any>>(new Map());
  const polylinesRef = useRef<any[]>([]);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    // Only initialize map on client side after component mounts
    if (!isClient || !mapContainer.current || map.current || !L) return;

    // Import Leaflet dynamically
    import('leaflet').then((LeafletModule) => {
      L = LeafletModule.default;

      // Initialize map
      if (!map.current) {
        map.current = L.map(mapContainer.current).setView([36.365, 6.615], 13);

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
          maxZoom: 19,
        }).addTo(map.current);

        // Fix default icon
        // @ts-ignore
        delete L.Icon.Default.prototype._getIconUrl;
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
        });
      }
    });

    return () => {
      // Cleanup if needed, but usually we keep map instance in React 18 strict mode to avoid flash
      // For now, just cleanup markers is enough
    };
  }, [isClient]);

  // Update markers when vehicles or stops change
  useEffect(() => {
    if (!isClient || !map.current || !L) return;

    // Remove old markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current.clear();

    const getIcon = (type?: string): any => {
      const iconHtml = (color: string, letter: string) => `
        <div style="position: relative; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 100%; height: 100%; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
            <circle cx="12" cy="10" r="3"></circle>
          </svg>
          <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -60%); color: white; font-weight: bold; font-size: 10px;">${letter}</div>
        </div>
      `;

      switch (type?.toLowerCase()) {
        case 'tram':
          return L.divIcon({
            html: iconHtml('#ef4444', 'T'), // Red
            className: 'custom-div-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30]
          });
        case 'bus':
          return L.divIcon({
            html: iconHtml('#3b82f6', 'B'), // Blue
            className: 'custom-div-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30]
          });
        case 'taxi':
          return L.divIcon({
            html: iconHtml('#eab308', 'Tx'), // Yellow
            className: 'custom-div-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30]
          });
        default:
          return L.divIcon({
            html: iconHtml('#6b7280', '?'), // Gray
            className: 'custom-div-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30]
          });
      }
    };

    // Add user location
    if (userLocation) {
      const marker = L.marker([userLocation.lat, userLocation.lon], {
        icon: L.icon({
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
        }),
      }).addTo(map.current);
      marker.bindPopup('You are here');
      markersRef.current.set('user', marker);
    }

    // Add stops
    stops.forEach((stop) => {
      const marker = L.marker([stop.lat, stop.lon], { icon: getIcon(stop.type) }).addTo(map.current!);
      marker.bindPopup(
        `<div class="font-bold">${stop.name}</div><div class="text-xs text-gray-500">ID: ${stop.id}</div>`
      );
      markersRef.current.set(stop.id, marker);
    });

    // Add vehicles
    vehicles.forEach((vehicle) => {
      const marker = L.marker([vehicle.lat, vehicle.lon], { icon: getIcon(vehicle.type) }).addTo(map.current!);
      marker.bindPopup(
        `<div class="font-bold">${vehicle.route}</div><div class="text-xs">Status: ${vehicle.status}</div>`
      );
      markersRef.current.set(vehicle.id, marker);
    });
  }, [isClient, vehicles, stops, userLocation]);

  // Update polylines
  useEffect(() => {
    if (!isClient || !map.current || !routePath || !L) return;

    // Remove old polylines
    polylinesRef.current.forEach(polyline => polyline.remove());
    polylinesRef.current = [];

    routePath.forEach((step) => {
      let positions: any[] | undefined;

      if (step.path_coordinates) {
        positions = step.path_coordinates.map(([lat, lng]) => [lat, lng]);
      } else {
        const fromStop = stops.find(s => s.id === step.from_stop);
        const toStop = stops.find(s => s.id === step.to_stop);
        if (fromStop && toStop) {
          positions = [[fromStop.lat, fromStop.lon], [toStop.lat, toStop.lon]];
        }
      }

      if (positions) {
        const color = step.mode === 'tram' ? 'red' : step.mode === 'bus' ? 'blue' : 'gray';
        const polyline = L.polyline(positions, {
          color,
          dashArray: step.mode === 'walk' ? '5, 10' : undefined,
          weight: 5,
        }).addTo(map.current!);
        polylinesRef.current.push(polyline);
      }
    });
  }, [isClient, routePath, stops]);

  return (
    <div ref={mapContainer} style={{ height: '100%', width: '100%' }}>
      {!isClient && <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f3f4f6' }}>Loading Map...</div>}
    </div>
  );
}
