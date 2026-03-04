import React from 'react';
import RouteSearch from './RouteSearch';
import TripDetails from './TripDetails';
import { Stop, RouteResponse, UserLocation } from '@/types';

interface SidebarProps {
    isSidebarOpen: boolean;
    setIsSidebarOpen: (isOpen: boolean) => void;
    stops: Stop[];
    onSearch: (origin: string, destination: string, originCoords?: UserLocation) => void;
    isLoading: boolean;
    routeDetails: RouteResponse | null;
}

const Sidebar: React.FC<SidebarProps> = ({
    isSidebarOpen,
    setIsSidebarOpen,
    stops,
    onSearch,
    isLoading,
    routeDetails
}) => {
    return (
        <div
            className={`bg-white z-20 shadow-xl flex flex-col transition-all duration-300 ease-in-out relative
          ${isSidebarOpen ? 'w-full h-1/3 md:w-1/3 lg:w-1/4 md:h-full p-4' : 'w-full h-12 md:w-12 md:h-full p-2 items-center'}
        `}
        >
            <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="absolute top-2 right-2 p-2 rounded-full hover:bg-gray-100 z-50"
            >
                {isSidebarOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                    </svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <rect width="18" height="18" x="3" y="3" rx="2" ry="2" /><path d="M9 3v18" />
                    </svg>
                )}
            </button>

            <div className={`flex flex-col gap-4 overflow-y-auto h-full ${!isSidebarOpen && 'hidden'}`}>
                <h1 className="text-2xl font-bold text-blue-800">Transit Navigator</h1>

                <RouteSearch
                    stops={stops}
                    onSearch={onSearch}
                    isLoading={isLoading}
                />

                {routeDetails && <TripDetails routeDetails={routeDetails} />}
            </div>
        </div>
    );
};

export default Sidebar;
