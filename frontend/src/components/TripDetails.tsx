import React, { useMemo } from 'react';
import { RouteResponse, RouteStep } from '@/types';

interface TripDetailsProps {
    routeDetails: RouteResponse;
}

const TripDetails: React.FC<TripDetailsProps> = ({ routeDetails }) => {
    const aggregatedSteps = useMemo(() => {
        const aggr: RouteStep[] = [];
        if (!routeDetails.steps || routeDetails.steps.length === 0) return aggr;

        let currentStep: RouteStep & { count: number } | null = null;

        routeDetails.steps.forEach((step) => {
            if (!currentStep) {
                currentStep = { ...step, count: 1 };
            } else if (
                step.mode === currentStep.mode &&
                step.route === currentStep.route &&
                step.mode !== 'walk'
            ) {
                currentStep.to_stop = step.to_stop;
                currentStep.count += 1;
                currentStep.duration += step.duration;
            } else {
                aggr.push(currentStep);
                currentStep = { ...step, count: 1 };
            }
        });
        if (currentStep) aggr.push(currentStep);
        return aggr;
    }, [routeDetails.steps]);

    return (
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col mt-2">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-5 text-white">
                <h3 className="font-bold text-lg tracking-tight">Trip Details</h3>
                <div className="flex justify-between items-center text-blue-100 text-sm mt-2 font-medium">
                    <span className="bg-white/20 px-2.5 py-1 rounded-lg backdrop-blur-sm">{Math.round(routeDetails.total_duration / 60)} min</span>
                    <span className="bg-white/20 px-2.5 py-1 rounded-lg backdrop-blur-sm">{routeDetails.transfers} transfers</span>
                </div>
            </div>

            <div className="p-5 space-y-6 relative overflow-y-auto max-h-[40vh] scrollbar-hide">
                {aggregatedSteps.map((step, idx) => (
                    <div key={idx} className="relative pl-8 pb-6 last:pb-2 border-l-2 border-gray-100 last:border-transparent ml-2">
                        {/* Node timeline dot */}
                        <div className={`absolute -left-[11px] top-1 w-5 h-5 rounded-full border-[3px] border-white shadow-sm z-10 
                            ${step.mode === 'tram' ? 'bg-rose-500' :
                                step.mode === 'bus' ? 'bg-blue-500' :
                                    step.mode === 'taxi' ? 'bg-amber-500' : 'bg-emerald-500'
                            }`} />

                        <div className="flex flex-col gap-1.5 -mt-1.5">
                            <div className="flex items-center gap-2">
                                <span className={`font-bold capitalize text-sm px-2 py-0.5 rounded-md text-white shadow-sm
                                    ${step.mode === 'tram' ? 'bg-rose-500' :
                                        step.mode === 'bus' ? 'bg-blue-500' :
                                            step.mode === 'taxi' ? 'bg-amber-500' : 'bg-emerald-500'
                                    }`}>
                                    {step.mode}
                                </span>
                                {step.route && (
                                    <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-md font-bold border border-gray-200">
                                        {step.route}
                                    </span>
                                )}
                                <span className="text-sm font-semibold text-gray-400 ml-auto bg-gray-50 px-2 py-0.5 rounded-md">
                                    {Math.round(step.duration / 60)} min
                                </span>
                            </div>

                            <div className="text-sm text-gray-600 mt-1 bg-gray-50/50 p-2.5 rounded-lg border border-gray-100">
                                <div className="font-medium text-gray-900 flex items-center gap-2">
                                    <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
                                    {step.from_stop}
                                </div>
                                {step.count && step.count > 1 && (
                                    <div className="text-xs text-gray-400 my-1.5 pl-[11px] border-l-2 border-dashed border-gray-200 ml-0.5 py-0.5">
                                        {step.count} stops
                                    </div>
                                )}
                                <div className="font-medium text-gray-900 flex items-center gap-2 mt-1">
                                    <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
                                    {step.to_stop}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TripDetails;
