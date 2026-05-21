#!/usr/bin/env python3
import urllib.request
urls = [
    'http://127.0.0.1:3000/',
    'http://127.0.0.1:3000/paths',
    'http://127.0.0.1:3000/resumes',
    'http://127.0.0.1:3000/mentors',
    'http://127.0.0.1:3000/marketplace',
    'http://127.0.0.1:3000/job-tracker'
]
print('=== FRONTEND SMOKE TEST ===')
for u in urls:
    try:
        r = urllib.request.urlopen(u, timeout=10)
        body = r.read(2000).decode('utf-8',errors='ignore')
        found = 'YES' if ('<html' in body.lower()) else 'NO'
        print(f'{u:40} {r.getcode()} html={found} len={len(body)}')
    except Exception as e:
        print(f'{u:40} ERROR {e}')
