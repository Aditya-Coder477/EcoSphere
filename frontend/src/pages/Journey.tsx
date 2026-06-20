import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { TrendChart } from '../components/charts/TrendChart';
import { MilestoneCard, AchievementCard } from '../components/cards/MilestoneCard';
import { SkeletonChart, SkeletonList } from '../components/ui/SkeletonLoader';
import { StatCard } from '../components/dashboard/StatCard';
import {
  mockJourneyMonths,
  mockMilestones,
  mockAchievements,
  mockCumulativeSavings,
  mockStreakMonths,
  getDataOrFallback,
} from '../mocks';
import { TreePine, Flame, TrendingDown, CalendarCheck } from 'lucide-react';

const Journey = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Journey data is currently always from mock; backend endpoint TBD
    getDataOrFallback(null, mockJourneyMonths);
    setLoading(false);
  }, []);

  const currentMonth = mockJourneyMonths[mockJourneyMonths.length - 1];
  const previousMonth = mockJourneyMonths[mockJourneyMonths.length - 2];
  const monthChange =
    previousMonth
      ? (((previousMonth.emissions_kg - currentMonth.emissions_kg) / previousMonth.emissions_kg) * 100)
      : 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Your Carbon Journey</h1>
        <p className="text-text-muted mt-1">
          Track your progress and celebrate every milestone.
        </p>
      </div>

      {loading ? (
        <><SkeletonChart /><SkeletonList rows={3} /></>
      ) : (
        <>
          {/* Stats row */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard
              title="This Month"
              value={`${currentMonth.emissions_kg} kg`}
              icon={TrendingDown}
              accent="blue"
              trend={{ value: Math.abs(monthChange), isPositive: monthChange > 0 }}
            />
            <StatCard
              title="Total Saved"
              value={`${mockCumulativeSavings} kg`}
              subtitle="vs. your Jul 2024 baseline"
              icon={TreePine}
              accent="emerald"
            />
            <StatCard
              title="Reduction Streak"
              value={`${mockStreakMonths} months`}
              subtitle="consecutive improvements"
              icon={Flame}
              accent="amber"
            />
            <StatCard
              title="Milestones Earned"
              value={mockMilestones.length}
              subtitle="achievements unlocked"
              icon={CalendarCheck}
              accent="purple"
            />
          </div>

          {/* Trend chart */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Monthly Emissions Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <TrendChart
                data={mockJourneyMonths}
                goalLine={544}
                height={300}
              />
              <div className="flex items-center gap-6 mt-4 text-xs text-text-muted">
                <span className="flex items-center gap-1.5">
                  <span className="w-6 h-0.5 bg-blue-400 inline-block rounded" /> Emissions (kg)
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-6 h-0.5 bg-emerald-400 inline-block rounded border-dashed" /> Monthly savings
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="w-6 h-0.5 bg-emerald-500 inline-block rounded" style={{ borderTop: '2px dashed' }} /> 10% goal
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Milestones + Achievements */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle className="text-base">Milestones</CardTitle></CardHeader>
              <CardContent className="space-y-3 pt-0">
                {mockMilestones.map((m) => (
                  <MilestoneCard key={m.id} milestone={m} />
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="text-base">Achievements</CardTitle></CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-3">
                  {mockAchievements.map((a) => (
                    <AchievementCard key={a.id} achievement={a} />
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </div>
  );
};

export default Journey;
