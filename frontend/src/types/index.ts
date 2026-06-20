export interface UserProfile {
  id: string;
  name: string;
  email?: string;
  occupation?: string;
  preferences: {
    country: string;
    household_size: number;
    diet: string;
    commute_mode: string;
    budget_level: string;
    electricity_source?: string;
    electricity_kwh_per_year?: number;
  };
}

export interface CarbonSummary {
  user_id: string;
  total_emissions_kg_co2e: number;
  category_emissions: Record<string, number>;
  category_shares_pct: Record<string, number>;
  dominant_source: string;
  human_readable_summary: string;
  month_over_month_change_pct?: number;
  monthly_goal_kg?: number;
}

export interface RecommendationItem {
  id: string;
  title: string;
  category: string;
  description: string;
  why_explanation?: string;
  carbon_savings_kg: number;
  impact_score: number;
  effort_level: 'low' | 'medium' | 'high';
  cost_level: 'free' | 'low' | 'medium' | 'high';
  adoption_probability: number;
  annual_cost_savings_usd?: number;
}

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp?: number;
  confidence?: 'low' | 'medium' | 'high';
  fallback_mode?: 'none' | 'demo' | 'weak_rag' | 'missing_data' | 'clarification';
  response_source?: 'rag' | 'rag_profile' | 'profile' | 'recommendations' | 'demo' | 'clarification';
  suggested_follow_up_questions?: string[];
  used_demo_data?: boolean;
  grounded_facts?: string[];
}

export interface JourneyMonth {
  month: string;        // e.g. "Jul 2024"
  emissions_kg: number;
  savings_kg: number;   // vs. baseline
}

export interface Milestone {
  id: string;
  title: string;
  description: string;
  achieved_at: string;  // ISO date string
  icon: string;         // lucide icon name
  color: string;        // Tailwind color class
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  unlocked: boolean;
  progress?: number;    // 0–100
}

export interface BreakdownCategory {
  key: string;
  label: string;
  emissions_kg: number;
  share_pct: number;
  color: string;
  icon: string;
  subcategories: { label: string; value_kg: number }[];
  comparison_text: string;
}
