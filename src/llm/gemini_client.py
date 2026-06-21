import os
from typing import Optional
from google import genai
from google.genai import types
from tenacity import retry, stop_after_attempt, wait_exponential
from .exceptions import GeminiAPIError
from src.utils.logger import get_logger

log = get_logger(__name__)

class GeminiClient:
    """Wrapper around Gemini API using the modern google-genai SDK."""
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            log.warning("GEMINI_API_KEY environment variable not set. LLM calls will fail.")
            # Use a dummy key to prevent Client instantiation crash in testing/dev environments
            api_key = "dummy-api-key-placeholder"
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_content(self, prompt: str, temperature: float = 0.2, response_mime_type: Optional[str] = None) -> str:
        """Generates content safely with retries."""
        try:
            log.debug(f"Calling Gemini ({self.model_name}) with prompt length: {len(prompt)}")
            
            config_args = {"temperature": temperature}
            if response_mime_type:
                config_args["response_mime_type"] = response_mime_type
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**config_args)
            )
                
            if not response.text:
                raise GeminiAPIError("Empty response received from Gemini.")
                
            return response.text
        except Exception as e:
            log.error(f"Gemini API failure: {e}")
            raise GeminiAPIError(f"Failed to generate content: {e}")
