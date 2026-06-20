import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { LucideIcon, TrendingDown, TrendingUp } from 'lucide-react';
import { cn } from '../../utils/cn';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean; // true = reducing emissions (good)
    label?: string;
  };
  accent?: 'primary' | 'emerald' | 'amber' | 'blue' | 'purple';
  className?: string;
}

const accentMap = {
  primary: { bg: 'bg-primary/10', text: 'text-primary', icon: 'text-primary' },
  emerald: { bg: 'bg-emerald-500/10', text: 'text-emerald-400', icon: 'text-emerald-400' },
  amber:   { bg: 'bg-amber-500/10',   text: 'text-amber-400',   icon: 'text-amber-400'   },
  blue:    { bg: 'bg-blue-500/10',    text: 'text-blue-400',    icon: 'text-blue-400'    },
  purple:  { bg: 'bg-purple-500/10',  text: 'text-purple-400',  icon: 'text-purple-400'  },
};

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accent = 'primary',
  className,
}) => {
  const colors = accentMap[accent];

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-text-muted">{title}</CardTitle>
        <div className={cn('w-8 h-8 rounded-lg flex items-center justify-center', colors.bg)}>
          <Icon className={cn('h-4 w-4', colors.icon)} aria-hidden="true" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-text-main">{value}</div>
        {subtitle && <p className="text-xs text-text-muted mt-1 leading-relaxed">{subtitle}</p>}
        {trend && (
          <p
            className={cn(
              'text-xs mt-2 font-medium flex items-center gap-1',
              trend.isPositive ? 'text-emerald-500' : 'text-red-400'
            )}
          >
            {trend.isPositive
              ? <TrendingDown className="w-3 h-3" aria-hidden="true" />
              : <TrendingUp className="w-3 h-3" aria-hidden="true" />
            }
            {trend.isPositive ? '↓' : '↑'} {Math.abs(trend.value)}%{' '}
            {trend.label ?? 'from last month'}
          </p>
        )}
      </CardContent>
    </Card>
  );
};
