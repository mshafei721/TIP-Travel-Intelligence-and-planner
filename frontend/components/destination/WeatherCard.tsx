'use client';

import { Cloud, CloudRain, CloudSnow, Sun, Wind, CloudFog, CloudDrizzle, Zap } from 'lucide-react';
import IntelligenceCard from './IntelligenceCard';
import type { WeatherForecast, WeatherCondition } from '@/types/destination';

interface WeatherCardProps {
  data: WeatherForecast;
  isExpanded?: boolean;
  isLoading?: boolean;
  onExpand?: (cardId: string) => void;
  onCollapse?: (cardId: string) => void;
}

// Animated weather icon component
function AnimatedWeatherIcon({ condition }: { condition: WeatherCondition }) {
  const iconClass = 'w-8 h-8';

  switch (condition) {
    case 'sunny':
      return (
        <div className="relative">
          <Sun className={`${iconClass} text-yellow-500 animate-spin-slow`} />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-12 h-12 bg-yellow-400/20 rounded-full animate-ping" />
          </div>
        </div>
      );
    case 'partly-cloudy':
      return (
        <div className="relative">
          <Sun className={`${iconClass} text-yellow-500 absolute top-0 right-0 animate-pulse`} />
          <Cloud className={`${iconClass} text-slate-400 animate-float`} />
        </div>
      );
    case 'cloudy':
      return <Cloud className={`${iconClass} text-slate-400 animate-float`} />;
    case 'rainy':
      return <CloudRain className={`${iconClass} text-blue-500 animate-bounce-gentle`} />;
    case 'stormy':
      return (
        <div className="relative">
          <CloudRain className={`${iconClass} text-slate-600`} />
          <Zap className="w-4 h-4 text-yellow-500 absolute bottom-0 right-0 animate-pulse" />
        </div>
      );
    case 'snowy':
      return <CloudSnow className={`${iconClass} text-blue-300 animate-float`} />;
    case 'windy':
      return <Wind className={`${iconClass} text-slate-500 animate-sway`} />;
    case 'foggy':
      return <CloudFog className={`${iconClass} text-slate-300 animate-float`} />;
    default:
      return <Cloud className={`${iconClass} text-slate-400`} />;
  }
}

export default function WeatherCard({
  data,
  isExpanded,
  isLoading,
  onExpand,
  onCollapse,
}: WeatherCardProps) {
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
  };

  const getConditionColor = (condition: WeatherCondition): string => {
    const colors = {
      sunny: 'from-yellow-400 to-orange-400',
      'partly-cloudy': 'from-blue-400 to-slate-300',
      cloudy: 'from-slate-300 to-slate-400',
      rainy: 'from-blue-400 to-blue-600',
      stormy: 'from-slate-600 to-blue-700',
      snowy: 'from-blue-200 to-blue-400',
      windy: 'from-slate-400 to-slate-500',
      foggy: 'from-slate-200 to-slate-300',
    };
    return colors[condition] || 'from-slate-300 to-slate-400';
  };

  const avgTemp =
    data.dailyForecasts.length > 0
      ? Math.round(
          data.dailyForecasts.reduce((sum, day) => sum + (day.tempHigh + day.tempLow) / 2, 0) /
            data.dailyForecasts.length,
        )
      : 0;

  return (
    <IntelligenceCard
      id="weather"
      title="Weather Forecast"
      icon={<Cloud className="w-6 h-6" />}
      iconColor="text-blue-500 dark:text-blue-400"
      isExpanded={isExpanded}
      isLoading={isLoading}
      onExpand={onExpand}
      onCollapse={onCollapse}
      badge={
        <span className="text-xs text-slate-500 dark:text-slate-400">
          {data.dailyForecasts.length} days • Avg {avgTemp}°C
        </span>
      }
    >
      <div className="space-y-6">
        {/* Daily forecasts */}
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide">
            Daily Forecast
          </h4>
          <div className="grid gap-3">
            {data.dailyForecasts.map((day, idx) => (
              <div
                key={idx}
                className="relative overflow-hidden flex items-center gap-4 p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg hover:shadow-md transition-shadow"
              >
                {/* Background gradient based on condition */}
                <div
                  className={`absolute inset-0 opacity-5 bg-gradient-to-r ${getConditionColor(day.condition)}`}
                />

                {/* Date */}
                <div className="flex-shrink-0 w-24">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-50">
                    {formatDate(day.date)}
                  </p>
                </div>

                {/* Weather icon */}
                <div className="flex-shrink-0">
                  <AnimatedWeatherIcon condition={day.condition} />
                </div>

                {/* Condition */}
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300 capitalize">
                    {day.condition.replace('-', ' ')}
                  </p>
                  {day.humidity && (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Humidity: {day.humidity}%
                    </p>
                  )}
                </div>

                {/* Temperature */}
                <div className="flex-shrink-0 text-right">
                  <p className="text-lg font-bold text-slate-900 dark:text-slate-50">
                    {day.tempHigh}°
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{day.tempLow}°</p>
                </div>

                {/* Precipitation */}
                <div className="flex-shrink-0 w-16 text-right">
                  <CloudDrizzle className="w-4 h-4 text-blue-500 inline-block mb-1" />
                  <p className="text-xs font-medium text-blue-600 dark:text-blue-400">
                    {day.precipitationChance}%
                  </p>
                </div>

                {/* Additional info */}
                {day.windSpeed && (
                  <div className="flex-shrink-0 w-16 text-right">
                    <Wind className="w-4 h-4 text-slate-500 inline-block mb-1" />
                    <p className="text-xs font-medium text-slate-600 dark:text-slate-400">
                      {day.windSpeed} km/h
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Best time to visit */}
        <div className="p-4 bg-gradient-to-br from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30 border border-amber-200 dark:border-amber-800 rounded-lg">
          <div className="flex items-start gap-3">
            <Sun className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wide mb-1">
                Best Time to Visit
              </p>
              <p className="text-sm text-amber-900 dark:text-amber-200">{data.bestTimeToVisit}</p>
            </div>
          </div>
        </div>

        {/* Climate type */}
        {data.climateType && (
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Climate Type
            </span>
            <span className="text-sm font-semibold text-slate-900 dark:text-slate-50">
              {data.climateType}
            </span>
          </div>
        )}

        {/* Packing recommendations */}
        {data.packingRecommendations.length > 0 && (
          <div className="p-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-3">
              Packing Recommendations
            </p>
            <ul className="space-y-2">
              {data.packingRecommendations.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 bg-blue-500 rounded-full mt-2" />
                  <span className="text-sm text-blue-900 dark:text-blue-200">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Custom animations */}
      <style jsx>{`
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        @keyframes float {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-5px);
          }
        }
        @keyframes bounce-gentle {
          0%,
          100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-3px);
          }
        }
        @keyframes sway {
          0%,
          100% {
            transform: translateX(0px);
          }
          50% {
            transform: translateX(5px);
          }
        }
        :global(.animate-spin-slow) {
          animation: spin-slow 8s linear infinite;
        }
        :global(.animate-float) {
          animation: float 3s ease-in-out infinite;
        }
        :global(.animate-bounce-gentle) {
          animation: bounce-gentle 2s ease-in-out infinite;
        }
        :global(.animate-sway) {
          animation: sway 2s ease-in-out infinite;
        }
      `}</style>
    </IntelligenceCard>
  );
}
