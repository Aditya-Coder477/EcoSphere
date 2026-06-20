import { AssistantMessage } from '../types';

// Simulated answers reference the same numbers as the mock footprint:
// total 7 240 kg, transport 3 850 kg (53 %), food 1 810 kg, electricity 1 020 kg

export const getWelcomeMessage = (name: string): AssistantMessage => ({
  id: 'welcome',
  role: 'assistant',
  content:
    `Hi ${name}! I'm your AI Climate Coach. 👋\n\n` +
    'Based on your profile, your annual footprint is **7,240 kg CO₂e** — ' +
    'with transport being your biggest opportunity at 53 % of total emissions.\n\n' +
    'Ask me anything about your footprint, how to reduce specific categories, or general climate science.',
  timestamp: Date.now(),
});

// Context-aware fallback answers keyed by keyword patterns
export const mockFallbackAnswers: Record<string, string> = {
  transport:
    'Your transport footprint is **3,850 kg CO₂e/yr** — the single largest ' +
    'category at 53 % of your total. Daily car commuting contributes about ' +
    '2,600 kg of that. The highest-impact change you can make is switching to ' +
    'public transit 3 days per week, which alone could save **860 kg/yr** at zero cost.',

  food:
    'Your food footprint is **1,810 kg CO₂e/yr** (25 % of total). Beef and lamb ' +
    'account for the biggest share. Replacing beef with chicken or lentils just ' +
    'twice a week can save around **180 kg/yr** — with no dietary sacrifice required.',

  electricity:
    'Your electricity footprint is **1,020 kg CO₂e/yr** (14 % of total). ' +
    'Air conditioning is the largest driver at 430 kg/yr due to India\'s coal-heavy ' +
    'grid. Installing a 2 kW solar panel could eliminate ~40 % of this — saving ' +
    '**420 kg/yr** and paying back within 5 years with current subsidies.',

  waste:
    'Waste contributes **560 kg CO₂e/yr** (7.7 %) to your footprint. Food waste ' +
    'going to landfill generates methane — a greenhouse gas 28× more potent than ' +
    'CO₂. Simple composting can cut this by **100–160 kg/yr** at zero cost.',

  reduce:
    'The three highest-impact actions for your profile are:\n\n' +
    '1. **Public transit 3×/week** → saves 860 kg CO₂e/yr (free)\n' +
    '2. **Reduce one flight per year** → saves 420 kg CO₂e/yr (free)\n' +
    '3. **Install rooftop solar** → saves 420 kg CO₂e/yr (medium cost, subsidised)\n\n' +
    'Together these actions would cut your footprint by **~23 %** from 7,240 to ~5,560 kg/yr.',

  high:
    'Your footprint of **7,240 kg CO₂e/yr** is above the Indian national average ' +
    'of ~5,900 kg but below the global average of ~9,500 kg. The main reasons are:\n\n' +
    '- Daily car commuting (2,600 kg)\n' +
    '- Two domestic flights per year (840 kg)\n' +
    '- Grid-powered electricity with no renewables (1,020 kg)\n\n' +
    'Transport alone is responsible for **53 %** of your total, which is high relative to your peers.',

  cheap:
    'The best **free or low-cost** actions for you are:\n\n' +
    '- Public transit 3 days/week → **860 kg/yr saved** (free + saves ₹26,000/yr in fuel)\n' +
    '- Carpool with a colleague → **410 kg/yr saved** (free)\n' +
    '- Eliminate beef twice a week → **180 kg/yr saved** (actually saves money)\n' +
    '- Compost food waste → **110 kg/yr saved** (free)\n\n' +
    'Total: **~1,560 kg/yr** at zero cost.',

  default:
    'Based on your current footprint of **7,240 kg CO₂e/yr**, here are some key insights:\n\n' +
    '- Transport (53 %) is your biggest opportunity area\n' +
    '- Cutting car usage is the single highest-impact action\n' +
    '- Your food and electricity footprints are near average\n\n' +
    'Feel free to ask me something more specific — like about your transport, food, electricity, or waste footprint!',
};

export const getSimulatedAnswer = (query: string): string => {
  const q = query.toLowerCase();
  if (q.includes('transport') || q.includes('car') || q.includes('commut') || q.includes('driv') || q.includes('flight')) {
    return mockFallbackAnswers.transport;
  }
  if (q.includes('food') || q.includes('diet') || q.includes('eat') || q.includes('beef') || q.includes('meat') || q.includes('veg')) {
    return mockFallbackAnswers.food;
  }
  if (q.includes('electr') || q.includes('solar') || q.includes('power') || q.includes('energy') || q.includes('ac') || q.includes('applian')) {
    return mockFallbackAnswers.electricity;
  }
  if (q.includes('waste') || q.includes('recycl') || q.includes('compost') || q.includes('trash') || q.includes('landfill')) {
    return mockFallbackAnswers.waste;
  }
  if (q.includes('cheap') || q.includes('budget') || q.includes('free') || q.includes('affordable') || q.includes('cost')) {
    return mockFallbackAnswers.cheap;
  }
  if (q.includes('high') || q.includes('why') || q.includes('reason') || q.includes('cause')) {
    return mockFallbackAnswers.high;
  }
  if (q.includes('reduc') || q.includes('lower') || q.includes('cut') || q.includes('improv') || q.includes('first') || q.includes('start')) {
    return mockFallbackAnswers.reduce;
  }
  return mockFallbackAnswers.default;
};
