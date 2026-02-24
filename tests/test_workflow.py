# tests/test_workflow.py
import pytest
import json
from src.tools.thermodynamics import calculate_phase_equilibrium
from src.tools.fea_simulation import run_fea_analysis
from src.main_workflow import execute_pipeline

def test_pycalphad_mock():
    result = calculate_phase_equilibrium(["Ti", "Al", "V"], 1000)
    data = json.loads(result)
    assert data["is_stable"] is True
    assert "stable_phases" in data

def test_pyansys_mock():
    result = run_fea_analysis("turbine", 1500.0, 650.0)
    data = json.loads(result)
    assert "survived" in data
    assert "max_displacement_mm" in data

def test_full_pipeline():
    session_state = execute_pipeline("Design a heat resistant alloy.")
    # Check that it traversed all steps and serialized properly
    assert session_state["next_agent"] == "composition_loop" # Updated state transition
    assert "final_formulation" in session_state # Loop passed
    assert "simulation_results" in session_state # Sim passed
    assert session_state["simulation_results"]["survived"] is True # 975 MPa < 1000 limit
