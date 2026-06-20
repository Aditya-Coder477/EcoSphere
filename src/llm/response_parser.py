import re

class ResponseParser:
    """Parses and cleans LLM outputs."""
    
    @staticmethod
    def clean_markdown(text: str) -> str:
        """Strips generic markdown wrappers if present."""
        text = text.strip()
        # Remove standard markdown code blocks if the LLM wrapped everything in it
        if text.startswith("```") and text.endswith("```"):
            lines = text.split("\n")
            if len(lines) >= 2:
                # Remove first and last lines
                return "\n".join(lines[1:-1]).strip()
        return text
