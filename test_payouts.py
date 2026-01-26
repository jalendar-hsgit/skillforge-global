#!/usr/bin/env python
"""Test the payouts endpoint"""
import requests
import json

# Test login
response = requests.post('http://localhost:8001/api/v1x/auth/login', 
    json={'email': 'superadmin@skillforge.com', 'password': 'password123'})
print(f'Login status: {response.status_code}')
data = response.json()
print(f'Login response: {json.dumps(data, indent=2)}')

if data.get('data') and data['data'].get('access_token'):
    token = data['data']['access_token']
    print(f'\nToken obtained: {token[:20]}...')
    
    # Test payouts endpoint
    headers = {'Authorization': f'Bearer {token}'}
    payouts = requests.get('http://localhost:8001/api/v1x/mentors/payouts/earnings', 
        headers=headers)
    print(f'\nPayouts status: {payouts.status_code}')
    print(f'Payouts response: {payouts.text}')
else:
    print(f'\nLogin failed or no token returned')
