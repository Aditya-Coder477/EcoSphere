import React from 'react';
import { FlaskConical, X } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export const DemoModeBanner: React.FC = () => {
  const toggleDemoMode = useAppStore((s) => s.toggleDemoMode);

  return (
    <div
      role="status"
      aria-label="Demo mode active"
      className="flex items-center justify-between gap-3 px-4 py-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-medium mb-4"
    >
      <div className="flex items-center gap-2">
        <FlaskConical className="w-3.5 h-3.5 flex-shrink-0" />
        <span>
          <strong>Sample data</strong> — backend unavailable or demo mode is on. Numbers are simulated.
        </span>
      </div>
      <button
        onClick={toggleDemoMode}
        aria-label="Dismiss demo mode banner"
        className="hover:text-amber-300 transition-colors flex-shrink-0"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
