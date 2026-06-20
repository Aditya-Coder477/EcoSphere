from typing import Optional, Dict, Any, List
from .schemas import ExplanationRequest, ExplanationResponse, SourceCitation
from .exceptions import ContextMissingError
from .gemini_client import GeminiClient
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from src.rag.rag_service import RAGService

class ExplanationService:
    """Orchestrates explanations and answers using Gemini and RAG."""
    
    def __init__(self, rag_service: Optional[RAGService] = None, db = None):
        self.client = GeminiClient()
        self.rag_service = rag_service
        self.db = db
        self.parser = ResponseParser()
        
    def generate_explanation(self, request: ExplanationRequest) -> ExplanationResponse:
        """Generates an explanation based on the context type."""
        
        if request.context_type == "footprint":
            prompt = PromptBuilder.build_footprint_explanation(request.context_data, request.tone)
            text = self.client.generate_content(prompt)
            text = self.parser.clean_markdown(text)
            return ExplanationResponse(
                explanation_text=text,
                model_used=self.client.model_name,
                confidence="high",
                fallback_mode="none",
                response_source="profile",
                suggested_follow_up_questions=[],
                used_demo_data=False,
                grounded_facts=[]
            )
            
        elif request.context_type == "recommendation":
            prompt = PromptBuilder.build_recommendation_explanation(request.context_data, request.tone)
            text = self.client.generate_content(prompt)
            text = self.parser.clean_markdown(text)
            return ExplanationResponse(
                explanation_text=text,
                model_used=self.client.model_name,
                confidence="high",
                fallback_mode="none",
                response_source="recommendations",
                suggested_follow_up_questions=[],
                used_demo_data=False,
                grounded_facts=[]
            )
            
        elif request.context_type == "rag_qa":
            if not request.query:
                raise ValueError("Query is required for rag_qa context type.")
            if not self.rag_service:
                raise ValueError("RAGService is required for rag_qa context type.")
                
            return self.answer_rag_query(request.query, request.user_id, request.tone)
            
        else:
            raise ValueError(f"Unknown context_type: {request.context_type}")
            
    def answer_rag_query(self, query: str, user_id: str, tone: str = "friendly") -> ExplanationResponse:
        """Answers a question using RAG, falling back to structured and demo data."""
        
        # 1. Check for vague questions (Clarification mode)
        if self._is_vague(query):
            prompt = PromptBuilder.build_clarification_prompt(query, tone)
            text = self.client.generate_content(prompt, response_mime_type="application/json")
            parsed = self._parse_json(text)
            
            return ExplanationResponse(
                explanation_text=parsed["answer"],
                model_used=self.client.model_name,
                sources=[],
                confidence="low",
                fallback_mode="clarification",
                response_source="clarification",
                suggested_follow_up_questions=parsed["suggested_follow_up_questions"],
                used_demo_data=False,
                grounded_facts=[]
            )
            
        # 2. Query RAG
        retrieval_res = self.rag_service.query(query, top_k=3)
        context_chunks = retrieval_res.results
        weak_context = retrieval_res.weak_context
        
        top_score = max([r.score for r in context_chunks]) if context_chunks else 0.0
        
        # 3. Retrieve user profile / platform facts
        facts, used_demo_data = self._get_user_facts(user_id)
        
        # 4. Determine response mode and source
        if not weak_context and top_score >= 0.70:
            # Strong context: grounded RAG answer
            fallback_mode = "none"
            response_source = "rag_profile" if facts.get("profile") else "rag"
            
            prompt = PromptBuilder.build_grounded_qa_prompt(query, context_chunks, tone)
            text = self.client.generate_content(prompt, response_mime_type="application/json")
            parsed = self._parse_json(text)
        else:
            # Weak/missing context: fallback response using facts
            fallback_mode = "demo" if used_demo_data else "weak_rag"
            response_source = "demo" if used_demo_data else "profile"
            
            prompt = PromptBuilder.build_fallback_qa_prompt(query, facts, context_chunks, tone)
            text = self.client.generate_content(prompt, response_mime_type="application/json")
            parsed = self._parse_json(text)
            
        # 5. Compute confidence level deterministically on the backend (Refinement 3)
        if top_score >= 0.70:
            confidence = "high" if not used_demo_data else "medium"
        elif 0.50 <= top_score < 0.70:
            confidence = "medium" if not used_demo_data else "low"
        else:
            confidence = "medium" if not used_demo_data else "low"
            
        # 6. Format sources
        sources = [
            SourceCitation(source=res.chunk.metadata.source, chunk_text=res.chunk.text)
            for res in context_chunks
        ] if context_chunks else []
        
        return ExplanationResponse(
            explanation_text=parsed["answer"],
            model_used=self.client.model_name,
            sources=sources,
            confidence=confidence,
            fallback_mode=fallback_mode,
            response_source=response_source,
            suggested_follow_up_questions=parsed["suggested_follow_up_questions"],
            used_demo_data=used_demo_data,
            grounded_facts=parsed["grounded_facts"]
        )
        
    def _is_vague(self, query: str) -> bool:
        q = query.strip().lower()
        if len(q) < 4:
            return True
        if q in {"hi", "hello", "hey", "test", "help", "yo", "hola", "greetings", "anyone there"}:
            return True
        return False
        
    def _parse_json(self, text: str) -> dict:
        import json
        import re
        try:
            return json.loads(text)
        except Exception:
            try:
                match = re.search(r"\{.*\}", text, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception:
                pass
            return {
                "answer": text,
                "grounded_facts": [],
                "suggested_follow_up_questions": []
            }
            
    def _get_user_facts(self, user_id: str) -> tuple[dict, bool]:
        """Retrieves user facts from SQLite DB, or falls back to mock/demo data."""
        # Use provided session or create a new local one (Refinement 1)
        db = self.db
        created_local_db = False
        
        if db is None:
            try:
                from backend.app.db.session import SessionLocal
                db = SessionLocal()
                created_local_db = True
            except Exception:
                pass
                
        if db is None:
            # If DB is completely unavailable/failed to load, fall back to mocks
            from src.llm.mocks import mock_user_profile, mock_carbon_summary, mock_recommendations, mock_journey_data
            facts = {
                "profile": mock_user_profile,
                "carbon_summary": mock_carbon_summary,
                "recommendations": mock_recommendations,
                "journey": mock_journey_data
            }
            return facts, True
            
        try:
            from backend.app.db import models
            
            # 1. Fetch user profile
            user = db.query(models.User).filter(models.User.id == user_id).first()
            
            # 2. Fetch latest carbon profile
            carbon = db.query(models.CarbonProfile).filter(models.CarbonProfile.user_id == user_id).order_by(models.CarbonProfile.created_at.desc()).first()
            
            # 3. Fetch recommendation history
            recs = db.query(models.RecommendationHistory).filter(models.RecommendationHistory.user_id == user_id).all()
            
            if not user and not carbon:
                # No database record for user - use mock data
                from src.llm.mocks import mock_user_profile, mock_carbon_summary, mock_recommendations, mock_journey_data
                facts = {
                    "profile": mock_user_profile,
                    "carbon_summary": mock_carbon_summary,
                    "recommendations": mock_recommendations,
                    "journey": mock_journey_data
                }
                return facts, True
                
            profile_dict = {
                "user_id": user.id if user else user_id,
                "occupation": user.occupation if user else "",
                "city_type": user.city_type if user else "",
                "budget_profile": user.budget_profile if user else "medium",
                "is_vegetarian": user.is_vegetarian if user else False,
            }
            
            if carbon:
                carbon_dict = {
                    "total_emissions_kg_co2e": carbon.total_emissions_kg_co2e,
                    "category_emissions": carbon.category_emissions,
                    "dominant_emission_source": carbon.dominant_emission_source,
                }
            else:
                from src.llm.mocks import mock_carbon_summary
                carbon_dict = mock_carbon_summary
                
            recs_list = []
            if recs:
                for r in recs:
                    recs_list.append({
                        "action_id": r.action_id,
                        "category": r.category,
                        "impact_score": r.impact_score,
                        "impact_level": r.impact_level
                    })
            else:
                from src.llm.mocks import mock_recommendations
                recs_list = mock_recommendations
                
            facts = {
                "profile": profile_dict,
                "carbon_summary": carbon_dict,
                "recommendations": recs_list,
                "journey": {
                    "cumulative_savings_kg": 0,
                    "streak_months": 0,
                    "monthly_history": []
                }
            }
            return facts, False
            
        except Exception:
            from src.llm.mocks import mock_user_profile, mock_carbon_summary, mock_recommendations, mock_journey_data
            facts = {
                "profile": mock_user_profile,
                "carbon_summary": mock_carbon_summary,
                "recommendations": mock_recommendations,
                "journey": mock_journey_data
            }
            return facts, True
        finally:
            if created_local_db and db:
                db.close()
