#!/usr/bin/env python3
"""
API Integration Tests
Tests all API endpoints and their functionality
"""

import pytest
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class TestAPIEndpoints:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = BASE_URL
        self.api_url = f"{BASE_URL}/api"
        
        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("Backend server not running")
        except requests.exceptions.RequestException:
            pytest.skip("Backend server not accessible")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(BASE_URL)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_list_calculators(self):
        """Test listing all calculators"""
        response = requests.get(f"{self.api_url}/calculators/")
        assert response.status_code == 200
        calculators = response.json()
        
        assert isinstance(calculators, list)
        assert len(calculators) >= 6  # 3 working + 3 dummy
        
        # Check required fields for each calculator
        for calc in calculators:
            assert "id" in calc
            assert "name" in calc
            assert "description" in calc
            assert "category" in calc
            assert "input_fields" in calc
    
    def test_calculator_info_endpoints(self):
        """Test individual calculator info endpoints"""
        # Get list of calculators first
        response = requests.get(f"{self.api_url}/calculators/")
        calculators = response.json()
        
        for calc in calculators:
            calc_id = calc["id"]
            response = requests.get(f"{self.api_url}/calculators/{calc_id}/info")
            assert response.status_code == 200
            
            info = response.json()
            assert info["id"] == calc_id
            assert "input_fields" in info
    
    def test_calculator_examples(self):
        """Test calculator example endpoints"""
        calc_ids = ["mtbf", "duane_model", "test_sample_size"]
        
        for calc_id in calc_ids:
            response = requests.get(f"{self.api_url}/calculators/calculate/{calc_id}/example")
            assert response.status_code == 200
            
            example = response.json()
            assert "calculator_id" in example
            assert "example_inputs" in example
            assert "example_results" in example
            assert example["calculator_id"] == calc_id
    
    def test_mtbf_calculation(self):
        """Test MTBF calculator API"""
        calc_data = {
            "inputs": {
                "failure_rate": 0.0001,
                "confidence_level": "95"
            }
        }
        
        response = requests.post(f"{self.api_url}/calculators/calculate/mtbf", json=calc_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["calculator_id"] == "mtbf"
        assert "results" in result
        
        results = result["results"]
        assert results["mtbf_hours"] == 10000.0
        assert results["failure_rate"] == 0.0001
    
    def test_duane_model_calculation(self):
        """Test Duane Model calculator API"""
        calc_data = {
            "inputs": {
                "failure_times": "100, 250, 480, 750, 1200",
                "confidence_level": "95"
            }
        }
        
        response = requests.post(f"{self.api_url}/calculators/calculate/duane_model", json=calc_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["calculator_id"] == "duane_model"
        
        results = result["results"]
        assert "duane_model_parameters" in results
        assert "reliability_growth" in results
    
    def test_test_sample_size_calculation(self):
        """Test Sample Size calculator API"""
        calc_data = {
            "inputs": {
                "target_reliability": 0.95,
                "confidence_level": "90",
                "test_type": "success_run"
            }
        }
        
        response = requests.post(f"{self.api_url}/calculators/calculate/test_sample_size", json=calc_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["calculator_id"] == "test_sample_size"
        
        results = result["results"]
        assert results["required_sample_size"] == 45
        assert results["test_type"] == "success_run"
    
    def test_dummy_calculator(self):
        """Test dummy calculator API"""
        calc_data = {
            "inputs": {
                "stress_level": 1.5,
                "temperature": 125
            }
        }
        
        response = requests.post(f"{self.api_url}/calculators/calculate/dummy_calculator_1", json=calc_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert result["results"]["status"] == "in_development"
    
    def test_invalid_calculator_id(self):
        """Test invalid calculator ID"""
        response = requests.get(f"{self.api_url}/calculators/nonexistent/info")
        assert response.status_code == 404
    
    def test_invalid_calculation_input(self):
        """Test invalid calculation input"""
        calc_data = {
            "inputs": {
                "invalid_field": "invalid_value"
            }
        }
        
        response = requests.post(f"{self.api_url}/calculators/calculate/mtbf", json=calc_data)
        assert response.status_code == 400

class TestAuthenticationAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.api_url = f"{BASE_URL}/api"
        self.test_email = f"test_{int(time.time())}@example.com"
        self.test_password = "testpass123"
    
    def test_user_registration(self):
        """Test user registration"""
        reg_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/register", json=reg_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_user_login(self):
        """Test user login"""
        # Register user first
        reg_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        requests.post(f"{self.api_url}/auth/register", json=reg_data)
        
        # Now test login
        login_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
    
    def test_usage_status_anonymous(self):
        """Test usage status for anonymous user"""
        response = requests.get(f"{self.api_url}/auth/usage")
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_usage" in data
        assert "daily_limit" in data
        assert "is_premium" in data
        assert data["is_premium"] is False
        assert data["daily_limit"] == 10
    
    def test_usage_status_authenticated(self):
        """Test usage status for authenticated user"""
        # Register and get token
        reg_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = requests.post(f"{self.api_url}/auth/register", json=reg_data)
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.api_url}/auth/usage", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "daily_usage" in data
        assert "daily_limit" in data
        assert "is_premium" in data
    
    def test_premium_upgrade(self):
        """Test premium upgrade"""
        # Register and get token
        reg_data = {
            "email": self.test_email,
            "password": self.test_password
        }
        response = requests.post(f"{self.api_url}/auth/register", json=reg_data)
        token = response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{self.api_url}/auth/upgrade", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert data["user"]["is_premium"] is True
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{self.api_url}/auth/login", json=login_data)
        assert response.status_code == 401

def run_api_tests():
    """Run all API tests"""
    print("=" * 60)
    print("API INTEGRATION TESTS")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server not running")
            return False
    except requests.exceptions.RequestException:
        print("❌ Backend server not accessible")
        return False
    
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
    success = run_api_tests()
    if success:
        print("\n✅ All API tests passed!")
    else:
        print("\n❌ Some API tests failed!")
        sys.exit(1)