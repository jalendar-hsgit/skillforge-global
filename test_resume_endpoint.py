#!/usr/bin/env python
"""Quick test of resume creation"""
import requests
import json

# Test data
test_resume = {
    "title": "Test Resume",
    "template_id": "modern"
}

# Try to create a resume (will fail without auth but shows if endpoint works)
response = requests.post(
    "http://localhost:8001/api/v1x/resumes",
    json=test_resume,
    timeout=5
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
