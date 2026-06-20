import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface BarItem {
  label: string;
  value_kg: number;
  color?: string;
}

interface BreakdownBarChartProps {
  data: BarItem[];
  height?: number;
}

const DEFAULT_COLOR = '#3b82f6';

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface border border-border rounded-lg px-4 py-3 shadow-lg text-sm">
      <p className="font-semibold text-text-main mb-1">{label}</p>
      <p style={{ color: payload[0]?.fill || DEFAULT_COLOR }}>
        {payload[0]?.value?.toFixed(0)} kg CO₂e
      </p>
    </div>
  );
};

export const BreakdownBarChart: React.FC<BreakdownBarChartProps> = ({
  data,
  height = 220,
}) => {
  if (!data || data.length === 0) {
    return (
      <div
        className="flex items-center justify-center text-text-muted text-sm"
        style={{ height }}
      >
        No data available.
      </div>
    );
  }

  return (
    <div style={{ height }} aria-label="Emissions breakdown bar chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 16, left: 0, bottom: 0 }}
        >
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: '#64748b' }}
            tickLine={false}
            axisLine={false}
            unit=" kg"
          />
          <YAxis
            type="category"
            dataKey="label"
            width={130}
            tick={{ fontSize: 11, fill: '#94a3b8' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
          <Bar dataKey="value_kg" radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || DEFAULT_COLOR}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
