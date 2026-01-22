#!/usr/bin/env python3
"""Simple test to check if mentor-documents API is working"""

import requests
import json

API_BASE = "http://localhost:8001"

# Quick health check
print("Testing mentor-documents API...")

# Try to access the endpoint with a simple GET
try:
    response = requests.get(f"{API_BASE}/api/v1x/mentor-documents/my-documents", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.text else 'No content'}")
except Exception as e:
    print(f"Error: {e}")
