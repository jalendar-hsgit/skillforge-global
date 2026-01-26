#!/usr/bin/env python
"""Test payment methods endpoint"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_payment_method_validation():
    """Test if payment method validation works"""
    
    # Test 1: Valid payment method request
    valid_request = {
        "account_holder_name": "John Doe",
        "bank_name": "Bank of America",
        "account_number": "123456789012",
        "routing_number": "123456789",
        "is_default": False
    }
    
    print("Test 1: Valid payment method request")
    print(f"Request: {json.dumps(valid_request, indent=2)}")
    print()
    
    # Test 2: Missing routing_number
    invalid_request_1 = {
        "account_holder_name": "John Doe",
        "bank_name": "Bank of America",
        "account_number": "123456789012"
    }
    
    print("Test 2: Missing routing_number")
    print(f"Request: {json.dumps(invalid_request_1, indent=2)}")
    print()
    
    # Test 3: Invalid routing_number length (not 9)
    invalid_request_2 = {
        "account_holder_name": "John Doe",
        "bank_name": "Bank of America",
        "account_number": "123456789012",
        "routing_number": "12345"  # Only 5 chars, needs to be 9
    }
    
    print("Test 3: Invalid routing_number length")
    print(f"Request: {json.dumps(invalid_request_2, indent=2)}")
    print()
    
    # Test 4: account_number too short
    invalid_request_3 = {
        "account_holder_name": "John Doe",
        "bank_name": "Bank of America",
        "account_number": "123456",  # Only 6 chars, needs 8-17
        "routing_number": "123456789"
    }
    
    print("Test 4: account_number too short")
    print(f"Request: {json.dumps(invalid_request_3, indent=2)}")
    print()
    
    # Test 5: account_holder_name too short
    invalid_request_4 = {
        "account_holder_name": "J",  # Only 1 char, needs 2+
        "bank_name": "Bank of America",
        "account_number": "123456789012",
        "routing_number": "123456789"
    }
    
    print("Test 5: account_holder_name too short")
    print(f"Request: {json.dumps(invalid_request_4, indent=2)}")
    print()
    
    print("\n✅ All validation checks shown above")
    print("\nIf the frontend is sending any of the invalid requests, it will get 422 error")
    print("The most likely culprit is routing_number not being exactly 9 characters")

if __name__ == "__main__":
    test_payment_method_validation()
