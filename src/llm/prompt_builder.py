import json
from typing import Dict, Any, List
from src.rag.schemas import RetrievalResult

class PromptBuilder:
    """Builds safe, constrained prompts for Gemini."""
    
    @staticmethod
    def build_footprint_explanation(data: Dict[str, Any], tone: str) -> str:
        return f"""
You are an expert climate coach. Your tone should be {tone}.
Explain the following carbon footprint profile to the user.
Do NOT invent any numbers. Only use the numbers provided below.
Focus on the dominant source and provide actionable insights.

Profile Data:
{json.dumps(data, indent=2)}

Explanation:
"""

    @staticmethod
    def build_recommendation_explanation(data: Dict[str, Any], tone: str) -> str:
        return f"""
You are an expert climate coach. Your tone should be {tone}.
Explain the following recommended action and why it was selected for the user.
Do NOT invent impact scores or carbon savings. Use exactly what is provided.

Recommendation Data:
{json.dumps(data, indent=2)}

Explanation:
"""

    @staticmethod
    def build_rag_qa_prompt(query: str, context_chunks: List[RetrievalResult], tone: str) -> str:
        context_str = ""
        for i, res in enumerate(context_chunks):
            context_str += f"--- Document {i+1} (Source: {res.chunk.metadata.source}) ---\n"
            context_str += f"{res.chunk.text}\n\n"
            
        return f"""
You are an expert climate assistant. Your tone should be {tone}.
Answer the user's question based ONLY on the provided context below.
If the answer is not contained in the context, reply EXACTLY with:
"I do not have enough information in my knowledge base to answer that."
Do NOT guess or hallucinate. Do NOT compute new emission factors.

Context:
{context_str}

Question: {query}
Answer:
"""

    @staticmethod
    def build_grounded_qa_prompt(query: str, context_chunks: List[RetrievalResult], tone: str) -> str:
        context_str = ""
        for i, res in enumerate(context_chunks):
            context_str += f"--- Document {i+1} (Source: {res.chunk.metadata.source}) ---\n"
            context_str += f"{res.chunk.text}\n\n"
            
        return f"""
You are an expert climate coach. Your tone should be {tone}.
Answer the user's question using the provided context chunks below.
Return your response as a JSON object matching this schema:
{{
  "answer": "A friendly, comprehensive answer directly answering the question using facts from the context. Do not invent any numbers.",
  "grounded_facts": ["Fact 1 used in the answer", "Fact 2 used in the answer"],
  "suggested_follow_up_questions": ["Suggested follow-up question 1", "Suggested follow-up question 2"]
}}

Context:
{context_str}

Question: {query}
JSON Output:
"""

    @staticmethod
    def build_fallback_qa_prompt(query: str, facts: Dict[str, Any], context_chunks: List[RetrievalResult], tone: str) -> str:
        context_str = ""
        if context_chunks:
            for i, res in enumerate(context_chunks):
                context_str += f"--- Weak Document {i+1} (Source: {res.chunk.metadata.source}) ---\n"
                context_str += f"{res.chunk.text}\n\n"
                
        facts_str = json.dumps(facts, indent=2)
        
        weak_context_prompt = f"Weak Context Chunks (use with caution):\n{context_str}" if context_str else ""
        
        return f"""
You are an expert climate coach. Your tone should be {tone}.
The user has asked a question: "{query}"
The specific knowledge base matches for this question are very weak or missing.
To provide a helpful answer, use the user's structured profile facts and safe general climate science principles.

User Profile & Platform Facts:
{facts_str}

{weak_context_prompt}

Your output MUST be a JSON object containing:
- "answer": A friendly, helpful fallback answer that starts with a direct response to the question, provides a safe general explanation of the climate science, and gives exactly one actionable suggestion based on their footprint profile or recommendations. Do not claim absolute certainty.
- "grounded_facts": Short factual bullets about the user's actual profile (e.g., "Dominant emission source is transport", "Total footprint is 7240 kg").
- "suggested_follow_up_questions": [Exactly two relevant follow-up questions related to their footprint or the action you suggested].

JSON Output matching this schema:
{{
  "answer": "...",
  "grounded_facts": ["...", "..."],
  "suggested_follow_up_questions": ["...", "..."]
}}
"""

    @staticmethod
    def build_clarification_prompt(query: str, tone: str) -> str:
        return f"""
You are an expert climate coach. Your tone should be {tone}.
The user query is vague: "{query}". It is too short or lacks specific details for a helpful response.
You must guide the user to clarify their intent by offering options.

Your output MUST be a JSON object containing:
- "answer": A polite, welcoming greeting guiding them to specify what they want to know (e.g. asking them if they want to talk about transportation, food, home electricity, or waste).
- "grounded_facts": [],
- "suggested_follow_up_questions": [Three specific and interesting follow-up choices they can click, e.g. "Why is my footprint high?", "What should I reduce first?", "How much can I save by using public transport?"]

JSON Output matching this schema:
{{
  "answer": "...",
  "grounded_facts": [],
  "suggested_follow_up_questions": ["...", "...", "..."]
}}
"""

    @staticmethod
    def build_summary_prompt(total: float, dominant: str, recs: List[Dict[str, Any]], tone: str) -> str:
        return f"""
You are an expert climate coach. Your tone should be {tone}.
Write a short, engaging summary of the user's footprint and top recommendations.
Do NOT invent any numbers. Only use the numbers provided below.

Total Emissions: {total} kg CO2e
Dominant Source: {dominant}

Top Recommendations:
{json.dumps(recs, indent=2)}

Summary:
"""
