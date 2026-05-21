#!/usr/bin/env python
"""Test all resume and session endpoints"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1x"

def test_healthz():
    try:
        resp = requests.get(f"{BASE_URL}/healthz")
        print(f"✓ Health check: {resp.status_code}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_session_endpoints():
    """Test session endpoints"""
    print("\n=== Testing Session Endpoints ===")
    
    # Test /session/me (no auth, should fail)
    try:
        resp = requests.get(f"{API_BASE}/session/me")
        print(f"Session /me (no auth): {resp.status_code}")
    except Exception as e:
        print(f"Session /me error: {e}")
    
    # Test /session/resumes (no auth, should fail)
    try:
        resp = requests.get(f"{API_BASE}/session/resumes")
        print(f"Session /resumes (no auth): {resp.status_code}")
    except Exception as e:
        print(f"Session /resumes error: {e}")

def test_resumes_endpoints():
    """Test v1x resumes endpoints"""
    print("\n=== Testing Resumes Endpoints ===")
    
    # Test GET /resumes
    try:
        resp = requests.get(f"{API_BASE}/resumes")
        print(f"GET /resumes: {resp.status_code}")
    except Exception as e:
        print(f"GET /resumes error: {e}")

if __name__ == "__main__":
    print(f"Testing SkillForge Backend API")
    print(f"Timestamp: {datetime.now()}")
    print(f"API Base: {API_BASE}")
    
    # Test health
    if test_healthz():
        print("\nBackend is responding!")
        test_session_endpoints()
        test_resumes_endpoints()
    else:
        print("\n❌ Backend is not responding at", BASE_URL)
