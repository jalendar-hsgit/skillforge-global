#!/usr/bin/env python
"""Quick test of Resume AI endpoints"""

import requests

# Test summary endpoint directly
res = requests.post('http://localhost:8001/api/v1x/resume-ai/professional-summary', 
    json={'title': 'Senior Dev', 'years_of_experience': 5}
)

print(f"Status: {res.status_code}")
if res.status_code == 200:
    data = res.json()
    print(f"✅ Summary generated ({len(data.get('summary', ''))} chars)")
    print(f"Summary: {data['summary'][:100]}...")
    print(f"Variations: {len(data.get('variations', []))}")
elif res.status_code == 401:
    print("❌ Requires authentication")
else:
    print(f"❌ Error: {res.text[:300]}")
