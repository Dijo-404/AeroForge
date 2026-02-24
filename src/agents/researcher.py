# src/agents/researcher.py
import json
from .orchestrators import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Research Agent", thinking_level="medium")
        
    def execute(self, session_state: dict):
        """
        Parallel Fan-Out/Gather Pattern to search Vertex AI Data Stores.
        Uses Generative Models to extract structured constraints.
        """
        intent = session_state.get("query_intent", "alloy research")
        print(f"[{self.name}] Querying Vertex/Gemini (RAG) for: {intent}")
        
        try:
            from google import genai
            from google.genai import types
            from src.config import settings
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=f"Analyze this alloy request and propose a formulation strategy: {intent}",
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert aerospace materials scientist. Output ONLY valid JSON containing three keys: 'required_properties' (list of strings), 'suggested_elements' (list of string atomic symbols like ['Ti', 'Al']), and 'thermodynamic_constraints' (string).",
                    response_mime_type="application/json",
                ),
            )
            
            research_plan = json.loads(response.text)
            
        except Exception as e:
            print(f"[{self.name}] API Error: {e}. Falling back to default mock.")
            research_plan = {
                "required_properties": ["high_tensile_strength", "oxidation_resistance", "low_weight"],
                "suggested_elements": ["Ti", "Al", "V"],
                "thermodynamic_constraints": "Maintain phase stability below 1000K."
            }
        
        # Save to shared session state
        session_state["research_plan"] = research_plan
        session_state["next_agent"] = "composition_loop"
        
        print(f"[{self.name}] Saved research_plan to state.")
        return session_state
