from .schemas import ClimateCoachSummaryRequest, ExplanationResponse
from .gemini_client import GeminiClient
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser

class ClimateCoach:
    """Provides high-level insights and coaching."""
    
    def __init__(self):
        self.client = GeminiClient()
        self.parser = ResponseParser()
        
    def generate_summary(self, request: ClimateCoachSummaryRequest) -> ExplanationResponse:
        """Generates an engaging coaching summary."""
        prompt = PromptBuilder.build_summary_prompt(
            total=request.total_emissions,
            dominant=request.dominant_category,
            recs=request.recommendations,
            tone=request.tone
        )
        
        text = self.client.generate_content(prompt)
        text = self.parser.clean_markdown(text)
        
        return ExplanationResponse(
            explanation_text=text,
            model_used=self.client.model_name
        )
