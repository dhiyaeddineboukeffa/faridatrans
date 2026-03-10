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
        <div className="w-full">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 mb-4 flex items-center gap-2">
                <Navigation className="w-4 h-4 text-blue-500" />
                Plan Journey
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-400" />

                    {!useLocation ? (
                        <select
                            value={origin}
                            onChange={(e) => setOrigin(e.target.value)}
                            className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 hover:bg-gray-100 transition-all outline-none appearance-none text-gray-800 font-medium"
                            required={!useLocation}
                        >
                            <option value="">Select Origin</option>
                            {stops.map(stop => (
                                <option key={stop.id} value={stop.id}>{stop.name}</option>
                            ))}
                        </select>
                    ) : (
                        <div className="w-full pl-10 pr-4 py-3 bg-blue-50 border border-blue-200 rounded-xl text-blue-700 flex items-center justify-between font-medium">
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
                        className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 hover:bg-gray-100 transition-all outline-none appearance-none text-gray-800 font-medium"
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
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 mt-2 rounded-xl font-bold shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:from-blue-700 hover:to-indigo-700 active:scale-[0.98] transition-all disabled:opacity-50 disabled:active:scale-100 flex items-center justify-center gap-2"
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
