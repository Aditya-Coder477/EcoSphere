import { CarbonSummary } from '../types';

// Aditya drives a car ~15 000 km/yr, eats average meat, uses grid electricity
// Transport dominates at 53 %
export const mockCarbonSummary: CarbonSummary = {
  user_id: 'mock_user_aditya',
  total_emissions_kg_co2e: 7240,
  category_emissions: {
    transport:   3850,
    food:        1810,
    electricity: 1020,
    waste:        560,
  },
  category_shares_pct: {
    transport:   53.2,
    food:        25.0,
    electricity: 14.1,
    waste:         7.7,
  },
  dominant_source: 'transport',
  human_readable_summary:
    'Your biggest impact area is transport at 53 % of your footprint. ' +
    'Switching to public transit for your commute just 3 days per week could save ' +
    'over 800 kg CO₂e annually. Your food and electricity footprints are near ' +
    'the national average for a 2-person household in India.',
  month_over_month_change_pct: -4.7,   // improving
  monthly_goal_kg: 544,                // 7 240 × 0.9 / 12
};
