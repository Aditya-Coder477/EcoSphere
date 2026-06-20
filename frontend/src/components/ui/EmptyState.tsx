import React from 'react';
import { LucideIcon, Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title,
  description,
  action,
}) => (
  <div className="flex flex-col items-center justify-center py-16 px-8 text-center glass-card">
    <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mb-4">
      <Icon className="w-7 h-7 text-primary/70" aria-hidden="true" />
    </div>
    <h3 className="text-lg font-semibold text-text-main mb-1">{title}</h3>
    {description && (
      <p className="text-sm text-text-muted max-w-sm leading-relaxed mb-4">{description}</p>
    )}
    {action && <div className="mt-2">{action}</div>}
  </div>
);
