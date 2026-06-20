import { BreakdownCategory } from '../types';

export const mockBreakdownData: BreakdownCategory[] = [
  {
    key: 'transport',
    label: 'Transport',
    emissions_kg: 3850,
    share_pct: 53.2,
    color: '#3b82f6',
    icon: 'Car',
    subcategories: [
      { label: 'Car commute (daily)', value_kg: 2600 },
      { label: 'Flights (2 short-haul)', value_kg: 840 },
      { label: 'Ride-hailing', value_kg: 280 },
      { label: 'Other (bus/auto)', value_kg: 130 },
    ],
    comparison_text:
      'Your transport footprint is 28 % above the Indian average. Daily car commuting is the primary driver.',
  },
  {
    key: 'food',
    label: 'Food & Diet',
    emissions_kg: 1810,
    share_pct: 25.0,
    color: '#10b981',
    icon: 'Utensils',
    subcategories: [
      { label: 'Beef & lamb', value_kg: 620 },
      { label: 'Dairy products', value_kg: 440 },
      { label: 'Poultry & eggs', value_kg: 310 },
      { label: 'Vegetables & grains', value_kg: 280 },
      { label: 'Food waste', value_kg: 160 },
    ],
    comparison_text:
      'Food emissions are close to the Indian average. Reducing beef intake twice a week could save ~180 kg/yr.',
  },
  {
    key: 'electricity',
    label: 'Electricity',
    emissions_kg: 1020,
    share_pct: 14.1,
    color: '#f59e0b',
    icon: 'Zap',
    subcategories: [
      { label: 'Air conditioning', value_kg: 430 },
      { label: 'Appliances & lighting', value_kg: 310 },
      { label: 'Electronics', value_kg: 185 },
      { label: 'Water heating', value_kg: 95 },
    ],
    comparison_text:
      'Electricity use is within the average range. Solar panels could eliminate this category entirely.',
  },
  {
    key: 'waste',
    label: 'Waste',
    emissions_kg: 560,
    share_pct: 7.7,
    color: '#8b5cf6',
    icon: 'Trash2',
    subcategories: [
      { label: 'General waste (landfill)', value_kg: 310 },
      { label: 'Food waste', value_kg: 160 },
      { label: 'Plastic & packaging', value_kg: 90 },
    ],
    comparison_text:
      'Waste emissions are slightly above average. Composting food waste could cut 100+ kg/yr.',
  },
];
