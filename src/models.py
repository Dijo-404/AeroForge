# src/models.py
"""
Data models for AeroForge Autonomous Multi-Agent System.
Implements SessionState and related data structures with validation.
"""
import json
from typing import Any, Optional, TypedDict

# Periodic table of elements (valid element symbols)
PERIODIC_TABLE = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",
    "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
    "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
}


# Supporting data structures
class ResearchPlan(TypedDict, total=False):
    """Research plan synthesized from knowledge retrieval."""
    required_properties: list[str]
    suggested_elements: list[str]
    thermodynamic_constraints: str


class AlloyCandidate(TypedDict, total=False):
    """Alloy formulation candidate."""
    matrix: list[str]  # List of atomic symbols
    target_temp_K: int  # Target operating temperature in Kelvin


class ThermoResult(TypedDict, total=False):
    """Thermodynamic validation results from PyCALPHAD."""
    is_stable: bool
    phases: list[str]
    temperature: int


class FEAResult(TypedDict, total=False):
    """Finite Element Analysis simulation results."""
    survived: bool
    failure_mode: Optional[str]
    max_stress_mpa: float
    max_temperature_k: float


# Validation functions for data models

def validate_research_plan(plan: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate ResearchPlan data model.

    Args:
        plan: ResearchPlan dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
    - required_properties must be a non-empty list of strings
    - suggested_elements must be a list of valid element symbols
    - thermodynamic_constraints must be a non-empty string

    Requirements: 14.1, 18.1
    """
    errors = []

    # Validate required_properties
    if "required_properties" not in plan:
        errors.append("Missing required field: required_properties")
    elif not isinstance(plan["required_properties"], list):
        errors.append("required_properties must be a list")
    elif len(plan["required_properties"]) == 0:
        errors.append("required_properties cannot be empty")
    elif not all(isinstance(prop, str) for prop in plan["required_properties"]):
        errors.append("All required_properties must be strings")

    # Validate suggested_elements
    if "suggested_elements" not in plan:
        errors.append("Missing required field: suggested_elements")
    elif not isinstance(plan["suggested_elements"], list):
        errors.append("suggested_elements must be a list")
    else:
        for element in plan["suggested_elements"]:
            if not isinstance(element, str):
                errors.append(f"Element must be a string, got: {type(element).__name__}")
            elif element not in PERIODIC_TABLE:
                errors.append(f"Invalid element symbol: {element}")

    # Validate thermodynamic_constraints
    if "thermodynamic_constraints" not in plan:
        errors.append("Missing required field: thermodynamic_constraints")
    elif not isinstance(plan["thermodynamic_constraints"], str):
        errors.append("thermodynamic_constraints must be a string")
    elif not plan["thermodynamic_constraints"].strip():
        errors.append("thermodynamic_constraints cannot be empty")

    return len(errors) == 0, errors


def validate_alloy_candidate(candidate: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate AlloyCandidate data model.

    Args:
        candidate: AlloyCandidate dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
    - matrix must be a non-empty list of valid element symbols
    - target_temp_K must be a positive integer

    Requirements: 14.2, 18.1, 18.2
    """
    errors = []

    # Validate matrix
    if "matrix" not in candidate:
        errors.append("Missing required field: matrix")
    elif not isinstance(candidate["matrix"], list):
        errors.append("matrix must be a list")
    elif len(candidate["matrix"]) == 0:
        errors.append("matrix cannot be empty")
    else:
        for element in candidate["matrix"]:
            if not isinstance(element, str):
                errors.append(f"Element must be a string, got: {type(element).__name__}")
            elif element not in PERIODIC_TABLE:
                errors.append(f"Invalid element symbol: {element}")

    # Validate target_temp_K
    if "target_temp_K" not in candidate:
        errors.append("Missing required field: target_temp_K")
    elif not isinstance(candidate["target_temp_K"], (int, float)):
        errors.append("target_temp_K must be a number")
    elif candidate["target_temp_K"] <= 0:
        errors.append("target_temp_K must be positive")

    return len(errors) == 0, errors


def validate_thermo_result(result: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate ThermoResult data model.

    Args:
        result: ThermoResult dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
    - is_stable must be a boolean
    - phases must be a list of strings
    - temperature must be a positive number

    Requirements: 14.3, 18.2
    """
    errors = []

    # Validate is_stable
    if "is_stable" not in result:
        errors.append("Missing required field: is_stable")
    elif not isinstance(result["is_stable"], bool):
        errors.append("is_stable must be a boolean")

    # Validate phases
    if "phases" not in result:
        errors.append("Missing required field: phases")
    elif not isinstance(result["phases"], list):
        errors.append("phases must be a list")
    elif not all(isinstance(phase, str) for phase in result["phases"]):
        errors.append("All phases must be strings")

    # Validate temperature
    if "temperature" not in result:
        errors.append("Missing required field: temperature")
    elif not isinstance(result["temperature"], (int, float)):
        errors.append("temperature must be a number")
    elif result["temperature"] <= 0:
        errors.append("temperature must be positive")

    return len(errors) == 0, errors


def validate_fea_result(result: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate FEAResult data model.

    Args:
        result: FEAResult dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
    - survived must be a boolean
    - failure_mode must be a string or None
    - max_stress_mpa must be a non-negative number
    - max_temperature_k must be a positive number

    Requirements: 14.4, 18.2, 18.3
    """
    errors = []

    # Validate survived
    if "survived" not in result:
        errors.append("Missing required field: survived")
    elif not isinstance(result["survived"], bool):
        errors.append("survived must be a boolean")

    # Validate failure_mode
    if "failure_mode" not in result:
        errors.append("Missing required field: failure_mode")
    elif result["failure_mode"] is not None and not isinstance(result["failure_mode"], str):
        errors.append("failure_mode must be a string or None")

    # Validate max_stress_mpa
    if "max_stress_mpa" not in result:
        errors.append("Missing required field: max_stress_mpa")
    elif not isinstance(result["max_stress_mpa"], (int, float)):
        errors.append("max_stress_mpa must be a number")
    elif result["max_stress_mpa"] < 0:
        errors.append("max_stress_mpa must be non-negative")

    # Validate max_temperature_k
    if "max_temperature_k" not in result:
        errors.append("Missing required field: max_temperature_k")
    elif not isinstance(result["max_temperature_k"], (int, float)):
        errors.append("max_temperature_k must be a number")
    elif result["max_temperature_k"] <= 0:
        errors.append("max_temperature_k must be positive")

    return len(errors) == 0, errors


# Main session state structure
class SessionState(TypedDict, total=False):
    """
    Shared session state for the AeroForge multi-agent pipeline.
    All values must be JSON-serializable (basic types, dicts, lists).

    Requirements: 7.1, 7.2, 7.3, 14.5
    """
    initial_prompt: str  # Original user request (required)
    query_intent: Optional[str]  # Parsed intent from Discovery Lead
    research_plan: Optional[ResearchPlan]  # Synthesized research findings
    proposed_alloy: Optional[AlloyCandidate]  # Current candidate formulation
    final_formulation: Optional[AlloyCandidate]  # Validated formulation
    thermo_validation: Optional[ThermoResult]  # PyCALPHAD results
    simulation_target: Optional[AlloyCandidate]  # Formulation for FEA
    simulation_results: Optional[FEAResult]  # FEA output
    next_agent: str  # Routing information
    loop_iterations: int  # Composition loop counter


# Valid agent identifiers for routing
VALID_AGENTS = {
    "discovery_lead",
    "research",
    "composition_loop",
    "simulation_lead",
    "fea",
    "complete"
}


def is_json_serializable(obj: Any) -> bool:
    """
    Check if an object is JSON-serializable.

    Args:
        obj: Object to check

    Returns:
        True if serializable, False otherwise
    """
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


def validate_session_state(state: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate SessionState for correctness and serializability.

    Args:
        state: Session state dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)

    Validation Rules:
    - All values must be JSON-serializable
    - initial_prompt is required and non-empty
    - loop_iterations must be non-negative integer
    - next_agent must be valid agent identifier
    """
    errors = []

    # Check required field: initial_prompt
    if "initial_prompt" not in state:
        errors.append("Missing required field: initial_prompt")
    elif not isinstance(state["initial_prompt"], str):
        errors.append("initial_prompt must be a string")
    elif not state["initial_prompt"].strip():
        errors.append("initial_prompt cannot be empty")

    # Validate loop_iterations if present
    if "loop_iterations" in state:
        if not isinstance(state["loop_iterations"], int):
            errors.append("loop_iterations must be an integer")
        elif state["loop_iterations"] < 0:
            errors.append("loop_iterations must be non-negative")

    # Validate next_agent if present
    if "next_agent" in state:
        if not isinstance(state["next_agent"], str):
            errors.append("next_agent must be a string")
        elif state["next_agent"] not in VALID_AGENTS:
            errors.append(f"next_agent must be one of {VALID_AGENTS}, got: {state['next_agent']}")

    # Check JSON serializability of all values
    for key, value in state.items():
        if not is_json_serializable(value):
            errors.append(f"Field '{key}' is not JSON-serializable")

    return len(errors) == 0, errors


def initialize_session_state(initial_prompt: str, next_agent: str = "discovery_lead") -> SessionState:
    """
    Initialize a new SessionState with default values.

    Args:
        initial_prompt: The original user request
        next_agent: Initial routing target (default: "discovery_lead")

    Returns:
        Initialized SessionState dictionary

    Raises:
        ValueError: If initial_prompt is empty or next_agent is invalid
    """
    if not initial_prompt or not initial_prompt.strip():
        raise ValueError("initial_prompt cannot be empty")

    if next_agent not in VALID_AGENTS:
        raise ValueError(f"next_agent must be one of {VALID_AGENTS}, got: {next_agent}")

    state: SessionState = {
        "initial_prompt": initial_prompt,
        "query_intent": None,
        "research_plan": None,
        "proposed_alloy": None,
        "final_formulation": None,
        "thermo_validation": None,
        "simulation_target": None,
        "simulation_results": None,
        "next_agent": next_agent,
        "loop_iterations": 0
    }

    return state


def update_session_state(state: SessionState, **updates: Any) -> SessionState:
    """
    Update session state with new values and validate.

    Args:
        state: Current session state
        **updates: Key-value pairs to update

    Returns:
        Updated session state

    Raises:
        ValueError: If updates result in invalid state
    """
    updated_state = {**state, **updates}

    is_valid, errors = validate_session_state(updated_state)
    if not is_valid:
        raise ValueError(f"Invalid session state update: {'; '.join(errors)}")

    return updated_state
