import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { StatCard } from '../components/dashboard/StatCard';
import { EmissionChart } from '../components/charts/EmissionChart';
import { ExplainButton } from '../components/ui/ExplainButton';
import { AchievementCard } from '../components/cards/MilestoneCard';
import { ProgressBar } from '../components/ui/ProgressBar';
import { SkeletonCard, SkeletonChart } from '../components/ui/SkeletonLoader';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { mockCarbonSummary, mockAchievements, mockUserProfile, getDataOrFallback } from '../mocks';
import { CarbonSummary } from '../types';
import {
  Activity, Flame, Target, ArrowRight, Zap, PieChart,
  Lightbulb, TrendingDown,
} from 'lucide-react';
import { ROUTES } from '../constants/routes';

const Dashboard = () => {
  const navigate = useNavigate();
  const { user, footprint, isDemoMode } = useAppStore();
  const [data, setData] = useState<CarbonSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const { data: resolved } = getDataOrFallback(
      footprint,
      mockCarbonSummary
    );
    setData(resolved);
    setLoading(false);
  }, [footprint, isDemoMode]);

  if (!user && !isDemoMode) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4">
        <p className="text-text-muted">Please complete onboarding first.</p>
        <Button onClick={() => navigate(ROUTES.ONBOARDING)}>Get Started</Button>
      </div>
    );
  }

  const displayUser = user ?? mockUserProfile;

  if (loading || !data) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-6 md:grid-cols-3">
          <SkeletonCard /><SkeletonCard /><SkeletonCard />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <SkeletonChart /><SkeletonChart />
        </div>
      </div>
    );
  }

  const progressPct = data.monthly_goal_kg
    ? Math.min(
        100,
        Math.round(
          ((data.monthly_goal_kg - (data.total_emissions_kg_co2e / 12)) /
            data.monthly_goal_kg) *
            100 +
            70
        )
      )
    : 65;

  const changeValue = Math.abs(data.month_over_month_change_pct ?? 4.7);
  const changePositive = (data.month_over_month_change_pct ?? -1) < 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {displayUser.name.split(' ')[0]} 👋
          </h1>
          <p className="text-text-muted mt-1">Here's your carbon footprint overview.</p>
        </div>
        <ExplainButton
          userId={displayUser.id}
          contextType="footprint"
          contextData={data}
          label="Explain My Footprint"
        />
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Total Emissions"
          value={`${Math.round(data.total_emissions_kg_co2e).toLocaleString()} kg`}
          subtitle="CO₂e per year"
          icon={Activity}
          accent="blue"
          trend={{ value: changeValue, isPositive: changePositive }}
        />
        <StatCard
          title="Dominant Source"
          value={data.dominant_source.toUpperCase()}
          subtitle={`${Math.round(data.category_shares_pct[data.dominant_source] ?? 0)}% of total emissions`}
          icon={Flame}
          accent="amber"
        />
        <StatCard
          title="Monthly Goal"
          value={`${Math.round((data.monthly_goal_kg ?? data.total_emissions_kg_co2e * 0.075)).toLocaleString()} kg`}
          subtitle="Based on 10% annual reduction"
          icon={Target}
          accent="emerald"
        />
      </div>

      {/* Goal progress */}
      <Card>
        <CardContent className="p-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm font-semibold text-text-main">Progress Toward Annual Goal</p>
              <p className="text-xs text-text-muted mt-0.5">
                Target: {Math.round(data.total_emissions_kg_co2e * 0.9).toLocaleString()} kg/yr (10% reduction)
              </p>
            </div>
            <span className="text-sm font-bold text-primary">{progressPct}%</span>
          </div>
          <ProgressBar value={progressPct} color="primary" size="lg" />
        </CardContent>
      </Card>

      {/* Charts row */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Emission Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <EmissionChart data={data.category_emissions} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">AI Insight</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-primary/5 rounded-lg p-5 border border-primary/20">
              <p className="text-sm text-text-muted leading-relaxed">
                {data.human_readable_summary}
              </p>
            </div>
            {changePositive && (
              <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400 font-medium">
                <TrendingDown className="w-3.5 h-3.5" aria-hidden="true" />
                Great work — emissions down {changeValue}% from last month!
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Achievements row */}
      <div>
        <h2 className="text-base font-semibold text-text-main mb-3">Recent Achievements</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {mockAchievements.map((a) => (
            <AchievementCard key={a.id} achievement={a} />
          ))}
        </div>
      </div>

      {/* Quick action buttons */}
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          { label: 'View Full Breakdown', icon: PieChart, to: ROUTES.BREAKDOWN },
          { label: 'See My Action Plan', icon: Lightbulb, to: ROUTES.RECOMMENDATIONS },
          { label: 'Ask Climate Coach', icon: Zap, to: ROUTES.ASSISTANT },
        ].map(({ label, icon: Icon, to }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="glass-card p-4 flex items-center justify-between text-sm font-medium text-text-muted hover:text-text-main hover:border-primary/40 transition-all group"
          >
            <div className="flex items-center gap-2">
              <Icon className="w-4 h-4 text-primary" aria-hidden="true" />
              {label}
            </div>
            <ArrowRight className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
          </button>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
