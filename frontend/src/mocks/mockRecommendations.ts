import { RecommendationItem } from '../types';

// Transport is dominant → top recs target transport
// User has medium budget → mix of free and low-cost actions
export const mockRecommendations: RecommendationItem[] = [
  {
    id: 'rec_001',
    title: 'Switch to Public Transit 3 Days/Week',
    category: 'transport',
    description:
      'Taking the metro or bus three days per week instead of driving reduces fuel burn and lowers your per-km emission factor from 192 g CO₂e to under 40 g CO₂e.',
    why_explanation:
      'Your daily car commute alone contributes 2 600 kg/yr — the single largest item in your footprint. Even partial substitution with public transit produces outsized savings with zero upfront cost.',
    carbon_savings_kg: 860,
    impact_score: 9.2,
    effort_level: 'medium',
    cost_level: 'free',
    adoption_probability: 0.72,
    annual_cost_savings_usd: 320,
  },
  {
    id: 'rec_002',
    title: 'Eliminate Beef Twice a Week',
    category: 'food',
    description:
      'Swapping two weekly beef meals for chicken, legumes, or paneer reduces dietary emissions by 15–18 % without requiring a full vegetarian diet.',
    why_explanation:
      'Beef produces 27 kg CO₂e per kg of food — roughly 20× more than lentils. Your current diet includes frequent beef consumption. Two swap days per week is a high-return, low-friction change.',
    carbon_savings_kg: 180,
    impact_score: 7.8,
    effort_level: 'low',
    cost_level: 'free',
    adoption_probability: 0.85,
    annual_cost_savings_usd: 90,
  },
  {
    id: 'rec_003',
    title: 'Install a Solar Rooftop Panel (2 kW)',
    category: 'electricity',
    description:
      'A 2 kW rooftop solar system covers ~40 % of average household electricity needs in India and eliminates the associated grid emissions.',
    why_explanation:
      'India\'s grid has a high carbon intensity (~0.82 kg CO₂/kWh). Solar generation directly offsets grid usage. With current subsidies, payback period is under 5 years.',
    carbon_savings_kg: 420,
    impact_score: 8.5,
    effort_level: 'high',
    cost_level: 'medium',
    adoption_probability: 0.42,
    annual_cost_savings_usd: 210,
  },
  {
    id: 'rec_004',
    title: 'Carpool with a Colleague',
    category: 'transport',
    description:
      'Sharing your daily commute with one colleague halves per-person emissions on that trip, saving approximately 400 kg CO₂e per year.',
    why_explanation:
      'Carpooling is the fastest way to cut transport emissions if switching to transit is not feasible. Splitting fuel costs also saves money directly.',
    carbon_savings_kg: 410,
    impact_score: 7.5,
    effort_level: 'low',
    cost_level: 'free',
    adoption_probability: 0.68,
    annual_cost_savings_usd: 160,
  },
  {
    id: 'rec_005',
    title: 'Start Composting Food Waste',
    category: 'waste',
    description:
      'Composting kitchen scraps diverts organic material from landfill, preventing methane release and creating nutrient-rich compost for plants.',
    why_explanation:
      'Organic waste in landfills generates methane — a greenhouse gas 28× more potent than CO₂. Your household food waste accounts for 160 kg CO₂e/yr.',
    carbon_savings_kg: 110,
    impact_score: 5.9,
    effort_level: 'low',
    cost_level: 'free',
    adoption_probability: 0.78,
    annual_cost_savings_usd: 0,
  },
  {
    id: 'rec_006',
    title: 'Switch to LED Lighting Throughout',
    category: 'electricity',
    description:
      'Replacing all remaining incandescent and CFL bulbs with LEDs reduces lighting electricity use by up to 75 %.',
    why_explanation:
      'Lighting contributes ~85 kg CO₂e/yr for your household. LEDs last 15–25× longer and consume a fraction of the energy. Payback is typically under 6 months.',
    carbon_savings_kg: 65,
    impact_score: 5.2,
    effort_level: 'low',
    cost_level: 'low',
    adoption_probability: 0.91,
    annual_cost_savings_usd: 35,
  },
  {
    id: 'rec_007',
    title: 'Reduce One Short-Haul Flight Per Year',
    category: 'transport',
    description:
      'Choosing train travel or video calls instead of one domestic flight saves 350–500 kg CO₂e per round trip.',
    why_explanation:
      'Aviation has one of the highest per-km emission factors. Your two short-haul flights account for 840 kg/yr. Eliminating or offsetting one significantly reduces your transport total.',
    carbon_savings_kg: 420,
    impact_score: 8.1,
    effort_level: 'medium',
    cost_level: 'free',
    adoption_probability: 0.55,
    annual_cost_savings_usd: 140,
  },
  {
    id: 'rec_008',
    title: 'Upgrade to Energy-Efficient AC',
    category: 'electricity',
    description:
      'Replacing an old 3-star AC with a 5-star BEE-rated model reduces electricity consumption by 25–30 % for cooling, which is your largest electrical load.',
    why_explanation:
      'Air conditioning accounts for 430 kg CO₂e/yr in your home. A 5-star model can cut this by ~120 kg/yr. Combined with keeping the thermostat at 24°C, savings compound.',
    carbon_savings_kg: 120,
    impact_score: 6.3,
    effort_level: 'medium',
    cost_level: 'medium',
    adoption_probability: 0.48,
    annual_cost_savings_usd: 70,
  },
];
