'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import Sidebar from '@/components/Sidebar';
import { Video } from 'lucide-react';
import { Stop, Vehicle, RouteStep, RouteResponse, UserLocation } from '@/types';

const Map = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-200 flex items-center justify-center"><p>Loading Map...</p></div>
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [stops, setStops] = useState<Stop[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [routePath, setRoutePath] = useState<RouteStep[] | undefined>(undefined);
  const [isLoading, setIsLoading] = useState(false);
  const [routeDetails, setRouteDetails] = useState<RouteResponse | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [userLocation, setUserLocation] = useState<UserLocation | null>(null);

  // Fetch stops on mount
  useEffect(() => {
    const fetchStops = async () => {
      try {
        const res = await fetch(`${API_URL}/stops`);
        const data = await res.json();
        setStops(data);
      } catch (error) {
        console.error('Error fetching stops:', error);
      }
    };

    fetchStops();
  }, []);

  // Poll for vehicle positions
  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const res = await fetch(`${API_URL}/vehicles`);
        if (res.ok) {
          const data = await res.json();
          setVehicles(data);
        }
      } catch (error) {
        console.error('Error fetching vehicles:', error);
      }
    };

    fetchVehicles(); // Initial fetch
    const interval = setInterval(fetchVehicles, 2000); // Poll every 2s

    return () => clearInterval(interval);
  }, []);

  // Get user location
  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
        },
        (error) => {
          console.error('Error getting user location:', error);
        }
      );
    } else {
      console.log('Geolocation is not available');
    }
  }, []);

  const handleSearch = async (origin: string, destination: string, originCoords?: UserLocation) => {
    setIsLoading(true);
    if (originCoords) {
      setUserLocation(originCoords);
    }

    try {
      const body: any = { origin, destination };
      if (originCoords) {
        body.origin_lat = originCoords.lat;
        body.origin_lon = originCoords.lon;
      }

      const res = await fetch(`${API_URL}/route`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error('Route not found');

      const data: RouteResponse = await res.json();
      setRoutePath(data.steps);
      setRouteDetails(data);
    } catch (error) {
      alert('Failed to find route. Please try again.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="relative h-screen w-screen overflow-hidden bg-gray-50 font-sans">
      {/* Map Background Layer */}
      <div className="absolute inset-0 z-0">
        <Map
          vehicles={vehicles}
          stops={stops}
          routePath={routePath}
          userLocation={userLocation}
        />
      </div>

      {/* Floating UI Layer */}
      <div className="absolute inset-0 z-10 pointer-events-none p-4 md:p-6 lg:p-8 flex flex-col md:flex-row">
        <div className="pointer-events-auto w-full md:w-96 shrink-0 flex flex-col gap-4">
          <Sidebar
            isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
        stops={stops}
        onSearch={handleSearch}
        isLoading={isLoading}
        routeDetails={routeDetails}
      />
        </div>
      </div>
    </main>
  );
}
