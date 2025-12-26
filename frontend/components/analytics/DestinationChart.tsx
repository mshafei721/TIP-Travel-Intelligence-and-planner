'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { DestinationCount } from '@/types/analytics';

interface DestinationChartProps {
  data: DestinationCount[];
  className?: string;
}

const COLORS = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
  '#f97316',
  '#6366f1',
];

export function DestinationChart({ data, className }: DestinationChartProps) {
  // Format data for display
  const chartData = data.slice(0, 10).map((item) => ({
    name: item.city || item.country,
    country: item.country,
    count: item.count,
    percentage: item.percentage,
  }));

  return (
    <div className={className}>
      <h3 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        Top Destinations
      </h3>
      {chartData.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-slate-500">
          No destination data available
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                type="number"
                tick={{ fill: '#64748b', fontSize: 12 }}
                axisLine={{ stroke: '#e2e8f0' }}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 12 }}
                axisLine={{ stroke: '#e2e8f0' }}
                width={75}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
                formatter={(value, _name, props) => [
                  `${value} trips (${props.payload?.percentage?.toFixed(1) ?? 0}%)`,
                  props.payload?.country ?? '',
                ]}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
