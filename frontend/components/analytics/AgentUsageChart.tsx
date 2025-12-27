'use client';

import { memo, useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { AgentUsageStats } from '@/types/analytics';

interface AgentUsageChartProps {
  data: AgentUsageStats[];
  className?: string;
}

// Format agent type to display name (e.g., "visa" -> "Visa")
function formatAgentName(agentType: string): string {
  return agentType
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export const AgentUsageChart = memo(function AgentUsageChart({
  data,
  className,
}: AgentUsageChartProps) {
  const chartData = useMemo(
    () =>
      data.map((item) => {
        // Calculate successful/failed from total and success_rate
        const successful = Math.round((item.invocations * item.success_rate) / 100);
        const failed = item.invocations - successful;
        return {
          name: formatAgentName(item.agent_type),
          successful,
          failed,
          total: item.invocations,
          success_rate: item.success_rate,
          avg_time: item.avg_duration_seconds,
        };
      }),
    [data],
  );

  return (
    <div className={className}>
      <h3 className="mb-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
        AI Agent Usage
      </h3>
      {chartData.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-slate-500">
          No agent usage data available
        </div>
      ) : (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="name"
                tick={{ fill: '#64748b', fontSize: 11 }}
                axisLine={{ stroke: '#e2e8f0' }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: '#e2e8f0' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                }}
                formatter={(value, name, props) => {
                  if (name === 'Successful' && props.payload) {
                    return [
                      `${value} (${props.payload.success_rate?.toFixed(1) ?? 0}% success rate)`,
                      name,
                    ];
                  }
                  return [value, name];
                }}
              />
              <Legend />
              <Bar
                dataKey="successful"
                name="Successful"
                stackId="a"
                fill="#10b981"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="failed"
                name="Failed"
                stackId="a"
                fill="#ef4444"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
});
