import React, { useState } from 'react';
import { RecommendationItem } from '../../types';
import { Card, CardContent } from '../ui/Card';
import { Leaf, DollarSign, Activity, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { ExplainButton } from '../ui/ExplainButton';
import { cn } from '../../utils/cn';

// Impact badge colour mapping
const impactColors = {
  high:   'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  medium: 'bg-amber-500/15   text-amber-400   border-amber-500/30',
  low:    'bg-slate-500/15   text-slate-400   border-slate-500/30',
};

const getImpactLevel = (score: number): 'high' | 'medium' | 'low' => {
  if (score >= 8) return 'high';
  if (score >= 6) return 'medium';
  return 'low';
};

const effortColors: Record<string, string> = {
  low:    'text-emerald-400',
  medium: 'text-amber-400',
  high:   'text-red-400',
};

const costColors: Record<string, string> = {
  free:   'text-emerald-400',
  low:    'text-blue-400',
  medium: 'text-amber-400',
  high:   'text-red-400',
};

export const RecommendationCard: React.FC<{
  item: RecommendationItem;
  userId: string;
  rank?: number;
}> = ({ item, userId, rank }) => {
  const [expanded, setExpanded] = useState(false);
  const impactLevel = getImpactLevel(item.impact_score);

  return (
    <Card className="hover:scale-[1.005] transition-transform">
      <CardContent className="p-6">
        {/* Header row */}
        <div className="flex justify-between items-start mb-4 gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              {rank && (
                <span className="text-xs font-bold text-text-muted/60 tabular-nums">
                  #{rank}
                </span>
              )}
              <span className="text-xs font-semibold px-2 py-0.5 bg-surface rounded-md text-primary uppercase tracking-wider">
                {item.category}
              </span>
              <span
                className={cn(
                  'text-xs font-semibold px-2 py-0.5 rounded-full border capitalize',
                  impactColors[impactLevel]
                )}
              >
                {impactLevel} impact
              </span>
            </div>
            <h3 className="text-base font-bold text-text-main leading-snug">{item.title}</h3>
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-2xl font-black text-primary">
              -{item.carbon_savings_kg.toFixed(0)}
            </div>
            <div className="text-xs text-text-muted">kg CO₂e/yr</div>
          </div>
        </div>

        {/* Description */}
        <p className="text-text-muted text-sm mb-4 leading-relaxed">{item.description}</p>

        {/* Why explanation (expandable) */}
        {item.why_explanation && (
          <div className="mb-4">
            <button
              onClick={() => setExpanded((p) => !p)}
              aria-expanded={expanded}
              className="flex items-center gap-1.5 text-xs text-accent hover:text-accent/80 transition-colors font-medium"
            >
              <HelpCircle className="w-3.5 h-3.5" aria-hidden="true" />
              Why this recommendation?
              {expanded
                ? <ChevronUp className="w-3 h-3" aria-hidden="true" />
                : <ChevronDown className="w-3 h-3" aria-hidden="true" />
              }
            </button>
            {expanded && (
              <div className="mt-2 p-3 rounded-lg bg-accent/5 border border-accent/20 text-xs text-text-muted leading-relaxed">
                {item.why_explanation}
              </div>
            )}
          </div>
        )}

        {/* Footer row */}
        <div className="flex items-center justify-between border-t border-border pt-4 gap-2 flex-wrap">
          <div className="flex gap-4 flex-wrap">
            <div
              className={cn('flex items-center gap-1.5 text-xs', effortColors[item.effort_level])}
              title={`Effort: ${item.effort_level}`}
            >
              <Activity className="w-3.5 h-3.5" aria-hidden="true" />
              <span className="capitalize">{item.effort_level} effort</span>
            </div>
            <div
              className={cn('flex items-center gap-1.5 text-xs', costColors[item.cost_level])}
              title={`Cost: ${item.cost_level}`}
            >
              <DollarSign className="w-3.5 h-3.5" aria-hidden="true" />
              <span className="capitalize">{item.cost_level} cost</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-text-muted" title="Match probability">
              <Leaf className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{(item.adoption_probability * 100).toFixed(0)}% match</span>
            </div>
          </div>
          <ExplainButton userId={userId} contextType="recommendation" contextData={item} />
        </div>
      </CardContent>
    </Card>
  );
};
