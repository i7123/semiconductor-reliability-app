#!/usr/bin/env python3
"""
Direct test of Test Sample Size Calculator without middleware
"""

import sys
sys.path.append('/Users/james/semiconductor-reliability-app/backend')

from app.calculators.test_sample_size import TestSampleSizeCalculator
from app.calculators.routes import CalculationRequest

def test_direct():
    print("Testing Test Sample Size Calculator directly...")
    
    calc = TestSampleSizeCalculator()
    
    # Test 1: Success run
    print("\nTest 1: Success Run")
    inputs = {
        "target_reliability": 0.95,
        "confidence_level": "90",
        "test_type": "success_run"
    }
    try:
        result = calc.calculate(inputs)
        print(f"✓ Success: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Time terminated
    print("\nTest 2: Time Terminated")
    inputs = {
        "target_reliability": 0.95,
        "confidence_level": "90", 
        "test_type": "time_terminated",
        "test_duration": 100.0,
        "target_mtbf": 1000.0,
        "max_failures": 0
    }
    try:
        result = calc.calculate(inputs)
        print(f"✓ Success: {result}")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct()