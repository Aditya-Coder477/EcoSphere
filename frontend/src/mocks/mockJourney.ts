import { JourneyMonth, Milestone, Achievement } from '../types';

// 12-month story: started at 8 100 kg/yr baseline, improved consistently
// Total saved over the year: 860 kg  (roughly 10% down from baseline)
export const mockJourneyMonths: JourneyMonth[] = [
  { month: 'Jul 2024', emissions_kg: 675, savings_kg: 0   },
  { month: 'Aug 2024', emissions_kg: 668, savings_kg: 7   },
  { month: 'Sep 2024', emissions_kg: 652, savings_kg: 23  },
  { month: 'Oct 2024', emissions_kg: 644, savings_kg: 31  },
  { month: 'Nov 2024', emissions_kg: 631, savings_kg: 44  },
  { month: 'Dec 2024', emissions_kg: 620, savings_kg: 55  },
  { month: 'Jan 2025', emissions_kg: 605, savings_kg: 70  },
  { month: 'Feb 2025', emissions_kg: 598, savings_kg: 77  },
  { month: 'Mar 2025', emissions_kg: 588, savings_kg: 87  },
  { month: 'Apr 2025', emissions_kg: 572, savings_kg: 103 },
  { month: 'May 2025', emissions_kg: 560, savings_kg: 115 },
  { month: 'Jun 2025', emissions_kg: 603, savings_kg: 72  }, // this month (current)
];

export const mockMilestones: Milestone[] = [
  {
    id: 'ms_001',
    title: 'First Step Taken',
    description: 'Completed your carbon footprint assessment.',
    achieved_at: '2024-07-01',
    icon: 'Flag',
    color: 'text-blue-400',
  },
  {
    id: 'ms_002',
    title: '100 kg Saved',
    description: 'Reached your first 100 kg CO₂e reduction milestone.',
    achieved_at: '2024-11-15',
    icon: 'Leaf',
    color: 'text-emerald-400',
  },
  {
    id: 'ms_003',
    title: '3-Month Streak',
    description: 'Reduced emissions consistently for three months in a row.',
    achieved_at: '2024-12-01',
    icon: 'Flame',
    color: 'text-orange-400',
  },
  {
    id: 'ms_004',
    title: 'Transit Switcher',
    description: 'Used public transit for the first time as your primary commute.',
    achieved_at: '2025-01-10',
    icon: 'Train',
    color: 'text-cyan-400',
  },
  {
    id: 'ms_005',
    title: '500 kg Saved',
    description: 'Cumulative savings have crossed the 500 kg mark — equivalent to planting 22 trees.',
    achieved_at: '2025-04-20',
    icon: 'TreePine',
    color: 'text-green-400',
  },
];

export const mockAchievements: Achievement[] = [
  {
    id: 'ach_001',
    title: 'Green Pioneer',
    description: 'Joined EcoSphere and started tracking.',
    icon: 'Sprout',
    color: 'text-emerald-400',
    unlocked: true,
    progress: 100,
  },
  {
    id: 'ach_002',
    title: 'Transit Champion',
    description: 'Use public transit for 30 commute days.',
    icon: 'Bus',
    color: 'text-blue-400',
    unlocked: false,
    progress: 67,
  },
  {
    id: 'ach_003',
    title: 'Plant-Based Explorer',
    description: 'Log 20 plant-based meals.',
    icon: 'Salad',
    color: 'text-green-400',
    unlocked: false,
    progress: 45,
  },
  {
    id: 'ach_004',
    title: 'Carbon Saver 500',
    description: 'Save 500 kg CO₂e cumulatively.',
    icon: 'TreePine',
    color: 'text-teal-400',
    unlocked: true,
    progress: 100,
  },
  {
    id: 'ach_005',
    title: 'Solar Ready',
    description: 'Install a renewable energy source at home.',
    icon: 'Sun',
    color: 'text-yellow-400',
    unlocked: false,
    progress: 0,
  },
];

export const mockCumulativeSavings = 558; // kg saved since Jul 2024
export const mockStreakMonths = 5;        // months of consistent reduction
