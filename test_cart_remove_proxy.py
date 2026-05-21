#!/usr/bin/env python3
"""
Test cart remove functionality via the Next.js proxy
This simulates what the browser does
"""
import requests
import json
from http.cookiejar import CookieJar

# Create a session with cookie handling (like browser does)
session = requests.Session()

print("=" * 60)
print("STEP 1: Login via /api/session/login (Next.js proxy)")
print("=" * 60)

login_response = session.post(
    'http://localhost:3000/api/session/login',
    json={
        'email': 'admin@skillforge.com',
        'password': 'admin123'
    }
)

print(f"Status: {login_response.status_code}")
print(f"Response: {login_response.json()}")
print(f"Cookies in session: {session.cookies.get_dict()}")

print("\n" + "=" * 60)
print("STEP 2: Get cart via /api/session/v1x/marketplace/cart")
print("=" * 60)

cart_response = session.get(
    'http://localhost:3000/api/session/v1x/marketplace/cart'
)

print(f"Status: {cart_response.status_code}")
if cart_response.ok:
    cart_data = cart_response.json()
    print(f"Items in cart: {len(cart_data.get('items', []))}")
    for item in cart_data.get('items', []):
        print(f"  - Item {item['id']}: Course {item['course_id']}")
else:
    print(f"Error: {cart_response.text}")

print("\n" + "=" * 60)
print("STEP 3: Remove item via DELETE /api/session/v1x/marketplace/cart/1")
print("=" * 60)

# Get the first item ID from cart
if cart_response.ok:
    cart_data = cart_response.json()
    if cart_data.get('items'):
        item_id_to_delete = cart_data['items'][0]['id']
        print(f"Deleting item ID: {item_id_to_delete}")
        
        delete_response = session.delete(
            f'http://localhost:3000/api/session/v1x/marketplace/cart/{item_id_to_delete}'
        )
        
        print(f"Status: {delete_response.status_code}")
        print(f"Response: {delete_response.json()}")
        
        print("\n" + "=" * 60)
        print("STEP 4: Verify deletion - get cart again")
        print("=" * 60)
        
        cart_response_2 = session.get(
            'http://localhost:3000/api/session/v1x/marketplace/cart'
        )
        
        print(f"Status: {cart_response_2.status_code}")
        if cart_response_2.ok:
            cart_data_2 = cart_response_2.json()
            print(f"Items in cart: {len(cart_data_2.get('items', []))}")
            for item in cart_data_2.get('items', []):
                print(f"  - Item {item['id']}: Course {item['course_id']}")
            
            if len(cart_data_2.get('items', [])) == len(cart_data.get('items', [])) - 1:
                print("\n✅ SUCCESS: Item was deleted!")
            else:
                print("\n❌ FAILED: Item count didn't decrease!")
        else:
            print(f"Error: {cart_response_2.text}")
