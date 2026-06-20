import React from 'react';
import { cn } from '../../utils/cn';

interface ProgressBarProps {
  value: number;      // 0–100
  max?: number;
  label?: string;
  showLabel?: boolean;
  color?: 'primary' | 'emerald' | 'amber' | 'blue';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const colorMap = {
  primary: 'bg-primary',
  emerald: 'bg-emerald-500',
  amber:   'bg-amber-500',
  blue:    'bg-blue-500',
};

const sizeMap = {
  sm: 'h-1.5',
  md: 'h-2.5',
  lg: 'h-3.5',
};

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  label,
  showLabel = false,
  color = 'primary',
  size = 'md',
  className,
}) => {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  return (
    <div className={cn('w-full', className)}>
      {(label || showLabel) && (
        <div className="flex justify-between items-center mb-1.5">
          {label && <span className="text-xs text-text-muted">{label}</span>}
          {showLabel && (
            <span className="text-xs font-medium text-text-main">
              {Math.round(pct)}%
            </span>
          )}
        </div>
      )}
      <div
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
        className={cn('w-full rounded-full bg-surface border border-border/50 overflow-hidden', sizeMap[size])}
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-700 ease-out',
            colorMap[color]
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
};
