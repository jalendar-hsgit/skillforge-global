#!/usr/bin/env python3
"""
Test script for auth endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_signup():
    """Test signup endpoint"""
    print("\n=== Testing Signup ===")
    payload = {
        "email": "testuser@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/signup", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code == 200

def test_login():
    """Test login endpoint"""
    print("\n=== Testing Login ===")
    payload = {
        "email": "testuser@example.com",
        "password": "TestPassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code == 200

def test_me():
    """Test /me endpoint"""
    print("\n=== Testing /me endpoint ===")
    response = requests.get(f"{BASE_URL}/api/v1/auth/me")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code in [200, 401]

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health ===")
    response = requests.get(f"{BASE_URL}/healthz")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Starting auth tests...")
    
    # Test health first
    if not test_health():
        print("ERROR: Backend is not responding!")
        exit(1)
    
    print("\n✅ Backend is running")
    
    # Test signup
    if not test_signup():
        print("❌ Signup failed")
    else:
        print("✅ Signup succeeded")
    
    # Test login
    if not test_login():
        print("❌ Login failed")
    else:
        print("✅ Login succeeded")
    
    # Test /me
    if not test_me():
        print("❌ /me endpoint failed")
    else:
        print("✅ /me endpoint working")
    
    print("\n✅ All tests completed!")
