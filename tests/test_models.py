# tests/test_models.py
"""
Unit tests for SessionState data model and validation functions.
"""
import pytest
import json
from src.models import (
    SessionState,
    ResearchPlan,
    AlloyCandidate,
    ThermoResult,
    FEAResult,
    PERIODIC_TABLE,
    is_json_serializable,
    validate_session_state,
    validate_research_plan,
    validate_alloy_candidate,
    validate_thermo_result,
    validate_fea_result,
    initialize_session_state,
    update_session_state,
    VALID_AGENTS
)


class TestJSONSerializability:
    """Test JSON serializability checking."""
    
    def test_serializable_basic_types(self):
        """Test that basic types are serializable."""
        assert is_json_serializable("string")
        assert is_json_serializable(42)
        assert is_json_serializable(3.14)
        assert is_json_serializable(True)
        assert is_json_serializable(None)
        assert is_json_serializable([1, 2, 3])
        assert is_json_serializable({"key": "value"})
    
    def test_serializable_nested_structures(self):
        """Test that nested structures are serializable."""
        nested = {
            "list": [1, 2, {"nested": "dict"}],
            "dict": {"a": 1, "b": [2, 3]},
            "mixed": [{"x": 1}, {"y": 2}]
        }
        assert is_json_serializable(nested)
    
    def test_non_serializable_objects(self):
        """Test that non-serializable objects are detected."""
        assert not is_json_serializable(object())
        assert not is_json_serializable(lambda x: x)
        assert not is_json_serializable(set([1, 2, 3]))


class TestValidateSessionState:
    """Test session state validation."""
    
    def test_valid_minimal_state(self):
        """Test validation of minimal valid state."""
        state = {
            "initial_prompt": "Test prompt",
            "next_agent": "discovery_lead",
            "loop_iterations": 0
        }
        is_valid, errors = validate_session_state(state)
        assert is_valid
        assert len(errors) == 0
    
    def test_valid_complete_state(self):
        """Test validation of complete state with all fields."""
        state = {
            "initial_prompt": "Design a high-temp alloy",
            "query_intent": "aerospace alloy",
            "research_plan": {
                "required_properties": ["strength", "heat_resistance"],
                "suggested_elements": ["Ti", "Al"],
                "thermodynamic_constraints": "stable below 1000K"
            },
            "proposed_alloy": {
                "matrix": ["Ti", "Al", "V"],
                "target_temp_K": 900
            },
            "final_formulation": {
                "matrix": ["Ti", "Al", "V"],
                "target_temp_K": 900
            },
            "thermo_validation": {
                "is_stable": True,
                "phases": ["alpha", "beta"],
                "temperature": 900
            },
            "simulation_target": {
                "matrix": ["Ti", "Al", "V"],
                "target_temp_K": 900
            },
            "simulation_results": {
                "survived": True,
                "failure_mode": None,
                "max_stress_mpa": 450.0,
                "max_temperature_k": 920.0
            },
            "next_agent": "complete",
            "loop_iterations": 2
        }
        is_valid, errors = validate_session_state(state)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_initial_prompt(self):
        """Test that missing initial_prompt is caught."""
        state = {"next_agent": "discovery_lead", "loop_iterations": 0}
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("initial_prompt" in err for err in errors)
    
    def test_empty_initial_prompt(self):
        """Test that empty initial_prompt is caught."""
        state = {"initial_prompt": "   ", "next_agent": "discovery_lead"}
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("empty" in err.lower() for err in errors)
    
    def test_invalid_initial_prompt_type(self):
        """Test that non-string initial_prompt is caught."""
        state = {"initial_prompt": 123, "next_agent": "discovery_lead"}
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("string" in err.lower() for err in errors)
    
    def test_negative_loop_iterations(self):
        """Test that negative loop_iterations is caught."""
        state = {
            "initial_prompt": "Test",
            "loop_iterations": -1
        }
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("non-negative" in err.lower() for err in errors)
    
    def test_invalid_loop_iterations_type(self):
        """Test that non-integer loop_iterations is caught."""
        state = {
            "initial_prompt": "Test",
            "loop_iterations": "5"
        }
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("integer" in err.lower() for err in errors)
    
    def test_invalid_next_agent(self):
        """Test that invalid next_agent is caught."""
        state = {
            "initial_prompt": "Test",
            "next_agent": "invalid_agent"
        }
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("invalid_agent" in err for err in errors)
    
    def test_invalid_next_agent_type(self):
        """Test that non-string next_agent is caught."""
        state = {
            "initial_prompt": "Test",
            "next_agent": 123
        }
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("string" in err.lower() for err in errors)
    
    def test_non_serializable_value(self):
        """Test that non-serializable values are caught."""
        state = {
            "initial_prompt": "Test",
            "research_plan": lambda x: x  # Non-serializable
        }
        is_valid, errors = validate_session_state(state)
        assert not is_valid
        assert any("serializable" in err.lower() for err in errors)


class TestInitializeSessionState:
    """Test session state initialization."""
    
    def test_initialize_with_defaults(self):
        """Test initialization with default values."""
        state = initialize_session_state("Test prompt")
        
        assert state["initial_prompt"] == "Test prompt"
        assert state["query_intent"] is None
        assert state["research_plan"] is None
        assert state["proposed_alloy"] is None
        assert state["final_formulation"] is None
        assert state["thermo_validation"] is None
        assert state["simulation_target"] is None
        assert state["simulation_results"] is None
        assert state["next_agent"] == "discovery_lead"
        assert state["loop_iterations"] == 0
    
    def test_initialize_with_custom_next_agent(self):
        """Test initialization with custom next_agent."""
        state = initialize_session_state("Test prompt", next_agent="research")
        assert state["next_agent"] == "research"
    
    def test_initialize_empty_prompt_raises(self):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            initialize_session_state("")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            initialize_session_state("   ")
    
    def test_initialize_invalid_next_agent_raises(self):
        """Test that invalid next_agent raises ValueError."""
        with pytest.raises(ValueError, match="must be one of"):
            initialize_session_state("Test", next_agent="invalid")
    
    def test_initialized_state_is_valid(self):
        """Test that initialized state passes validation."""
        state = initialize_session_state("Test prompt")
        is_valid, errors = validate_session_state(state)
        assert is_valid
        assert len(errors) == 0
    
    def test_initialized_state_is_serializable(self):
        """Test that initialized state is JSON-serializable."""
        state = initialize_session_state("Test prompt")
        json_str = json.dumps(state)
        assert json_str is not None
        
        # Verify round-trip
        restored = json.loads(json_str)
        assert restored["initial_prompt"] == "Test prompt"


class TestUpdateSessionState:
    """Test session state updates."""
    
    def test_update_single_field(self):
        """Test updating a single field."""
        state = initialize_session_state("Test")
        updated = update_session_state(state, query_intent="aerospace alloy")
        
        assert updated["query_intent"] == "aerospace alloy"
        assert updated["initial_prompt"] == "Test"
    
    def test_update_multiple_fields(self):
        """Test updating multiple fields."""
        state = initialize_session_state("Test")
        updated = update_session_state(
            state,
            query_intent="aerospace alloy",
            loop_iterations=1,
            next_agent="research"
        )
        
        assert updated["query_intent"] == "aerospace alloy"
        assert updated["loop_iterations"] == 1
        assert updated["next_agent"] == "research"
    
    def test_update_with_complex_data(self):
        """Test updating with complex nested data."""
        state = initialize_session_state("Test")
        research_plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti", "Al"],
            "thermodynamic_constraints": "stable"
        }
        updated = update_session_state(state, research_plan=research_plan)
        
        assert updated["research_plan"] == research_plan
    
    def test_update_invalid_raises(self):
        """Test that invalid updates raise ValueError."""
        state = initialize_session_state("Test")
        
        with pytest.raises(ValueError, match="Invalid session state"):
            update_session_state(state, loop_iterations=-1)
        
        with pytest.raises(ValueError, match="Invalid session state"):
            update_session_state(state, next_agent="invalid")
    
    def test_update_preserves_original(self):
        """Test that update doesn't modify original state."""
        state = initialize_session_state("Test")
        original_iterations = state["loop_iterations"]
        
        updated = update_session_state(state, loop_iterations=5)
        
        assert state["loop_iterations"] == original_iterations
        assert updated["loop_iterations"] == 5


class TestDataStructures:
    """Test supporting data structures."""
    
    def test_research_plan_structure(self):
        """Test ResearchPlan structure."""
        plan: ResearchPlan = {
            "required_properties": ["strength", "heat_resistance"],
            "suggested_elements": ["Ti", "Al", "V"],
            "thermodynamic_constraints": "stable below 1000K"
        }
        assert is_json_serializable(plan)
    
    def test_alloy_candidate_structure(self):
        """Test AlloyCandidate structure."""
        alloy: AlloyCandidate = {
            "matrix": ["Ti", "Al", "V"],
            "target_temp_K": 900
        }
        assert is_json_serializable(alloy)
    
    def test_thermo_result_structure(self):
        """Test ThermoResult structure."""
        result: ThermoResult = {
            "is_stable": True,
            "phases": ["alpha", "beta"],
            "temperature": 900
        }
        assert is_json_serializable(result)
    
    def test_fea_result_structure(self):
        """Test FEAResult structure."""
        result: FEAResult = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        assert is_json_serializable(result)


class TestValidAgents:
    """Test valid agent identifiers."""
    
    def test_valid_agents_constant(self):
        """Test that VALID_AGENTS contains expected values."""
        expected = {
            "discovery_lead",
            "research",
            "composition_loop",
            "simulation_lead",
            "fea",
            "complete"
        }
        assert VALID_AGENTS == expected
    
    def test_all_valid_agents_accepted(self):
        """Test that all valid agents are accepted in initialization."""
        for agent in VALID_AGENTS:
            state = initialize_session_state("Test", next_agent=agent)
            assert state["next_agent"] == agent



class TestPeriodicTable:
    """Test periodic table constant."""
    
    def test_periodic_table_contains_common_elements(self):
        """Test that periodic table contains common elements."""
        common_elements = ["H", "C", "N", "O", "Fe", "Ti", "Al", "Cu", "Ni"]
        for element in common_elements:
            assert element in PERIODIC_TABLE
    
    def test_periodic_table_size(self):
        """Test that periodic table has expected number of elements."""
        # 118 known elements as of 2024
        assert len(PERIODIC_TABLE) == 118


class TestValidateResearchPlan:
    """Test ResearchPlan validation."""
    
    def test_valid_research_plan(self):
        """Test validation of valid research plan."""
        plan = {
            "required_properties": ["strength", "heat_resistance"],
            "suggested_elements": ["Ti", "Al", "V"],
            "thermodynamic_constraints": "stable below 1000K"
        }
        is_valid, errors = validate_research_plan(plan)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_properties(self):
        """Test that missing required_properties is caught."""
        plan = {
            "suggested_elements": ["Ti", "Al"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("required_properties" in err for err in errors)
    
    def test_empty_required_properties(self):
        """Test that empty required_properties is caught."""
        plan = {
            "required_properties": [],
            "suggested_elements": ["Ti"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("cannot be empty" in err for err in errors)
    
    def test_invalid_required_properties_type(self):
        """Test that non-list required_properties is caught."""
        plan = {
            "required_properties": "strength",
            "suggested_elements": ["Ti"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("must be a list" in err for err in errors)
    
    def test_non_string_required_properties(self):
        """Test that non-string items in required_properties are caught."""
        plan = {
            "required_properties": ["strength", 123],
            "suggested_elements": ["Ti"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("must be strings" in err for err in errors)
    
    def test_missing_suggested_elements(self):
        """Test that missing suggested_elements is caught."""
        plan = {
            "required_properties": ["strength"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("suggested_elements" in err for err in errors)
    
    def test_invalid_element_symbol(self):
        """Test that invalid element symbols are caught."""
        plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti", "Xx", "Al"],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("Invalid element symbol: Xx" in err for err in errors)
    
    def test_non_string_element(self):
        """Test that non-string elements are caught."""
        plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti", 123],
            "thermodynamic_constraints": "stable"
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("must be a string" in err for err in errors)
    
    def test_missing_thermodynamic_constraints(self):
        """Test that missing thermodynamic_constraints is caught."""
        plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti"]
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("thermodynamic_constraints" in err for err in errors)
    
    def test_empty_thermodynamic_constraints(self):
        """Test that empty thermodynamic_constraints is caught."""
        plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti"],
            "thermodynamic_constraints": "   "
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("cannot be empty" in err for err in errors)
    
    def test_invalid_thermodynamic_constraints_type(self):
        """Test that non-string thermodynamic_constraints is caught."""
        plan = {
            "required_properties": ["strength"],
            "suggested_elements": ["Ti"],
            "thermodynamic_constraints": 123
        }
        is_valid, errors = validate_research_plan(plan)
        assert not is_valid
        assert any("must be a string" in err for err in errors)


class TestValidateAlloyCandidate:
    """Test AlloyCandidate validation."""
    
    def test_valid_alloy_candidate(self):
        """Test validation of valid alloy candidate."""
        candidate = {
            "matrix": ["Ti", "Al", "V"],
            "target_temp_K": 900
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert is_valid
        assert len(errors) == 0
    
    def test_valid_alloy_candidate_float_temp(self):
        """Test validation with float temperature."""
        candidate = {
            "matrix": ["Ti", "Al"],
            "target_temp_K": 900.5
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_matrix(self):
        """Test that missing matrix is caught."""
        candidate = {"target_temp_K": 900}
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("matrix" in err for err in errors)
    
    def test_empty_matrix(self):
        """Test that empty matrix is caught."""
        candidate = {
            "matrix": [],
            "target_temp_K": 900
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("cannot be empty" in err for err in errors)
    
    def test_invalid_matrix_type(self):
        """Test that non-list matrix is caught."""
        candidate = {
            "matrix": "Ti-Al",
            "target_temp_K": 900
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("must be a list" in err for err in errors)
    
    def test_invalid_element_in_matrix(self):
        """Test that invalid element symbols in matrix are caught."""
        candidate = {
            "matrix": ["Ti", "Zz", "Al"],
            "target_temp_K": 900
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("Invalid element symbol: Zz" in err for err in errors)
    
    def test_non_string_element_in_matrix(self):
        """Test that non-string elements in matrix are caught."""
        candidate = {
            "matrix": ["Ti", 22, "Al"],
            "target_temp_K": 900
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("must be a string" in err for err in errors)
    
    def test_missing_target_temp(self):
        """Test that missing target_temp_K is caught."""
        candidate = {"matrix": ["Ti", "Al"]}
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("target_temp_K" in err for err in errors)
    
    def test_negative_temperature(self):
        """Test that negative temperature is caught."""
        candidate = {
            "matrix": ["Ti", "Al"],
            "target_temp_K": -100
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_zero_temperature(self):
        """Test that zero temperature is caught."""
        candidate = {
            "matrix": ["Ti", "Al"],
            "target_temp_K": 0
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_invalid_temperature_type(self):
        """Test that non-numeric temperature is caught."""
        candidate = {
            "matrix": ["Ti", "Al"],
            "target_temp_K": "900"
        }
        is_valid, errors = validate_alloy_candidate(candidate)
        assert not is_valid
        assert any("must be a number" in err for err in errors)


class TestValidateThermoResult:
    """Test ThermoResult validation."""
    
    def test_valid_thermo_result(self):
        """Test validation of valid thermo result."""
        result = {
            "is_stable": True,
            "phases": ["alpha", "beta"],
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_valid_thermo_result_float_temp(self):
        """Test validation with float temperature."""
        result = {
            "is_stable": False,
            "phases": ["liquid"],
            "temperature": 1200.5
        }
        is_valid, errors = validate_thermo_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_is_stable(self):
        """Test that missing is_stable is caught."""
        result = {
            "phases": ["alpha"],
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("is_stable" in err for err in errors)
    
    def test_invalid_is_stable_type(self):
        """Test that non-boolean is_stable is caught."""
        result = {
            "is_stable": "yes",
            "phases": ["alpha"],
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be a boolean" in err for err in errors)
    
    def test_missing_phases(self):
        """Test that missing phases is caught."""
        result = {
            "is_stable": True,
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("phases" in err for err in errors)
    
    def test_invalid_phases_type(self):
        """Test that non-list phases is caught."""
        result = {
            "is_stable": True,
            "phases": "alpha",
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be a list" in err for err in errors)
    
    def test_non_string_phase(self):
        """Test that non-string phases are caught."""
        result = {
            "is_stable": True,
            "phases": ["alpha", 123],
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be strings" in err for err in errors)
    
    def test_empty_phases_allowed(self):
        """Test that empty phases list is allowed."""
        result = {
            "is_stable": False,
            "phases": [],
            "temperature": 900
        }
        is_valid, errors = validate_thermo_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_temperature(self):
        """Test that missing temperature is caught."""
        result = {
            "is_stable": True,
            "phases": ["alpha"]
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("temperature" in err for err in errors)
    
    def test_negative_temperature(self):
        """Test that negative temperature is caught."""
        result = {
            "is_stable": True,
            "phases": ["alpha"],
            "temperature": -100
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_zero_temperature(self):
        """Test that zero temperature is caught."""
        result = {
            "is_stable": True,
            "phases": ["alpha"],
            "temperature": 0
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_invalid_temperature_type(self):
        """Test that non-numeric temperature is caught."""
        result = {
            "is_stable": True,
            "phases": ["alpha"],
            "temperature": "900K"
        }
        is_valid, errors = validate_thermo_result(result)
        assert not is_valid
        assert any("must be a number" in err for err in errors)


class TestValidateFEAResult:
    """Test FEAResult validation."""
    
    def test_valid_fea_result_survived(self):
        """Test validation of valid FEA result (survived)."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_valid_fea_result_failed(self):
        """Test validation of valid FEA result (failed)."""
        result = {
            "survived": False,
            "failure_mode": "thermal_stress",
            "max_stress_mpa": 850.5,
            "max_temperature_k": 1100.3
        }
        is_valid, errors = validate_fea_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_zero_stress_allowed(self):
        """Test that zero stress is allowed."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 0.0,
            "max_temperature_k": 300.0
        }
        is_valid, errors = validate_fea_result(result)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_survived(self):
        """Test that missing survived is caught."""
        result = {
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("survived" in err for err in errors)
    
    def test_invalid_survived_type(self):
        """Test that non-boolean survived is caught."""
        result = {
            "survived": "yes",
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be a boolean" in err for err in errors)
    
    def test_missing_failure_mode(self):
        """Test that missing failure_mode is caught."""
        result = {
            "survived": True,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("failure_mode" in err for err in errors)
    
    def test_invalid_failure_mode_type(self):
        """Test that non-string/None failure_mode is caught."""
        result = {
            "survived": False,
            "failure_mode": 123,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be a string or None" in err for err in errors)
    
    def test_missing_max_stress(self):
        """Test that missing max_stress_mpa is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("max_stress_mpa" in err for err in errors)
    
    def test_negative_stress(self):
        """Test that negative stress is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": -100.0,
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be non-negative" in err for err in errors)
    
    def test_invalid_stress_type(self):
        """Test that non-numeric stress is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": "450",
            "max_temperature_k": 920.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be a number" in err for err in errors)
    
    def test_missing_max_temperature(self):
        """Test that missing max_temperature_k is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("max_temperature_k" in err for err in errors)
    
    def test_negative_temperature(self):
        """Test that negative temperature is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": -100.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_zero_temperature(self):
        """Test that zero temperature is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": 0.0
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be positive" in err for err in errors)
    
    def test_invalid_temperature_type(self):
        """Test that non-numeric temperature is caught."""
        result = {
            "survived": True,
            "failure_mode": None,
            "max_stress_mpa": 450.0,
            "max_temperature_k": "920K"
        }
        is_valid, errors = validate_fea_result(result)
        assert not is_valid
        assert any("must be a number" in err for err in errors)
