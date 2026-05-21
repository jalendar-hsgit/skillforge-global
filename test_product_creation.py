#!/usr/bin/env python3
"""
Test product creation via API
"""
import requests
import json

BASE_URL = "http://localhost:8001/api/v1x"

def test_product_creation():
    """Test creating a product"""
    
    # First, login
    print("1. Testing login...")
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "sarah.chen@skillforge.com",
        "password": "password123"
    })
    print(f"   Status: {login_res.status_code}")
    
    if login_res.status_code != 200:
        print(f"   Login failed: {login_res.text}")
        return
    
    # Get session from cookies
    cookies = login_res.cookies
    print(f"   Logged in successfully. Cookies: {cookies}")
    
    # Create a product
    print("\n2. Testing product creation...")
    product_data = {
        "name": "Python Masterclass - Test Product",
        "description": "A comprehensive guide to mastering Python programming from basics to advanced concepts",
        "product_type": "course",
        "category": "programming",
        "price": 49.99,
        "tags": ["python", "programming", "beginner"],
        "requirements": ["Basic computer knowledge"],
        "features": ["Video tutorials", "Code examples", "Lifetime access"],
        "thumbnail_url": None,
        "content_url": None,
        "preview_url": None
    }
    
    print(f"   Payload: {json.dumps(product_data, indent=2)}")
    
    create_res = requests.post(
        f"{BASE_URL}/marketplace/seller/products",
        json=product_data,
        cookies=cookies
    )
    
    print(f"   Status: {create_res.status_code}")
    print(f"   Response: {create_res.text}")
    
    if create_res.status_code == 200 or create_res.status_code == 201:
        print("\n✅ SUCCESS! Product created.")
        product = create_res.json()
        print(f"   Product ID: {product.get('id')}")
        print(f"   Product Name: {product.get('name')}")
        print(f"   Product Slug: {product.get('slug')}")
    else:
        print(f"\n❌ FAILED! Status: {create_res.status_code}")
        print(f"   Response: {create_res.json()}")

if __name__ == "__main__":
    test_product_creation()
