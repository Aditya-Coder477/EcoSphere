import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { JourneyMonth } from '../../types';

interface TrendChartProps {
  data: JourneyMonth[];
  goalLine?: number;
  height?: number;
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-4 py-3 shadow-lg text-sm">
      <p className="font-semibold text-text-main mb-1">{label}</p>
      <p className="text-blue-400">
        Emissions: <span className="font-bold">{payload[0]?.value} kg</span>
      </p>
      {payload[1] && (
        <p className="text-emerald-400">
          Saved: <span className="font-bold">{payload[1]?.value} kg</span>
        </p>
      )}
    </div>
  );
};

export const TrendChart: React.FC<TrendChartProps> = ({
  data,
  goalLine,
  height = 280,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center text-text-muted text-sm"
        style={{ height }}
      >
        No trend data available.
      </div>
    );
  }

  return (
    <div style={{ height }} className="w-full" aria-label="Monthly emissions trend chart">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2940" />
          <XAxis
            dataKey="month"
            tick={{ fontSize: 11, fill: '#64748b' }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#64748b' }}
            tickLine={false}
            axisLine={false}
            unit=" kg"
          />
          <Tooltip content={<CustomTooltip />} />
          {goalLine && (
            <ReferenceLine
              y={goalLine}
              stroke="#10b981"
              strokeDasharray="4 4"
              label={{ value: 'Goal', fill: '#10b981', fontSize: 11 }}
            />
          )}
          <Line
            type="monotone"
            dataKey="emissions_kg"
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={{ r: 4, fill: '#3b82f6', strokeWidth: 0 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="savings_kg"
            stroke="#10b981"
            strokeWidth={2}
            strokeDasharray="5 3"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
