import React, { useEffect, useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import { BreakdownCategory } from '../types';
import { EmissionChart } from '../components/charts/EmissionChart';
import { BreakdownBarChart } from '../components/charts/BreakdownBarChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { SkeletonChart } from '../components/ui/SkeletonLoader';
import { mockBreakdownData, getDataOrFallback } from '../mocks';
import { Car, Utensils, Zap, Trash2 } from 'lucide-react';
import { cn } from '../utils/cn';

const ICON_MAP: Record<string, React.ComponentType<any>> = {
  Car, Utensils, Zap, Trash2,
};

const CarbonBreakdown = () => {
  const footprint = useAppStore((s) => s.footprint);
  const [breakdown, setBreakdown] = useState<BreakdownCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    // Derive breakdown from store footprint or fall back to mock
    const realData =
      footprint && Object.keys(footprint.category_emissions).length > 0
        ? mockBreakdownData.map((cat) => ({
            ...cat,
            emissions_kg: footprint.category_emissions[cat.key] ?? cat.emissions_kg,
            share_pct: footprint.category_shares_pct[cat.key] ?? cat.share_pct,
          }))
        : null;

    const { data } = getDataOrFallback(realData, mockBreakdownData);
    setBreakdown(data);
    setLoading(false);
    setSelected(data[0]?.key ?? null);
  }, [footprint]);

  const selectedCat = breakdown.find((c) => c.key === selected);
  const donutData = breakdown.reduce<Record<string, number>>(
    (acc, c) => ({ ...acc, [c.label]: c.emissions_kg }),
    {}
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Carbon Breakdown</h1>
        <p className="text-text-muted mt-1">
          A detailed look at where your emissions come from.
        </p>
      </div>

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2">
          <SkeletonChart /><SkeletonChart />
        </div>
      ) : (
        <>
          {/* Category tiles */}
          <div className="grid gap-4 grid-cols-2 md:grid-cols-4" role="group" aria-label="Emission categories">
            {breakdown.map((cat) => {
              const Icon = ICON_MAP[cat.icon] ?? Car;
              const isActive = selected === cat.key;
              return (
                <button
                  key={cat.key}
                  onClick={() => setSelected(cat.key)}
                  aria-pressed={isActive}
                  className={cn(
                    'glass-card p-4 text-left transition-all hover:scale-[1.02]',
                    isActive ? 'ring-2 ring-primary/60' : ''
                  )}
                >
                  <div
                    className="w-9 h-9 rounded-lg flex items-center justify-center mb-3"
                    style={{ backgroundColor: cat.color + '25' }}
                  >
                    <Icon className="w-5 h-5" style={{ color: cat.color }} aria-hidden="true" />
                  </div>
                  <p className="text-sm font-medium text-text-muted">{cat.label}</p>
                  <p className="text-2xl font-bold text-text-main mt-0.5">
                    {cat.emissions_kg.toFixed(0)}
                    <span className="text-xs font-normal text-text-muted ml-1">kg</span>
                  </p>
                  <p className="text-xs text-text-muted mt-1">{cat.share_pct.toFixed(1)}% of total</p>
                </button>
              );
            })}
          </div>

          {/* Charts row */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="text-base">Overall Distribution</CardTitle></CardHeader>
              <CardContent><EmissionChart data={donutData} /></CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">
                  {selectedCat?.label ?? 'Category'} — Sub-categories
                </CardTitle>
              </CardHeader>
              <CardContent>
                {selectedCat ? (
                  <BreakdownBarChart
                    data={selectedCat.subcategories.map((s) => ({
                      label: s.label,
                      value_kg: s.value_kg,
                      color: selectedCat.color,
                    }))}
                    height={240}
                  />
                ) : (
                  <p className="text-text-muted text-sm">Select a category above.</p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Comparison note for selected category */}
          {selectedCat && (
            <Card>
              <CardContent className="p-5">
                <p className="text-sm font-semibold text-text-main mb-1">
                  {selectedCat.label} — Context
                </p>
                <p className="text-sm text-text-muted leading-relaxed">
                  {selectedCat.comparison_text}
                </p>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default CarbonBreakdown;
