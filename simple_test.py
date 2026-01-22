#!/usr/bin/env python3
import subprocess
import sys

# Test endpoints with curl
tests = [
    ("Admin Login", "curl -X POST http://localhost:8001/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@skillforge.com\",\"password\":\"admin123\"}' -s"),
    ("Mentor Login", "curl -X POST http://localhost:8001/api/v1/auth/login -H 'Content-Type: application/json' -d '{\"email\":\"mentor.sarah@skillforge.com\",\"password\":\"mentor123\"}' -s"),
]

for name, cmd in tests:
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(result.stdout[:500])
        if result.stderr:
            print("STDERR:", result.stderr[:500])
    except Exception as e:
        print(f"ERROR: {e}")
