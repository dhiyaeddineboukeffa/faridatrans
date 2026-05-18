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
            className={`transition-all duration-300 ease-in-out relative flex flex-col overflow-hidden
          ${isSidebarOpen
                    ? 'bg-white/95 backdrop-blur-xl shadow-2xl rounded-2xl w-full h-[85vh] md:h-auto md:max-h-[calc(100vh-4rem)] border border-white/20'
                    : 'bg-white shadow-lg rounded-full w-12 h-12 self-end md:self-start items-center justify-center'}
        `}
        >
            <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className={`absolute top-3 right-3 p-1.5 rounded-full hover:bg-gray-100 z-50 text-gray-500 transition-colors ${!isSidebarOpen && 'top-1.5 right-1.5'}`}
            >
                {isSidebarOpen ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                    </svg>
                ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <line x1="3" x2="21" y1="6" y2="6" /><line x1="3" x2="21" y1="12" y2="12" /><line x1="3" x2="21" y1="18" y2="18" />
                    </svg>
                )}
            </button>

            <div className={`flex flex-col gap-5 p-5 overflow-y-auto scrollbar-hide h-full ${!isSidebarOpen && 'hidden'}`}>
                {/* Trajecto Logo Component */}
                <div className="flex flex-col items-center justify-center pb-4 border-b border-gray-100">
                    <img 
                        src="/logo.jpg" 
                        alt="Trajecto Logo" 
                        className="w-full max-w-[200px] object-contain drop-shadow-sm"
                    />
                </div>

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
