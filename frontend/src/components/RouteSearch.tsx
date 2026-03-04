'use client';

import { useState } from 'react';
import { Search, MapPin, Navigation } from 'lucide-react';

interface RouteSearchProps {
    stops: any[];
    onSearch: (origin: string, destination: string, originCoords?: { lat: number, lon: number }) => void;
    isLoading: boolean;
}

export default function RouteSearch({ stops, onSearch, isLoading }: RouteSearchProps) {
    const [origin, setOrigin] = useState('');
    const [destination, setDestination] = useState('');
    const [useLocation, setUseLocation] = useState(false);
    const [userCoords, setUserCoords] = useState<{ lat: number, lon: number } | null>(null);
    const [locationError, setLocationError] = useState<string | null>(null);

    const handleUseLocation = () => {
        if (!navigator.geolocation) {
            setLocationError("Geolocation is not supported by your browser");
            return;
        }

        setIsLoadingLocation(true);
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setUserCoords({
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                });
                setUseLocation(true);
                setOrigin(''); // Clear text origin
                setIsLoadingLocation(false);
                setLocationError(null);
            },
            (error) => {
                console.error("Error getting location:", error);
                setLocationError("Unable to retrieve your location");
                setIsLoadingLocation(false);
            }
        );
    };

    const [isLoadingLocation, setIsLoadingLocation] = useState(false);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if ((origin || useLocation) && destination) {
            onSearch(origin, destination, useLocation && userCoords ? userCoords : undefined);
        }
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow-lg w-full max-w-md">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Navigation className="w-6 h-6 text-blue-600" />
                Plan Your Journey
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />

                    {!useLocation ? (
                        <select
                            value={origin}
                            onChange={(e) => setOrigin(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none appearance-none bg-white"
                            required={!useLocation}
                        >
                            <option value="">Select Origin</option>
                            {stops.map(stop => (
                                <option key={stop.id} value={stop.id}>{stop.name}</option>
                            ))}
                        </select>
                    ) : (
                        <div className="w-full pl-10 pr-4 py-2 border rounded-lg bg-blue-50 text-blue-700 flex items-center justify-between">
                            <span>Current Location</span>
                            <button
                                type="button"
                                onClick={() => { setUseLocation(false); setUserCoords(null); }}
                                className="text-xs text-blue-500 hover:text-blue-700 underline"
                            >
                                Change
                            </button>
                        </div>
                    )}
                </div>

                {!useLocation && (
                    <button
                        type="button"
                        onClick={handleUseLocation}
                        disabled={isLoadingLocation}
                        className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 pl-1"
                    >
                        {isLoadingLocation ? "Locating..." : "📍 Use my current location"}
                    </button>
                )}

                {locationError && (
                    <p className="text-xs text-red-500 pl-1">{locationError}</p>
                )}

                <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-red-400" />
                    <select
                        value={destination}
                        onChange={(e) => setDestination(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none appearance-none bg-white"
                        required
                    >
                        <option value="">Select Destination</option>
                        {stops.map(stop => (
                            <option key={stop.id} value={stop.id}>{stop.name}</option>
                        ))}
                    </select>
                </div>

                <button
                    type="submit"
                    disabled={isLoading || (useLocation && !userCoords)}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        <span>Calculating...</span>
                    ) : (
                        <>
                            <Search className="w-5 h-5" />
                            Find Route
                        </>
                    )}
                </button>
            </form>
        </div>
    );
}
