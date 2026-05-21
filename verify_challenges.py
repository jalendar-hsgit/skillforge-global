#!/usr/bin/env python3
"""Verify that the API returns different challenges for different slugs"""

import requests
import json

# Test slugs from the comprehensive seed file
test_slugs = [
    'two-sum',
    'reverse-string',
    'palindrome-number',
    'valid-parentheses',
    'binary-search',
    'reverse-linked-list',
    'longest-substring-no-repeat',
]

print("=" * 80)
print("TESTING CHALLENGE ENDPOINTS")
print("=" * 80)

# Test 1: Get challenge list
print("\n1. Testing /challenges endpoint (list):")
try:
    r = requests.get('http://localhost:8001/api/v1x/coding-practice/challenges?limit=10')
    r.raise_for_status()
    challenges = r.json()
    print(f"   ✓ Got {len(challenges)} challenges")
    print("   First 5:")
    for c in challenges[:5]:
        print(f"     - {c['title']:30} ({c['slug']:30}) difficulty: {c['difficulty']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Get specific challenges
print("\n2. Testing /challenges/{slug} endpoint (detail):")
print("   Slug".ljust(30), "Title".ljust(30), "Difficulty")
print("   " + "-" * 77)

for slug in test_slugs:
    try:
        r = requests.get(f'http://localhost:8001/api/v1x/coding-practice/challenges/{slug}')
        r.raise_for_status()
        data = r.json()
        print(f"   {slug:30} {data['title']:30} {data['difficulty']}")
    except Exception as e:
        print(f"   {slug:30} ERROR: {e}")

print("\n" + "=" * 80)
print("Test completed!")
print("=" * 80)
