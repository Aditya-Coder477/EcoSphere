import React from 'react';
import { cn } from '../../utils/cn';

export interface FilterChip {
  key: string;
  label: string;
  count?: number;
}

interface FilterChipsProps {
  chips: FilterChip[];
  active: string;
  onChange: (key: string) => void;
  className?: string;
}

export const FilterChips: React.FC<FilterChipsProps> = ({
  chips,
  active,
  onChange,
  className,
}) => (
  <div
    role="group"
    aria-label="Filter options"
    className={cn('flex gap-2 flex-wrap', className)}
  >
    {chips.map((chip) => (
      <button
        key={chip.key}
        onClick={() => onChange(chip.key)}
        aria-pressed={active === chip.key}
        className={cn(
          'px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border',
          active === chip.key
            ? 'bg-primary text-white border-primary shadow-sm shadow-primary/30'
            : 'bg-surface/50 text-text-muted border-border hover:border-primary/50 hover:text-text-main'
        )}
      >
        {chip.label}
        {chip.count !== undefined && (
          <span
            className={cn(
              'ml-1.5 text-xs',
              active === chip.key ? 'opacity-80' : 'opacity-50'
            )}
          >
            ({chip.count})
          </span>
        )}
      </button>
    ))}
  </div>
);
