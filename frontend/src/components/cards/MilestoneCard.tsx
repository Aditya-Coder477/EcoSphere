import React from 'react';
import {
  Flag, Leaf, Flame, Train, TreePine, Sprout, Bus, Sun,
  Trophy, Star, Zap, Award,
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { Milestone, Achievement } from '../../types';

// Dynamic icon resolver
const ICON_MAP: Record<string, React.FC<{ className?: string }>> = {
  Flag, Leaf, Flame, Train, TreePine, Sprout, Bus, Sun,
  Trophy, Star, Zap, Award,
};

const resolveIcon = (name: string) => ICON_MAP[name] ?? Award;

// ─── Milestone Card ───────────────────────────────────────────────
interface MilestoneCardProps {
  milestone: Milestone;
}

export const MilestoneCard: React.FC<MilestoneCardProps> = ({ milestone }) => {
  const Icon = resolveIcon(milestone.icon);
  const date = new Date(milestone.achieved_at).toLocaleDateString('en-IN', {
    month: 'short',
    year: 'numeric',
  });

  return (
    <div className="glass-card p-4 flex items-start gap-4 hover:scale-[1.01] transition-transform">
      <div className={cn('w-10 h-10 rounded-full bg-surface flex items-center justify-center flex-shrink-0', milestone.color)}>
        <Icon className="w-5 h-5" aria-hidden="true" />
      </div>
      <div className="min-w-0">
        <p className="text-sm font-semibold text-text-main truncate">{milestone.title}</p>
        <p className="text-xs text-text-muted leading-relaxed mt-0.5">{milestone.description}</p>
        <p className="text-xs text-text-muted/60 mt-1">{date}</p>
      </div>
    </div>
  );
};

// ─── Achievement Badge Card ────────────────────────────────────────
interface AchievementCardProps {
  achievement: Achievement;
}

export const AchievementCard: React.FC<AchievementCardProps> = ({ achievement }) => {
  const Icon = resolveIcon(achievement.icon);

  return (
    <div
      className={cn(
        'glass-card p-4 flex flex-col items-center text-center gap-2 transition-all',
        achievement.unlocked ? 'opacity-100' : 'opacity-40 grayscale'
      )}
      title={achievement.unlocked ? 'Achieved!' : 'Not yet unlocked'}
    >
      <div
        className={cn(
          'w-12 h-12 rounded-full flex items-center justify-center',
          achievement.unlocked ? 'bg-surface' : 'bg-surface/40',
          achievement.color
        )}
      >
        <Icon className="w-6 h-6" aria-hidden="true" />
      </div>
      <div>
        <p className="text-xs font-semibold text-text-main">{achievement.title}</p>
        <p className="text-[10px] text-text-muted mt-0.5 leading-relaxed">{achievement.description}</p>
      </div>
      {!achievement.unlocked && achievement.progress !== undefined && (
        <div className="w-full">
          <div className="h-1 bg-border rounded-full overflow-hidden">
            <div
              className="h-full bg-primary/50 rounded-full transition-all duration-700"
              style={{ width: `${achievement.progress}%` }}
            />
          </div>
          <p className="text-[10px] text-text-muted/60 mt-1">{achievement.progress}% complete</p>
        </div>
      )}
      {achievement.unlocked && (
        <span className="text-[10px] font-medium text-emerald-400">✓ Achieved</span>
      )}
    </div>
  );
};
