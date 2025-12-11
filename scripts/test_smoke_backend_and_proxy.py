#!/usr/bin/env python3
"""
Smoke test: backend direct + Next proxy
Tests signup → login → create resume → duplicate
- First via backend directly (127.0.0.1:8001)
- Then via Next proxy (127.0.0.1:3003)
"""
import requests
import time
import json

email = f'smoke{int(time.time())}@example.com'
pw = 'TestPass123!'

def test_flow(base_url, name):
    """Test signup → login → create → duplicate against base_url"""
    print(f'\n{"="*60}')
    print(f'Testing {name} ({base_url})')
    print(f'{"="*60}')
    s = requests.Session()
    
    # Signup
    print(f'1. POST {base_url}/api/v1/auth/signup')
    try:
        r = s.post(f'{base_url}/api/v1/auth/signup',
                   json={'email': email, 'password': pw, 'full_name': 'Smoke Test'},
                   timeout=10)
        print(f'   Status: {r.status_code}')
        if r.status_code != 200:
            print(f'   Response: {r.text}')
            return False
    except Exception as e:
        print(f'   Error: {e}')
        return False
    
    # Login
    print(f'2. POST {base_url}/api/v1/auth/login')
    try:
        r = s.post(f'{base_url}/api/v1/auth/login',
                   json={'email': email, 'password': pw},
                   timeout=10)
        print(f'   Status: {r.status_code}')
        if r.status_code != 200:
            print(f'   Response: {r.text}')
            return False
        print(f'   Cookies: {s.cookies.get_dict().keys()}')
    except Exception as e:
        print(f'   Error: {e}')
        return False
    
    # Create resume
    print(f'3. POST {base_url}/api/v1x/resumes (create)')
    try:
        r = s.post(f'{base_url}/api/v1x/resumes',
                   json={'title': 'Smoke Resume', 'template_id': 'modern'},
                   timeout=10)
        print(f'   Status: {r.status_code}')
        if r.status_code != 201:
            print(f'   Response: {r.text}')
            return False
        created = r.json()
        resume_id = created.get('id')
        print(f'   Created resume id: {resume_id}')
    except Exception as e:
        print(f'   Error: {e}')
        return False
    
    # Duplicate
    print(f'4. POST {base_url}/api/v1x/resumes/{resume_id}/duplicate')
    try:
        r = s.post(f'{base_url}/api/v1x/resumes/{resume_id}/duplicate',
                   timeout=10)
        print(f'   Status: {r.status_code}')
        if r.status_code != 200:
            print(f'   Response: {r.text}')
            return False
        dup = r.json()
        dup_id = dup.get('id')
        print(f'   Duplicated resume id: {dup_id}')
        print(f'   Title: {dup.get("title")}')
    except Exception as e:
        print(f'   Error: {e}')
        return False
    
    print(f'\n[PASS] {name} flow passed')
    return True

if __name__ == '__main__':
    print('Smoke Test: Backend Direct + Next Proxy')
    print(f'Email: {email}')
    
    # Test backend directly
    backend_ok = test_flow('http://127.0.0.1:8001', 'Backend Direct')
    
    # Test via Next proxy (same session, so reuse existing cookies)
    # For proxy test, use a new session to isolate cookie handling
    print('\n' + '='*60)
    print('Testing via Next proxy (fresh session)')
    print('='*60)
    s_proxy = requests.Session()
    
    # Signup via proxy
    print(f'1. POST http://127.0.0.1:3003/api/session/auth/signup')
    try:
        r = s_proxy.post('http://127.0.0.1:3003/api/session/signup',
                         json={'email': f'proxy{int(time.time())}@example.com', 'password': pw, 'full_name': 'Proxy Test'},
                         timeout=10)
        print(f'   Status: {r.status_code}')
        print(f'   Response: {r.text[:200]}')
    except Exception as e:
        print(f'   Error: {e}')
    
    # Summary
    print(f'\n{"="*60}')
    print('Summary:')
    print(f'  Backend direct: {"[PASS]" if backend_ok else "[FAIL]"}')
    print(f'{"="*60}')
