#!/usr/bin/env python3
"""Test API endpoints directly"""
import sys
sys.path.insert(0, '/app')

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

endpoints = [
    ("/healthz", "Health"),
    ("/api/v1/courses", "CoursesV1"),  
    ("/api/v1x/mentors", "MentorsV1X"),
    ("/api/v1/users", "UsersV1"),
]

print("TESTING ENDPOINTS:")
for path, name in endpoints:
    try:
        resp = client.get(path)
        data = resp.json()
        if isinstance(data, list):
            print(f"{name}: {resp.status_code} - {len(data)} items")
        else:
            print(f"{name}: {resp.status_code} - OK")
    except Exception as e:
        print(f"{name}: ERROR - {str(e)[:100]}")
