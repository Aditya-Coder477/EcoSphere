"""
ranker.py
=========
Filters, scores, and sorts actions.
"""

from typing import List

from .schemas import RecommendationContext, RankedRecommendation
from .action_library import get_action_library
from .rules import AdoptionEvaluator, RelevanceEvaluator
from .scoring import ImpactScoreCalculator

class RuleBasedRanker:
    """Core ranking logic combining rules and scores."""
    
    def __init__(self):
        self.actions = get_action_library()

    def rank(self, ctx: RecommendationContext, top_n: int = 3) -> List[RankedRecommendation]:
        """Filters out ineligible actions, scores the rest, and returns the top N."""
        results = []
        
        for action in self.actions:
            # 1. Eligibility Check
            try:
                if not action.eligibility_rule(ctx):
                    continue
            except Exception:
                # Safely skip if rule errors out due to missing data
                continue
                
            # 2. Score Components
            carbon_saved_kg = ImpactScoreCalculator.calculate_carbon_saved_kg(action, ctx)
            if carbon_saved_kg <= 0:
                continue # No impact possible

            adoption_prob = AdoptionEvaluator.calculate(action, ctx)
            relevance = RelevanceEvaluator.calculate(action, ctx)
            effort = ImpactScoreCalculator.calculate_adjusted_effort(action, ctx)
            cost = ImpactScoreCalculator.calculate_adjusted_cost(action, ctx)
            
            # 3. Final Impact Score
            impact_score = ImpactScoreCalculator.calculate_impact_score(
                carbon_saved_kg=carbon_saved_kg,
                adoption_prob=adoption_prob,
                relevance=relevance,
                effort=effort,
                cost=cost
            )
            
            # Determine Impact Level label
            # These thresholds could be configurable. 
            if impact_score > 500:
                impact_level = "high"
            elif impact_score > 100:
                impact_level = "medium"
            else:
                impact_level = "low"
                
            # 4. Generate Explanation
            pct_val = 0.0
            if ctx.total_emissions_kg_co2e > 0:
                pct_val = (ctx.category_emissions.get(action.category, 0) / ctx.total_emissions_kg_co2e) * 100
                
            try:
                explanation = action.explanation_template.format(
                    cat_pct=round(pct_val, 1),
                    city_type=ctx.city_type
                )
            except KeyError:
                # Fallback if template expects formatting variables not provided
                explanation = action.explanation_template
            
            rec = RankedRecommendation(
                action_id=action.action_id,
                title=action.title,
                category=action.category,
                description=action.description,
                impact_score=impact_score,
                carbon_saved_kg=carbon_saved_kg,
                adoption_probability=adoption_prob,
                relevance=relevance,
                effort=effort,
                cost=cost,
                ranking_position=0, # will be set during sort
                impact_level=impact_level,
                explanation=explanation
            )
            results.append(rec)
            
        # 5. Sort descending by impact score
        results.sort(key=lambda r: r.impact_score, reverse=True)
        
        # 6. Assign ranking position and slice
        final_results = results[:top_n]
        for i, rec in enumerate(final_results):
            rec.ranking_position = i + 1
            
        return final_results
