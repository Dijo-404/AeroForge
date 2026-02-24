# src/agents/orchestrators.py
import json

class BaseAgent:
    def __init__(self, name: str, thinking_level: str):
        self.name = name
        self.thinking_level = thinking_level
        self.sub_agents = []

    def set_sub_agents(self, agents: list):
        self.sub_agents = agents

class DiscoveryLeadAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Discovery Lead", thinking_level="low")
    
    def dispatch(self, user_intent: str, session_state: dict):
        """
        Coordinator/Dispatcher Pattern.
        Analyzes user intent and routes to specialized sub-agents.
        """
        print(f"[{self.name}] Analyzing intent: '{user_intent}' with thinking={self.thinking_level}")
        # In a real implementation, an LLM call would dictate the route.
        # For our sequential pipeline, we just trigger the first step of the pipeline.
        session_state["query_intent"] = user_intent
        print(f"[{self.name}] Routing to Research Agent...")
        session_state["next_agent"] = "research"
        return session_state

class SimulationLeadAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Simulation Lead", thinking_level="low")
        
    def dispatch(self, formulation_data: dict, session_state: dict):
        """
        Takes the finalized alloy candidate and routes it to the Simulation tools.
        """
        print(f"[{self.name}] Routing alloy candidate to FEA Simulation...")
        # Hands off to the FEA simulation sub-agent
        session_state["simulation_target"] = formulation_data
        return session_state
