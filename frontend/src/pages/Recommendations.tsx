import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { carbonService } from '../services/carbonService';
import { RecommendationItem } from '../types';
import { RecommendationCard } from '../components/cards/RecommendationCard';
import { FilterChips, FilterChip } from '../components/ui/FilterChips';
import { SkeletonList } from '../components/ui/SkeletonLoader';
import { EmptyState } from '../components/ui/EmptyState';
import { mockRecommendations, getDataOrFallback } from '../mocks';
import { Lightbulb } from 'lucide-react';

const CATEGORY_CHIPS: FilterChip[] = [
  { key: 'all',         label: 'All' },
  { key: 'transport',   label: '🚗 Transport' },
  { key: 'food',        label: '🥗 Food' },
  { key: 'electricity', label: '⚡ Electricity' },
  { key: 'waste',       label: '♻️ Waste' },
];

const COST_CHIPS: FilterChip[] = [
  { key: 'all',    label: 'Any Cost' },
  { key: 'free',   label: '✅ Free' },
  { key: 'low',    label: '💛 Low Cost' },
  { key: 'medium', label: '🟠 Medium Cost' },
];

const Recommendations = () => {
  const user = useAppStore((s) => s.user);
  const isDemoMode = useAppStore((s) => s.isDemoMode);
  const [recs, setRecs] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [costFilter, setCostFilter] = useState('all');

  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      try {
        if (user && !isDemoMode) {
          const res = await carbonService.getRecommendations(user.id);
          const apiRecs = res?.data?.recommendations;
          const { data } = getDataOrFallback(
            apiRecs && apiRecs.length > 0 ? apiRecs : null,
            mockRecommendations
          );
          setRecs(data);
        } else {
          setRecs(mockRecommendations);
        }
      } catch {
        setRecs(mockRecommendations);
      } finally {
        setLoading(false);
      }
    };
    fetchRecs();
  }, [user, isDemoMode]);

  const filtered = recs.filter((r) => {
    const catOk = categoryFilter === 'all' || r.category === categoryFilter;
    const costOk = costFilter === 'all' || r.cost_level === costFilter;
    return catOk && costOk;
  });

  // Enrich chips with counts from current cost filter
  const categoryChips = CATEGORY_CHIPS.map((c) => ({
    ...c,
    count:
      c.key === 'all'
        ? recs.length
        : recs.filter(
            (r) => r.category === c.key && (costFilter === 'all' || r.cost_level === costFilter)
          ).length,
  }));

  const costChips = COST_CHIPS.map((c) => ({
    ...c,
    count:
      c.key === 'all'
        ? recs.length
        : recs.filter(
            (r) => r.cost_level === c.key && (categoryFilter === 'all' || r.category === categoryFilter)
          ).length,
  }));

  const topThree = filtered.slice(0, 3);
  const rest = filtered.slice(3);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Your Action Plan</h1>
        <p className="text-text-muted mt-1">
          Personalized recommendations ranked by impact. Small changes, big results.
        </p>
      </div>

      {loading ? (
        <SkeletonList rows={4} />
      ) : (
        <>
          {/* Filters */}
          <div className="space-y-3">
            <FilterChips chips={categoryChips} active={categoryFilter} onChange={setCategoryFilter} />
            <FilterChips chips={costChips} active={costFilter} onChange={setCostFilter} />
          </div>

          {filtered.length === 0 ? (
            <EmptyState
              icon={Lightbulb}
              title="No actions match these filters"
              description="Try clearing a filter to see more recommendations."
            />
          ) : (
            <>
              {/* Top 3 highlight */}
              {topThree.length > 0 && (
                <div>
                  <h2 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
                    🏆 Top Actions
                  </h2>
                  <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
                    {topThree.map((rec, i) => (
                      <RecommendationCard
                        key={rec.id}
                        item={rec}
                        userId={user?.id ?? 'demo'}
                        rank={i + 1}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Rest of list */}
              {rest.length > 0 && (
                <div>
                  <h2 className="text-sm font-semibold text-text-muted uppercase tracking-wider mb-3">
                    More Actions
                  </h2>
                  <div className="grid gap-5 md:grid-cols-2">
                    {rest.map((rec, i) => (
                      <RecommendationCard
                        key={rec.id}
                        item={rec}
                        userId={user?.id ?? 'demo'}
                        rank={topThree.length + i + 1}
                      />
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Recommendations;
