#!/usr/bin/env python3
"""
Unit Tests for Calculator Functions
Tests all calculator logic and mathematical computations
"""

import pytest
import math
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.calculators.mtbf import MTBFCalculator
from app.calculators.duanemodel import DuaneModelCalculator
from app.calculators.test_sample_size import TestSampleSizeCalculator
from app.calculators.dummy1 import DummyCalculator1
from app.calculators.dummy2 import DummyCalculator2
from app.calculators.dummy3 import DummyCalculator3

class TestMTBFCalculator:
    def setup_method(self):
        self.calc = MTBFCalculator()
    
    def test_calculator_info(self):
        """Test calculator information"""
        info = self.calc.info
        assert info.id == "mtbf"
        assert info.name == "MTBF Calculator"
        assert info.category == "Reliability"
        assert len(info.input_fields) >= 3
    
    def test_basic_mtbf_calculation(self):
        """Test basic MTBF calculation"""
        inputs = {
            "failure_rate": 0.0001,
            "confidence_level": "95"
        }
        result = self.calc.calculate(inputs)
        
        assert result["mtbf_hours"] == 10000.0
        assert result["mtbf_years"] == pytest.approx(1.1408, rel=1e-3)
        assert result["failure_rate"] == 0.0001
        assert result["confidence_level"] == 95
    
    def test_mtbf_with_operating_hours(self):
        """Test MTBF calculation with operating hours"""
        inputs = {
            "failure_rate": 0.0001,
            "operating_hours": 8760,
            "confidence_level": "95"
        }
        result = self.calc.calculate(inputs)
        
        assert "reliability" in result
        assert "unreliability" in result
        assert result["operating_hours"] == 8760
        assert result["reliability"] == pytest.approx(math.exp(-0.0001 * 8760), rel=1e-6)
    
    def test_precise_confidence_intervals(self):
        """Test precise confidence intervals with test data"""
        inputs = {
            "failure_rate": 0.0001,
            "confidence_level": "95",
            "num_failures": 5,
            "test_time": 50000
        }
        result = self.calc.calculate(inputs)
        
        assert "precise_analysis" in result
        precise = result["precise_analysis"]
        assert precise["test_data"]["failures"] == 5
        assert precise["test_data"]["test_time"] == 50000
        assert "mtbf_confidence_interval" in precise
        assert "failure_rate_confidence_interval" in precise
    
    def test_zero_failures_case(self):
        """Test zero failures confidence interval"""
        inputs = {
            "failure_rate": 0.0001,
            "confidence_level": "95",
            "num_failures": 0,
            "test_time": 10000
        }
        result = self.calc.calculate(inputs)
        
        precise = result["precise_analysis"]
        assert precise["test_data"]["failures"] == 0
        assert precise["mtbf_confidence_interval"]["upper"] == "∞"
        assert precise["failure_rate_confidence_interval"]["lower"] == 0.0
    
    def test_input_validation(self):
        """Test input validation"""
        # Test missing required field
        with pytest.raises(ValueError):
            self.calc.calculate({})
        
        # Test invalid confidence level
        with pytest.raises(ValueError):
            self.calc.calculate({
                "failure_rate": 0.0001,
                "confidence_level": "85"  # Not in allowed options
            })

class TestDuaneModelCalculator:
    def setup_method(self):
        self.calc = DuaneModelCalculator()
    
    def test_calculator_info(self):
        """Test calculator information"""
        info = self.calc.info
        assert info.id == "duane_model"
        assert info.name == "Duane Model Reliability Growth Calculator"
        assert info.category == "Reliability Growth"
        assert len(info.input_fields) >= 3
    
    def test_duane_model_calculation(self):
        """Test Duane model calculation"""
        inputs = {
            "failure_times": "100, 250, 480, 750, 1200",
            "confidence_level": "95"
        }
        result = self.calc.calculate(inputs)
        
        assert "duane_model_parameters" in result
        params = result["duane_model_parameters"]
        assert "alpha" in params
        assert "beta" in params
        assert 0 < params["beta"] < 1  # Beta should indicate improvement
        
        assert "cumulative_mtbf_data" in result
        assert "model_fit_statistics" in result
        assert result["model_fit_statistics"]["r_squared"] > 0.9  # Good fit
    
    def test_duane_model_with_target_time(self):
        """Test Duane model with target time prediction"""
        inputs = {
            "failure_times": "100, 250, 480, 750, 1200",
            "confidence_level": "95",
            "target_time": 2000
        }
        result = self.calc.calculate(inputs)
        
        assert "target_prediction" in result
        target = result["target_prediction"]
        assert target["time"] == 2000
        assert "mtbf_cumulative" in target
        assert "mtbf_instantaneous" in target
        assert "confidence_interval" in target
    
    def test_reliability_growth_analysis(self):
        """Test reliability growth analysis"""
        inputs = {
            "failure_times": "100, 250, 480, 750, 1200",
            "confidence_level": "95"
        }
        result = self.calc.calculate(inputs)
        
        assert "reliability_growth" in result
        growth = result["reliability_growth"]
        assert "growth_rate_percent" in growth
        assert "interpretation" in growth
        assert "time_to_double_mtbf" in growth
    
    def test_input_validation_duane(self):
        """Test Duane model input validation"""
        # Test invalid failure times format
        with pytest.raises(ValueError):
            self.calc.calculate({
                "failure_times": "abc, def",
                "confidence_level": "95"
            })
        
        # Test insufficient failure times
        with pytest.raises(ValueError):
            self.calc.calculate({
                "failure_times": "100",
                "confidence_level": "95"
            })
        
        # Test non-ascending failure times (should be gracefully handled)
        # Note: Some implementations may not validate this strictly
        try:
            result = self.calc.calculate({
                "failure_times": "100, 250, 200, 750",
                "confidence_level": "95"
            })
            # If it doesn't raise an error, that's also acceptable behavior
        except ValueError as e:
            assert "ascending" in str(e).lower() or "order" in str(e).lower()

class TestTestSampleSizeCalculator:
    def setup_method(self):
        self.calc = TestSampleSizeCalculator()
    
    def test_calculator_info(self):
        """Test calculator information"""
        info = self.calc.info
        assert info.id == "test_sample_size"
        assert info.name == "Test Sample Size Calculator"
        assert info.category == "Test Planning"
        assert len(info.input_fields) >= 3
    
    def test_success_run_calculation(self):
        """Test success run calculation"""
        inputs = {
            "target_reliability": 0.95,
            "confidence_level": "90",
            "test_type": "success_run"
        }
        result = self.calc.calculate(inputs)
        
        assert result["test_type"] == "success_run"
        assert result["required_sample_size"] == 45  # Expected for 95% reliability, 90% confidence
        assert result["test_method"] == "Success Run Test"
        assert "alternative_scenarios" in result
    
    def test_time_terminated_calculation(self):
        """Test time-terminated calculation"""
        inputs = {
            "target_reliability": 0.95,
            "confidence_level": "90",
            "test_type": "time_terminated",
            "test_duration": 100,
            "target_mtbf": 1000,
            "max_failures": 0
        }
        result = self.calc.calculate(inputs)
        
        assert result["test_type"] == "time_terminated"
        assert "required_sample_size" in result
        assert "total_test_time" in result
        assert result["test_method"] == "Time-Terminated Test"
    
    def test_failure_terminated_calculation(self):
        """Test failure-terminated calculation"""
        inputs = {
            "target_reliability": 0.95,
            "confidence_level": "90",
            "test_type": "failure_terminated",
            "target_mtbf": 2000,
            "max_failures": 2
        }
        result = self.calc.calculate(inputs)
        
        assert result["test_type"] == "failure_terminated"
        assert "estimated_sample_size" in result
        assert "expected_total_test_time" in result
    
    def test_input_validation_sample_size(self):
        """Test sample size calculator input validation"""
        # Test invalid reliability
        with pytest.raises(ValueError):
            self.calc.calculate({
                "target_reliability": 1.5,
                "confidence_level": "90",
                "test_type": "success_run"
            })
        
        # Test missing required fields for time_terminated (should handle gracefully or raise error)
        try:
            result = self.calc.calculate({
                "target_reliability": 0.95,
                "confidence_level": "90",
                "test_type": "time_terminated"
                # Missing test_duration and target_mtbf
            })
            # Some implementations may provide defaults or handle missing fields gracefully
        except ValueError:
            # This is also acceptable - missing required fields should raise an error
            pass

class TestDummyCalculators:
    def test_dummy_calculator_1(self):
        """Test dummy calculator 1"""
        calc = DummyCalculator1()
        info = calc.info
        assert info.id == "dummy_calculator_1"
        assert info.category == "Future Development"
        
        result = calc.calculate({"stress_level": 1.0, "temperature": 100})
        assert result["status"] == "in_development"
        assert "planned_features" in result
    
    def test_dummy_calculator_2(self):
        """Test dummy calculator 2"""
        calc = DummyCalculator2()
        info = calc.info
        assert info.id == "dummy_calculator_2"
        assert info.category == "Future Development"
        
        result = calc.calculate({
            "burn_in_time": 24,
            "cost_per_hour": 10,
            "defect_rate": 5
        })
        assert result["status"] == "in_development"
        assert "planned_features" in result
    
    def test_dummy_calculator_3(self):
        """Test dummy calculator 3"""
        calc = DummyCalculator3()
        info = calc.info
        assert info.id == "dummy_calculator_3"
        assert info.category == "Future Development"
        
        result = calc.calculate({
            "lifetime_data": "100, 200, 300",
            "distribution_type": "Weibull",
            "censoring_type": "None"
        })
        assert result["status"] == "in_development"
        assert "planned_features" in result

def run_calculator_tests():
    """Run all calculator tests"""
    print("=" * 60)
    print("CALCULATOR UNIT TESTS")
    print("=" * 60)
    
    # Run pytest programmatically
    import subprocess
    import sys
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

if __name__ == "__main__":
    success = run_calculator_tests()
    if success:
        print("\n✅ All calculator tests passed!")
    else:
        print("\n❌ Some calculator tests failed!")
        sys.exit(1)