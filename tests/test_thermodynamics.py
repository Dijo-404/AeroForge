# tests/test_thermodynamics.py
"""
Unit tests for thermodynamics module - calculate_phase_equilibrium function.
Tests Requirements: 4.1, 4.2, 4.3, 4.7, 19.1, 19.3
"""
import pytest
import json
import os
from src.tools.thermodynamics import calculate_phase_equilibrium


class TestCalculatePhaseEquilibrium:
    """Test calculate_phase_equilibrium function."""
    
    def test_valid_single_element(self):
        """Test equilibrium calculation with single element."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            pressure=101325.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        assert "elements" in result
        assert result["elements"] == ["Ti"]
        assert "temperature_K" in result
        assert result["temperature_K"] == 900.0
        assert "pressure_Pa" in result
        assert result["pressure_Pa"] == 101325.0
        assert "stable_phases" in result
        assert isinstance(result["stable_phases"], list)
        assert "is_stable" in result
        assert isinstance(result["is_stable"], bool)
    
    def test_valid_binary_alloy(self):
        """Test equilibrium calculation with binary alloy."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=900.0,
            pressure=101325.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        assert result["elements"] == ["Ti", "Al"]
        assert result["temperature_K"] == 900.0
        assert "stable_phases" in result
        assert isinstance(result["stable_phases"], list)
    
    def test_valid_ternary_alloy(self):
        """Test equilibrium calculation with ternary alloy."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al", "V"],
            temperature=900.0,
            pressure=101325.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        assert result["elements"] == ["Ti", "Al", "V"]
        assert result["temperature_K"] == 900.0
        assert "stable_phases" in result
        assert len(result["stable_phases"]) > 0
    
    def test_default_pressure(self):
        """Test that default pressure is 1 atm (101325 Pa)."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["pressure_Pa"] == 101325.0
    
    def test_custom_pressure(self):
        """Test equilibrium calculation with custom pressure."""
        custom_pressure = 200000.0
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=900.0,
            pressure=custom_pressure,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["pressure_Pa"] == custom_pressure
    
    def test_low_temperature(self):
        """Test equilibrium at low temperature."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=300.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["temperature_K"] == 300.0
        assert "stable_phases" in result
    
    def test_high_temperature(self):
        """Test equilibrium at high temperature."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=1500.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["temperature_K"] == 1500.0
        assert "stable_phases" in result
    
    def test_phase_fractions_format(self):
        """Test that phase fractions are properly formatted."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al", "V"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        for phase in result["stable_phases"]:
            assert "phase" in phase
            assert "fraction" in phase
            assert isinstance(phase["phase"], str)
            assert isinstance(phase["fraction"], (int, float))
            assert 0.0 <= phase["fraction"] <= 1.0
    
    def test_missing_tdb_file(self):
        """Test error handling when TDB file is missing."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=900.0,
            tdb_path="nonexistent.tdb"
        )
        
        result = json.loads(result_str)
        
        assert result["is_stable"] is False
        assert "error" in result
        assert "stable_phases" in result
        assert result["stable_phases"] == []
    
    def test_invalid_tdb_path(self):
        """Test error handling with invalid TDB path."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            tdb_path="/invalid/path/to/file.tdb"
        )
        
        result = json.loads(result_str)
        
        assert result["is_stable"] is False
        assert "error" in result
    
    def test_json_serializable_output(self):
        """Test that output is valid JSON."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        # Should not raise exception
        result = json.loads(result_str)
        
        # Should be able to serialize again
        json.dumps(result)
    
    def test_case_insensitive_elements(self):
        """Test that element symbols are handled case-insensitively."""
        result_str = calculate_phase_equilibrium(
            elements=["ti", "al", "v"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # Should still work (elements converted to uppercase internally)
        assert "stable_phases" in result
        assert isinstance(result["stable_phases"], list)
    
    def test_return_type_is_string(self):
        """Test that function returns a string."""
        result = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        assert isinstance(result, str)
    
    def test_stable_phases_not_empty_for_valid_calculation(self):
        """Test that stable phases are returned for valid calculations."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al", "V"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # For a valid calculation with mock.tdb, we should get phases
        if result["is_stable"]:
            assert len(result["stable_phases"]) > 0


class TestPhaseEquilibriumEdgeCases:
    """Test edge cases for phase equilibrium calculations."""
    
    def test_very_low_temperature(self):
        """Test equilibrium at very low temperature (near absolute zero)."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=1.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert "temperature_K" in result
        assert result["temperature_K"] == 1.0
    
    def test_very_high_temperature(self):
        """Test equilibrium at very high temperature."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=5000.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert "temperature_K" in result
        assert result["temperature_K"] == 5000.0
    
    def test_zero_pressure(self):
        """Test equilibrium at zero pressure (vacuum)."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            pressure=0.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["pressure_Pa"] == 0.0
    
    def test_high_pressure(self):
        """Test equilibrium at high pressure."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=900.0,
            pressure=1e9,  # 1 GPa
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        assert result["pressure_Pa"] == 1e9


class TestPhaseEquilibriumIntegration:
    """Integration tests with actual mock.tdb file."""
    
    def test_mock_tdb_exists(self):
        """Verify that mock.tdb file exists."""
        assert os.path.exists("mock.tdb"), "mock.tdb file should exist in project root"
    
    def test_realistic_aerospace_alloy(self):
        """Test realistic aerospace alloy composition (Ti-6Al-4V analog)."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al", "V"],
            temperature=900.0,
            pressure=101325.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        assert result["elements"] == ["Ti", "Al", "V"]
        assert result["temperature_K"] == 900.0
        assert "stable_phases" in result
        
        # Should have at least one stable phase
        if result["is_stable"]:
            assert len(result["stable_phases"]) > 0
            
            # Verify phase fractions sum to approximately 1.0
            total_fraction = sum(p["fraction"] for p in result["stable_phases"])
            assert 0.9 <= total_fraction <= 1.1  # Allow small numerical errors
    
    def test_all_elements_in_mock_tdb(self):
        """Test that all elements in mock.tdb can be used."""
        elements_in_tdb = ["Al", "Ti", "V"]
        
        for element in elements_in_tdb:
            result_str = calculate_phase_equilibrium(
                elements=[element],
                temperature=900.0,
                tdb_path="mock.tdb"
            )
            
            result = json.loads(result_str)
            assert "stable_phases" in result
            assert isinstance(result["stable_phases"], list)


class TestPhaseEquilibriumErrorHandling:
    """Test error handling and edge cases for phase equilibrium calculations."""
    
    def test_equilibrium_calculation_failure_handling(self):
        """Test that equilibrium calculation failures are handled gracefully."""
        # Use an element not in the TDB to trigger calculation failure
        result_str = calculate_phase_equilibrium(
            elements=["Fe"],  # Not in mock.tdb
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # Should return error structure
        assert result["is_stable"] is False
        assert "error" in result
        assert result["stable_phases"] == []
    
    def test_empty_phases_result(self):
        """Test handling when no stable phases are found."""
        # This tests the is_stable = False path when stable_phases is empty
        # Using extreme conditions that might not produce stable phases
        result_str = calculate_phase_equilibrium(
            elements=["Ti"],
            temperature=10000.0,  # Extremely high temperature
            pressure=0.0,  # Vacuum
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # Should have valid structure even if no phases
        assert "is_stable" in result
        assert "stable_phases" in result
        assert isinstance(result["stable_phases"], list)
    
    def test_liquid_phase_stability_assessment(self):
        """Test that liquid phases are correctly assessed for stability."""
        # At very high temperature, we might get liquid phase
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al"],
            temperature=2000.0,  # High temperature likely to produce liquid
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # If we have only liquid phase, is_stable should be False
        if result["stable_phases"]:
            has_only_liquid = all(p["phase"] == "LIQUID" for p in result["stable_phases"])
            if has_only_liquid:
                assert result["is_stable"] is False
    
    def test_multiple_solid_phases_stability(self):
        """Test stability assessment with multiple solid phases."""
        result_str = calculate_phase_equilibrium(
            elements=["Ti", "Al", "V"],
            temperature=900.0,
            tdb_path="mock.tdb"
        )
        
        result = json.loads(result_str)
        
        # If we have solid phases (BCC, HCP), is_stable should be True
        if result["stable_phases"]:
            solid_phases = [p for p in result["stable_phases"] 
                          if p["phase"] not in ["LIQUID"]]
            if solid_phases:
                assert result["is_stable"] is True
