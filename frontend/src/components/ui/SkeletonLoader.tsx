import React from 'react';
import { cn } from '../../utils/cn';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className }) => (
  <div
    aria-hidden="true"
    className={cn(
      'animate-pulse rounded-md bg-surface/60 border border-border/30',
      className
    )}
  />
);

export const SkeletonCard: React.FC = () => (
  <div className="glass-card p-6 space-y-4">
    <Skeleton className="h-4 w-1/3" />
    <Skeleton className="h-8 w-1/2" />
    <Skeleton className="h-3 w-2/3" />
  </div>
);

export const SkeletonChart: React.FC = () => (
  <div className="glass-card p-6 space-y-3">
    <Skeleton className="h-4 w-1/4" />
    <Skeleton className="h-[260px] w-full rounded-lg" />
  </div>
);

export const SkeletonList: React.FC<{ rows?: number }> = ({ rows = 3 }) => (
  <div className="space-y-3">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="glass-card p-4 flex gap-4 items-center">
        <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-2/3" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    ))}
  </div>
);
