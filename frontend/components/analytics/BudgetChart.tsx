'use client';

import { memo, useMemo, useCallback } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import type { BudgetRange } from '@/types/analytics';

interface BudgetChartProps {
  data: BudgetRange[];
  averageBudget: number | null;
  currency?: string;
  className?: string;
}

const COLORS = [
  '#10b981', // green - low budget
  '#3b82f6', // blue
  '#f59e0b', // amber
  '#ef4444', // red
  '#8b5cf6', // purple - high budget
];

export const BudgetChart = memo(function BudgetChart({
  data,
  averageBudget,
  currency = 'USD',
  className,
}: BudgetChartProps) {
  const chartData = useMemo(
    () =>
      data.map((item) => ({
        name: item.range_label,
        value: item.count,
        percentage: item.percentage,
      })),
    [data],
  );

  const formatCurrency = useCallback(
    (value: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency,
        maximumFractionDigits: 0,
      }).format(value);
    },
    [currency],
  );

  return (
    <div className={className}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
          Budget Distribution
        </h3>
        {averageBudget !== null && (
          <div className="text-right">
            <p className="text-sm text-slate-500 dark:text-slate-400">Average Budget</p>
            <p className="text-xl font-bold text-slate-900 dark:text-slate-100">
              {formatCurrency(averageBudget)}
            </p>
          </div>
        )}
      </div>
      {chartData.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-slate-500">
          No budget data available
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={2}
                dataKey="value"
                label={({ name, percent }) => `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`}
                labelLine={{ stroke: '#64748b', strokeWidth: 1 }}
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
                formatter={(value, name, props) => [
                  `${value} trips (${props.payload?.percentage?.toFixed(1) ?? 0}%)`,
                  name,
                ]}
              />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => (
                  <span className="text-sm text-slate-600 dark:text-slate-400">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
});
