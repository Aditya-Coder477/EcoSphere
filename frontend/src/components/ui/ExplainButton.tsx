import React, { useState } from 'react';
import { Sparkles, Loader2, X } from 'lucide-react';
import { Button } from './Button';
import { assistantService } from '../../services/assistantService';

interface ExplainButtonProps {
  userId: string;
  contextType: 'footprint' | 'recommendation';
  contextData: any;
  label?: string;
}

export const ExplainButton: React.FC<ExplainButtonProps> = ({ userId, contextType, contextData, label = "Explain" }) => {
  const [loading, setLoading] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);

  const handleExplain = async () => {
    setLoading(true);
    try {
      let res;
      if (contextType === 'footprint') {
        res = await assistantService.explainFootprint(userId, contextData);
      } else {
        res = await assistantService.explainRecommendation(userId, contextData);
      }
      setExplanation(res.data.explanation_text);
    } catch (err) {
      console.error(err);
      setExplanation("Sorry, I couldn't generate an explanation at this time.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button variant="outline" size="sm" onClick={handleExplain} disabled={loading} className="gap-2">
        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-accent" />}
        {label}
      </Button>

      {explanation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm">
          <div className="bg-surface border border-border shadow-glass rounded-xl w-full max-w-lg p-6 relative">
            <button 
              onClick={() => setExplanation(null)}
              className="absolute top-4 right-4 text-text-muted hover:text-text-main"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-accent" />
              </div>
              <h3 className="text-xl font-semibold">AI Insights</h3>
            </div>
            <div className="text-text-muted leading-relaxed whitespace-pre-wrap">
              {explanation}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
