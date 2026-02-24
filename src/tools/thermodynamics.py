# src/tools/thermodynamics.py
import json
import logging

import numpy as np
from pycalphad import Database, equilibrium
from pycalphad import variables as v

logger = logging.getLogger("AeroForge Thermodynamics")

def calculate_phase_equilibrium(elements: list[str], temperature: float, pressure: float = 101325.0, tdb_path: str = "mock.tdb") -> str:
    """
    Calculates thermodynamic phase equilibria using PyCALPHAD.

    Args:
        elements: List of element symbols (e.g., ["Ti", "Al", "V"])
        temperature: Target temperature in Kelvin
        pressure: Pressure in Pascals (default: 1 atm)
        tdb_path: Path to thermodynamic database file

    Returns:
        JSON string with stability assessment and phase fractions

    Raises:
        No exceptions raised - errors are returned in JSON format
    """
    logger.info(f"Running Real PyCALPHAD equilibrium for {elements} at {temperature}K")
    try:
        dbf = Database(tdb_path)
    except Exception as e:
        logger.error(f"Failed to load thermodynamic database {tdb_path}: {e}")
        return json.dumps({"is_stable": False, "error": str(e), "stable_phases": []})

    # PyCALPHAD requires elements + 'VA' (vacancies) typically
    comps = [el.upper() for el in elements] + ['VA']

    # We will simulate a simple equimolar test across the provided elements
    conditions = {v.T: temperature, v.P: pressure}

    # For a multi-component alloy, we need to set N-1 mole fractions.
    fraction = 1.0 / len(comps[:-1])
    for el in comps[:-2]: # exclude VA and the last element
        conditions[v.X(el.upper())] = fraction

    try:
        # Run the equilibrium calculation
        eq = equilibrium(dbf, comps, dbf.phases.keys(), conditions)

        # Extract the stable phases (where phase fraction NP > 0)
        # Squeeze out the multidimensional xarray parameters for a single temp/pressure point
        phases = eq.Phase.squeeze().values
        fractions = eq.NP.squeeze().values

        stable_phases = []
        is_stable = False

        # Determine if the matrix is "stable" based on business logic
        # e.g., We don't want liquid, or we want a specific solid solution
        for phase_name, frac in zip(phases, fractions):
            # Check for valid phase name and fraction (not NaN, not empty, positive)
            if phase_name != '' and not np.isnan(frac) and frac > 0.0:
                stable_phases.append({"phase": str(phase_name), "fraction": float(frac)})

        # Determine stability based on presence of stable phases
        # For aerospace alloys, we typically want solid solutions (BCC, HCP) not liquid
        if stable_phases:
            # Check if we have desirable solid phases
            solid_phases = [p for p in stable_phases if p["phase"] not in ["LIQUID"]]
            is_stable = len(solid_phases) > 0
        else:
            # If no phases found, the TDB might be incomplete or calculation failed
            # For mock TDB validation, we still return a valid structure
            is_stable = False

        result = {
            "elements": elements,
            "temperature_K": temperature,
            "pressure_Pa": pressure,
            "stable_phases": stable_phases,
            "is_stable": is_stable
        }
        return json.dumps(result)

    except Exception as e:
        logger.error(f"Equilibrium calculation failed: {e}")
        return json.dumps({"is_stable": False, "error": str(e), "stable_phases": []})


