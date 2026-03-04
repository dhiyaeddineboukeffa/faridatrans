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
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="bg-blue-600 p-4 text-white">
                <h3 className="font-bold text-lg">Trip Details</h3>
                <div className="flex justify-between text-blue-100 text-sm mt-1">
                    <span>{Math.round(routeDetails.total_duration / 60)} min total</span>
                    <span>{routeDetails.transfers} transfers</span>
                </div>
            </div>

            <div className="p-4 space-y-4">
                {aggregatedSteps.map((step, idx) => (
                    <div key={idx} className="relative pl-6 pb-4 last:pb-0 border-l-2 border-gray-200 last:border-transparent">
                        <div className={`absolute -left-[9px] top-0 w-4 h-4 rounded-full border-2 border-white shadow-sm ${step.mode === 'tram' ? 'bg-red-500' :
                            step.mode === 'bus' ? 'bg-blue-500' :
                                step.mode === 'taxi' ? 'bg-yellow-500' : 'bg-gray-400'
                            }`} />

                        <div className="flex flex-col gap-1">
                            <div className="flex items-center gap-2">
                                <span className="font-bold text-gray-800 capitalize">{step.mode}</span>
                                {step.route && (
                                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full font-medium">
                                        {step.route}
                                    </span>
                                )}
                                <span className="text-xs text-gray-400 ml-auto">
                                    {Math.round(step.duration / 60)} min
                                </span>
                            </div>

                            <div className="text-sm text-gray-600">
                                <div className="font-medium">{step.from_stop}</div>
                                {step.count && step.count > 1 && (
                                    <div className="text-xs text-gray-400 my-1 pl-2 border-l-2 border-gray-100">
                                        {step.count} stops
                                    </div>
                                )}
                                <div className="font-medium">{step.to_stop}</div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default TripDetails;
