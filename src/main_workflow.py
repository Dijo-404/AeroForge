# src/main_workflow.py
import json
import logging
from src.agents.orchestrators import DiscoveryLeadAgent, SimulationLeadAgent
from src.agents.researcher import ResearchAgent
from src.agents.composition_loop import run_composition_loop
from src.tools.fea_simulation import run_fea_analysis
from src.synthesis.multimodal_reporter import finalize_presentation

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AeroForge Workflow")

def execute_pipeline(user_prompt: str):
    """
    Main entry point for the AeroForge Autonomous Multi-Agent System.
    Implements Shared Session State, Sequential Pipeline, and Loop primitive orchestration.
    """
    # Shared Session State initialization
    # Strict key-value constraints for basic serializable types
    session_state = {
        "initial_prompt": user_prompt,
        "query_intent": None,
        "research_plan": None,
        "final_formulation": None,
        "simulation_target": None,
        "simulation_results": None,
        "next_agent": "discovery_lead",
        "loop_iterations": 0
    }
    
    logger.info("Initializing Agent Hierarchy...")
    discovery_lead = DiscoveryLeadAgent()
    research_agent = ResearchAgent()
    simulation_lead = SimulationLeadAgent()
    
    # --- SEQUENTIAL PIPELINE ---
    
    # 1. Dispatcher Action
    logger.info("[Step 1] Coordinator/Dispatcher")
    session_state = discovery_lead.dispatch(user_prompt, session_state)
    
    # 2. Parallel Fan-Out/Gather (Simulated via RAG research node)
    logger.info("[Step 2] Grounding via Vertex AI (Knowledge Retrieval)")
    session_state = research_agent.execute(session_state)
    
    # 3. Generator & Critic Loop Pattern
    logger.info("[Step 3] Loop Primitive (Composition & Validation)")
    try:
        session_state = run_composition_loop(session_state, max_iterations=5)
    except Exception as e:
        logger.error(f"Formulation failed: {e}")
        return session_state
        
    # 4. Simulation Routing
    logger.info("[Step 4] Handoff to Simulation Pipeline")
    session_state = simulation_lead.dispatch(session_state["final_formulation"], session_state)
    
    # 5. Deterministic Validation (FEA)
    logger.info("[Step 5] Deterministic Physics Validation (PyAnsys)")
    fea_result_json = run_fea_analysis(
        mesh_geometry="high_pressure_turbine_blade_v1",
        thermal_load=1500.0,
        structural_load=650.0
    )
    fea_results = json.loads(fea_result_json)
    session_state["simulation_results"] = fea_results
    
    logger.info(f"Final Validation: Survived = {fea_results['survived']}")
    if not fea_results["survived"]:
        logger.warning(f"Component Failure: {fea_results['failure_mode']}")
        
    logger.info("[Step 6] Multimodal Synthesis Layer")
    svg_path, audio_path = finalize_presentation(session_state)
    logger.info(f"Generated Presentation Assets: {svg_path}, {audio_path}")
        
    logger.info("Pipeline execution complete.")
    logger.info("Printing final serializable session_state:")
    print(json.dumps(session_state, indent=2))
    return session_state

if __name__ == "__main__":
    import sys
    prompt = sys.argv[1] if len(sys.argv) > 1 else "I need a high-temperature lightweight aerospace alloy."
    execute_pipeline(prompt)
