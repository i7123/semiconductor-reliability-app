#!/usr/bin/env python3
"""
Test cases for the Test Sample Size Calculator
Tests both backend calculations and frontend integration
"""

import requests
import json
import time
from typing import Dict, Any

class TestSampleSizeCalculatorTest:
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.calculator_id = "test_sample_size"
        
    def test_success_run_calculation(self):
        """Test success run calculation with zero failures"""
        print("Testing Success Run Calculation...")
        
        test_cases = [
            {
                "name": "95% reliability, 90% confidence",
                "inputs": {
                    "target_reliability": 0.95,
                    "confidence_level": "90",
                    "test_type": "success_run"
                },
                "expected_sample_size_range": (44, 46)  # Expected ~45 samples
            },
            {
                "name": "99% reliability, 95% confidence", 
                "inputs": {
                    "target_reliability": 0.99,
                    "confidence_level": "95",
                    "test_type": "success_run"
                },
                "expected_sample_size_range": (298, 302)  # Expected ~300 samples
            },
            {
                "name": "90% reliability, 80% confidence",
                "inputs": {
                    "target_reliability": 0.90,
                    "confidence_level": "80",
                    "test_type": "success_run"
                },
                "expected_sample_size_range": (15, 17)  # Expected ~16 samples
            }
        ]
        
        for test_case in test_cases:
            result = self.make_calculation_request(test_case["inputs"])
            if result:
                sample_size = result.get("required_sample_size", 0)
                expected_range = test_case["expected_sample_size_range"]
                
                if expected_range[0] <= sample_size <= expected_range[1]:
                    print(f"✓ {test_case['name']}: {sample_size} samples (within expected range)")
                else:
                    print(f"✗ {test_case['name']}: {sample_size} samples (expected {expected_range[0]}-{expected_range[1]})")
            else:
                print(f"✗ {test_case['name']}: API call failed")
    
    def test_time_terminated_calculation(self):
        """Test time-terminated calculation"""
        print("\nTesting Time-Terminated Calculation...")
        
        test_cases = [
            {
                "name": "1000 hour MTBF, 100 hour test duration",
                "inputs": {
                    "target_reliability": 0.95,
                    "confidence_level": "90",
                    "test_type": "time_terminated",
                    "test_duration": 100,
                    "target_mtbf": 1000,
                    "max_failures": 0
                },
                "expected_sample_size_range": (11, 13)  # Expected ~12 samples
            },
            {
                "name": "500 hour MTBF, 50 hour test duration, 1 failure allowed",
                "inputs": {
                    "target_reliability": 0.90,
                    "confidence_level": "95",
                    "test_type": "time_terminated",
                    "test_duration": 50,
                    "target_mtbf": 500,
                    "max_failures": 1
                },
                "expected_sample_size_range": (59, 61)  # Expected ~60 samples
            }
        ]
        
        for test_case in test_cases:
            result = self.make_calculation_request(test_case["inputs"])
            if result:
                sample_size = result.get("required_sample_size", 0)
                expected_range = test_case["expected_sample_size_range"]
                
                if expected_range[0] <= sample_size <= expected_range[1]:
                    print(f"✓ {test_case['name']}: {sample_size} samples (within expected range)")
                    print(f"  Total test time: {result.get('total_test_time', 0)} hours")
                else:
                    print(f"✗ {test_case['name']}: {sample_size} samples (expected {expected_range[0]}-{expected_range[1]})")
            else:
                print(f"✗ {test_case['name']}: API call failed")
    
    def test_failure_terminated_calculation(self):
        """Test failure-terminated calculation"""
        print("\nTesting Failure-Terminated Calculation...")
        
        test_cases = [
            {
                "name": "2000 hour MTBF, 2 failures allowed",
                "inputs": {
                    "target_reliability": 0.95,
                    "confidence_level": "90",
                    "test_type": "failure_terminated",
                    "target_mtbf": 2000,
                    "max_failures": 2
                },
                "expected_sample_size_range": (5, 7)  # Expected ~6 samples
            }
        ]
        
        for test_case in test_cases:
            result = self.make_calculation_request(test_case["inputs"])
            if result:
                sample_size = result.get("estimated_sample_size", 0)
                expected_range = test_case["expected_sample_size_range"]
                
                if expected_range[0] <= sample_size <= expected_range[1]:
                    print(f"✓ {test_case['name']}: {sample_size} samples (within expected range)")
                    print(f"  Expected test time: {result.get('expected_total_test_time', 0)} hours")
                else:
                    print(f"✗ {test_case['name']}: {sample_size} samples (expected {expected_range[0]}-{expected_range[1]})")
            else:
                print(f"✗ {test_case['name']}: API call failed")
    
    def test_input_validation(self):
        """Test input validation"""
        print("\nTesting Input Validation...")
        
        invalid_test_cases = [
            {
                "name": "Invalid reliability (> 1.0)",
                "inputs": {
                    "target_reliability": 1.5,
                    "confidence_level": "90",
                    "test_type": "success_run"
                },
                "should_fail": True
            },
            {
                "name": "Invalid reliability (< 0.1)",
                "inputs": {
                    "target_reliability": 0.05,
                    "confidence_level": "90",
                    "test_type": "success_run"
                },
                "should_fail": True
            },
            {
                "name": "Missing required test_duration for time_terminated",
                "inputs": {
                    "target_reliability": 0.95,
                    "confidence_level": "90",
                    "test_type": "time_terminated",
                    "target_mtbf": 1000
                },
                "should_fail": True
            }
        ]
        
        for test_case in invalid_test_cases:
            result = self.make_calculation_request(test_case["inputs"])
            if test_case["should_fail"]:
                if result is None:
                    print(f"✓ {test_case['name']}: Correctly rejected invalid input")
                else:
                    print(f"✗ {test_case['name']}: Should have failed but didn't")
            else:
                if result is not None:
                    print(f"✓ {test_case['name']}: Valid input accepted")
                else:
                    print(f"✗ {test_case['name']}: Valid input rejected")
    
    def test_example_endpoint(self):
        """Test the example endpoint"""
        print("\nTesting Example Endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/calculators/calculate/{self.calculator_id}/example")
            if response.status_code == 200:
                example_data = response.json()
                print("✓ Example endpoint works")
                print(f"  Example inputs: {example_data.get('example_inputs', {})}")
                
                # Test the example calculation
                if "example_inputs" in example_data:
                    result = self.make_calculation_request(example_data["example_inputs"])
                    if result:
                        print("✓ Example calculation works")
                    else:
                        print("✗ Example calculation failed")
            else:
                print(f"✗ Example endpoint failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Example endpoint error: {e}")
    
    def test_calculator_info(self):
        """Test calculator info endpoint"""
        print("\nTesting Calculator Info...")
        
        try:
            response = requests.get(f"{self.base_url}/calculators/{self.calculator_id}/info")
            if response.status_code == 200:
                info = response.json()
                print("✓ Calculator info endpoint works")
                print(f"  Name: {info.get('name', 'Unknown')}")
                print(f"  Input fields: {len(info.get('input_fields', []))}")
                
                # Verify required fields are present
                required_fields = ["target_reliability", "confidence_level", "test_type"]
                input_field_names = [field["name"] for field in info.get("input_fields", [])]
                
                all_present = all(field in input_field_names for field in required_fields)
                if all_present:
                    print("✓ All required input fields present")
                else:
                    print("✗ Missing required input fields")
            else:
                print(f"✗ Calculator info failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ Calculator info error: {e}")
    
    def make_calculation_request(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Make a calculation request and return the result"""
        try:
            response = requests.post(
                f"{self.base_url}/calculators/calculate/{self.calculator_id}",
                json={"inputs": inputs},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json().get("results", {})
            else:
                print(f"  API Error: HTTP {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"  Request error: {e}")
            return None
    
    def run_all_tests(self):
        """Run all test cases"""
        print("=" * 60)
        print("TEST SAMPLE SIZE CALCULATOR - FUNCTIONAL TESTS")
        print("=" * 60)
        
        # Test if API is accessible
        try:
            response = requests.get(f"{self.base_url}/calculators/")
            if response.status_code != 200:
                print("✗ API not accessible. Make sure the backend is running.")
                return
        except Exception as e:
            print(f"✗ Cannot connect to API: {e}")
            print("Make sure the backend is running on http://localhost:8000")
            return
        
        print("✓ API is accessible")
        
        # Run individual test suites
        self.test_calculator_info()
        self.test_example_endpoint()
        self.test_success_run_calculation()
        self.test_time_terminated_calculation()
        self.test_failure_terminated_calculation()
        self.test_input_validation()
        
        print("\n" + "=" * 60)
        print("TESTING COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    tester = TestSampleSizeCalculatorTest()
    tester.run_all_tests()