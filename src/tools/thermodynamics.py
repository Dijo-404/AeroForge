# src/tools/thermodynamics.py
import json

def calculate_phase_equilibrium(elements: list[str], temperature: float, pressure: float = 101325.0) -> str:
    """
    Mock wrapper for PyCALPHAD to calculate thermodynamic phase equilibria.
    In a real implementation, this would load TDB files and compute Gibbs energy minimization.
    
    Args:
        elements: List of element symbols (e.g. ['Ti', 'Al', 'V'])
        temperature: Temperature in Kelvin.
        pressure: Pressure in Pascals (default 1atm).
        
    Returns:
        JSON string containing the stable phases and their calculated fractions.
    """
    # Mock behavior simulating pycalphad equilibrium return values
    mock_result = {
        "elements": elements,
        "temperature_K": temperature,
        "pressure_Pa": pressure,
        "stable_phases": [],
        "is_stable": False
    }

    if "Ti" in elements and "Al" in elements and temperature < 1200:
        mock_result["stable_phases"] = [
            {"phase": "ALPHA", "fraction": 0.85, "composition": {"Ti": 0.9, "Al": 0.1}},
            {"phase": "BETA", "fraction": 0.15, "composition": {"Ti": 0.8, "V": 0.2}}
        ]
        mock_result["is_stable"] = True
    elif temperature >= 1200:
         mock_result["stable_phases"] = [
            {"phase": "LIQUID", "fraction": 1.0, "composition": {el: 1.0/len(elements) for el in elements}}
         ]
         mock_result["is_stable"] = False # Melted
         
    return json.dumps(mock_result)
