#!/usr/bin/env python3
"""
Authorization System Test Script
Tests all authentication and authorization features
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_authorization_system():
    print("=" * 60)
    print("AUTHORIZATION SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Anonymous usage
    print("\n1. Testing Anonymous Usage:")
    response = requests.get(f"{BASE_URL}/auth/usage")
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Anonymous usage: {usage['daily_usage']}/{usage['daily_limit']} (Free: {not usage['is_premium']})")
    else:
        print("✗ Anonymous usage failed")
    
    # Test 2: User Registration
    print("\n2. Testing User Registration:")
    test_email = f"test_{int(time.time())}@example.com"
    reg_data = {"email": test_email, "password": "testpass123"}
    
    response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"✓ User registered successfully")
        print(f"  Token type: {token_data['token_type']}")
    else:
        print(f"✗ Registration failed: {response.text}")
        return
    
    # Test 3: User Login
    print("\n3. Testing User Login:")
    login_data = {"email": test_email, "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print("✓ User login successful")
    else:
        print(f"✗ Login failed: {response.text}")
        return
    
    # Test 4: Authenticated Usage Status
    print("\n4. Testing Authenticated Usage:")
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/auth/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Authenticated usage: {usage['daily_usage']}/{usage['daily_limit']}")
        print(f"  Premium: {usage['is_premium']}")
        print(f"  Remaining: {usage['usage_remaining']}")
    else:
        print(f"✗ Authenticated usage failed: {response.text}")
    
    # Test 5: Calculation with Authentication
    print("\n5. Testing Authenticated Calculation:")
    calc_data = {"inputs": {"failure_rate": 0.0001, "confidence_level": "95"}}
    response = requests.post(f"{BASE_URL}/calculators/calculate/mtbf", 
                           json=calc_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Calculation successful: {result['success']}")
        print(f"  MTBF: {result['results']['mtbf_hours']} hours")
    else:
        print(f"✗ Calculation failed: {response.text}")
    
    # Test 6: Usage Count After Calculation
    print("\n6. Testing Usage Tracking:")
    response = requests.get(f"{BASE_URL}/auth/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Usage tracked: {usage['daily_usage']}/{usage['daily_limit']}")
        print(f"  Remaining: {usage['usage_remaining']}")
    else:
        print(f"✗ Usage tracking failed: {response.text}")
    
    # Test 7: Premium Upgrade
    print("\n7. Testing Premium Upgrade:")
    response = requests.post(f"{BASE_URL}/auth/upgrade", headers=headers)
    if response.status_code == 200:
        upgrade_result = response.json()
        print("✓ Premium upgrade successful")
        print(f"  Message: {upgrade_result['message']}")
        print(f"  Premium status: {upgrade_result['user']['is_premium']}")
    else:
        print(f"✗ Premium upgrade failed: {response.text}")
    
    # Test 8: Premium Usage Status
    print("\n8. Testing Premium Usage Status:")
    response = requests.get(f"{BASE_URL}/auth/usage", headers=headers)
    if response.status_code == 200:
        usage = response.json()
        print(f"✓ Premium usage: {usage['daily_usage']}/{usage['daily_limit']}")
        print(f"  Premium: {usage['is_premium']}")
        print(f"  Remaining: {usage['usage_remaining']}")
    else:
        print(f"✗ Premium usage failed: {response.text}")
    
    # Test 9: Rate Limiting (Anonymous)
    print("\n9. Testing Rate Limiting:")
    calc_count = 0
    for i in range(12):  # Try to exceed limit
        response = requests.post(f"{BASE_URL}/calculators/calculate/mtbf", json=calc_data)
        if response.status_code == 200:
            calc_count += 1
        elif response.status_code == 429:
            print(f"✓ Rate limiting triggered after {calc_count} calculations")
            rate_limit_data = response.json()
            print(f"  Error: {rate_limit_data['detail']['error']}")
            break
    
    print("\n" + "=" * 60)
    print("AUTHORIZATION TESTS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_authorization_system()
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")