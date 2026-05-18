import React, { useMemo, useState, useEffect } from 'react';
import { RouteResponse, RouteStep } from '@/types';

interface TripDetailsProps {
    routeDetails: RouteResponse;
}

interface AggregatedStep extends RouteStep {
    intermediateStops: string[];
}

const modeColor = (mode: string) => {
    if (mode === 'tram') return 'bg-rose-500';
    if (mode === 'bus') return 'bg-blue-500';
    if (mode === 'taxi') return 'bg-amber-500';
    return 'bg-emerald-500'; // walk
};

const NextBusClock: React.FC = () => {
    const calculateTimeLeft = () => {
        const now = new Date();
        const minutes = now.getMinutes();
        const seconds = now.getSeconds();
        
        const remainderMinutes = minutes % 15;
        let minutesLeft = 14 - remainderMinutes;
        let secondsLeft = 60 - seconds;
        
        if (secondsLeft === 60) {
            secondsLeft = 0;
            minutesLeft += 1;
        }
        
        return minutesLeft * 60 + secondsLeft;
    };

    const [timeLeft, setTimeLeft] = useState(calculateTimeLeft());

    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft(calculateTimeLeft());
        }, 1000);
        return () => clearInterval(timer);
    }, []);

    const m = Math.floor(timeLeft / 60);
    const s = timeLeft % 60;
    
    return (
        <span className="flex items-center gap-1 px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded-md font-bold border border-amber-300">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {m}:{s.toString().padStart(2, '0')}
        </span>
    );
};

const StepCard: React.FC<{ step: AggregatedStep; idx: number; isLast: boolean }> = ({ step, idx, isLast }) => {
    const [expanded, setExpanded] = useState(false);
    const hasIntermediates = step.intermediateStops.length > 0;
    const color = modeColor(step.mode);

    return (
        <div className={`relative pl-8 pb-6 ${isLast ? 'pb-2 border-transparent' : 'border-l-2 border-gray-100'} ml-2`}>
            {/* Timeline dot */}
            <div className={`absolute -left-[11px] top-1 w-5 h-5 rounded-full border-[3px] border-white shadow-sm z-10 ${color}`} />

            <div className="flex flex-col gap-1.5 -mt-1.5">
                {/* Mode badge + duration */}
                <div className="flex items-center gap-2">
                    <span className={`font-bold capitalize text-sm px-2 py-0.5 rounded-md text-white shadow-sm ${color}`}>
                        {step.mode}
                    </span>
                    {(step.route_short || step.route) && (
                        <span className="px-2 py-0.5 bg-gray-100 text-gray-700 text-xs rounded-md font-bold border border-gray-200">
                            {step.route_short || step.route}
                        </span>
                    )}
                    <span className="text-sm font-semibold text-gray-400 ml-auto bg-gray-50 px-2 py-0.5 rounded-md">
                        {Math.round(step.duration / 60)} min
                    </span>
                </div>

                {/* Stops box */}
                <div className="text-sm text-gray-600 mt-1 bg-gray-50/50 rounded-lg border border-gray-100 overflow-hidden">
                    {/* Departure stop */}
                    <div className="font-medium text-gray-900 flex items-center gap-2 px-2.5 pt-2.5 pb-1.5">
                        <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${color}`} />
                        {step.from_name || step.from_stop}
                    </div>

                    {/* Intermediate stops */}
                    {hasIntermediates && (
                        <>
                            <button
                                onClick={() => setExpanded(!expanded)}
                                className="w-full flex items-center gap-2 px-3 py-1.5 text-xs font-semibold text-blue-600 hover:bg-blue-50 transition-colors border-y border-gray-100"
                            >
                                <svg
                                    className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-180' : ''}`}
                                    fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
                                </svg>
                                {expanded ? 'Hide' : 'Show'} {step.intermediateStops.length} intermediate stop{step.intermediateStops.length !== 1 ? 's' : ''}
                            </button>

                            {expanded && (
                                <div className="flex flex-col border-b border-gray-100">
                                    {step.intermediateStops.map((stop, i) => (
                                        <div key={i} className="flex items-center gap-2 px-2.5 py-1.5 hover:bg-gray-100/50 transition-colors">
                                            <div className="w-1.5 h-1.5 rounded-full bg-gray-300 flex-shrink-0 ml-0.5" />
                                            <span className="text-xs text-gray-600">{stop}</span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </>
                    )}

                    {/* Arrival stop */}
                    <div className="font-medium text-gray-900 flex items-center gap-2 px-2.5 pb-2.5 pt-1.5">
                        <div className="w-2.5 h-2.5 rounded-full border-2 border-gray-400 flex-shrink-0" />
                        {step.to_name || step.to_stop}
                    </div>
                </div>
            </div>
        </div>
    );
};

const TripDetails: React.FC<TripDetailsProps> = ({ routeDetails }) => {
    const aggregatedSteps = useMemo(() => {
        const aggr: AggregatedStep[] = [];
        if (!routeDetails.steps || routeDetails.steps.length === 0) return aggr;

        let currentStep: AggregatedStep | null = null;

        routeDetails.steps.forEach((step) => {
            if (!currentStep) {
                currentStep = { ...step, intermediateStops: [] };
            } else if (
                step.mode === currentStep.mode &&
                (step.route_short === currentStep.route_short || step.route === currentStep.route) &&
                step.mode !== 'walk'
            ) {
                // Collect the start of this leg as an intermediate stop
                currentStep.intermediateStops.push(step.from_name || step.from_stop);
                currentStep.to_stop = step.to_stop;
                currentStep.to_name = step.to_name;
                currentStep.duration += step.duration;
            } else {
                aggr.push(currentStep);
                currentStep = { ...step, intermediateStops: [] };
            }
        });
        if (currentStep) aggr.push(currentStep);
        return aggr;
    }, [routeDetails.steps]);

    return (
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-100 flex flex-col mt-2">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-5 text-white rounded-t-2xl">
                <div className="flex justify-between items-center">
                    <h3 className="font-bold text-lg tracking-tight">Trip Details</h3>
                    <div className="flex items-center gap-2 text-xs font-semibold bg-white/20 px-2 py-1 rounded-lg backdrop-blur-sm">
                        <span>Next Bus:</span>
                        <NextBusClock />
                    </div>
                </div>
                <div className="flex gap-2 text-blue-100 text-sm mt-2 font-medium flex-wrap">
                    <span className="bg-white/20 px-2.5 py-1 rounded-lg backdrop-blur-sm whitespace-nowrap">{Math.round(routeDetails.total_duration / 60)} min</span>
                    <span className="bg-white/20 px-2.5 py-1 rounded-lg backdrop-blur-sm whitespace-nowrap">{routeDetails.transfers} transfers</span>
                    {routeDetails.cost !== undefined && routeDetails.cost > 0 && (
                        <span className="bg-green-500/30 text-green-50 px-2.5 py-1 rounded-lg backdrop-blur-sm whitespace-nowrap font-bold ml-auto">{routeDetails.cost} DZD</span>
                    )}
                </div>
            </div>

            {/* Steps */}
            <div className="p-5 space-y-2 relative overflow-y-auto flex-1 scrollbar-hide">
                {aggregatedSteps.map((step, idx) => (
                    <StepCard
                        key={idx}
                        step={step}
                        idx={idx}
                        isLast={idx === aggregatedSteps.length - 1}
                    />
                ))}
            </div>
        </div>
    );
};

export default TripDetails;
