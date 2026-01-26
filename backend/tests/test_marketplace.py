"""
Automated Tests for Digital Marketplace API
Revenue Feature: $100K/mo
"""

import pytest
import requests
from datetime import datetime

BASE_URL = "http://localhost:8001"
STUDENT_EMAIL = "john.doe@example.com"
STUDENT_PASSWORD = "student123"


class TestDigitalMarketplace:
    """Test suite for digital marketplace"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data and auth tokens"""
        response = requests.post(
            f"{BASE_URL}/api/v1x/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
        )
        self.token = response.json()["access_token"]
    
    def test_01_list_products(self):
        """Test: GET /marketplace/digital-products - List products"""
        response = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "products" in data
        assert len(data["products"]) >= 3, "Should have 3+ products from demo"
        
        product = data["products"][0]
        assert "id" in product
        assert "name" in product
        assert "slug" in product
        assert "price" in product
        assert "sales_count" in product
        
        print(f"✅ Listed {len(data['products'])} products")
        return True
    
    def test_02_get_product_detail(self):
        """Test: GET /marketplace/digital-products/{id} - Product detail"""
        response = requests.get(f"{BASE_URL}/api/v1x/marketplace/digital-products/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == 1
        assert "description" in data
        assert "features" in data
        assert "requirements" in data
        assert "seller" in data
        
        print(f"✅ Retrieved product: {data['name']} (${data['price']})")
        return True
    
    def test_03_get_empty_cart(self):
        """Test: GET /marketplace/cart - Empty cart"""
        response = requests.get(
            f"{BASE_URL}/api/v1x/marketplace/cart",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "subtotal" in data
        assert "tax" in data
        assert "total" in data
        
        print(f"✅ Cart initialized (empty)")
        return True
    
    def test_04_add_to_cart(self):
        """Test: POST /marketplace/cart/add - Add to cart"""
        response = requests.post(
            f"{BASE_URL}/api/v1x/marketplace/cart/add",
            json={"product_id": 1},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) > 0, "Should have items"
        assert data["items"][0]["product_id"] == 1
        assert data["subtotal"] > 0
        assert data["total"] > 0
        
        self.total = data["total"]
        print(f"✅ Added product to cart (Total: ${data['total']})")
        return True
    
    def test_05_checkout(self):
        """Test: POST /marketplace/checkout - Checkout"""
        # Add product first
        requests.post(
            f"{BASE_URL}/api/v1x/marketplace/cart/add",
            json={"product_id": 1},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        response = requests.post(
            f"{BASE_URL}/api/v1x/marketplace/checkout",
            json={"product_ids": [1], "coupon_code": None},
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "order_id" in data
        assert "order_number" in data
        assert data["status"] == "completed"
        assert "download_url" in data
        
        print(f"✅ Order completed: {data['order_number']}")
        return True
    
    def test_06_seller_dashboard(self):
        """Test: GET /seller/dashboard - Seller stats"""
        seller_email = "jane.smith@example.com"
        seller_password = "seller123"
        
        login_response = requests.post(
            f"{BASE_URL}/api/v1x/auth/login",
            json={"email": seller_email, "password": seller_password}
        )
        seller_token = login_response.json()["access_token"]
        
        response = requests.get(
            f"{BASE_URL}/api/v1x/seller/dashboard",
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_revenue" in data
        assert "total_sales" in data
        assert "average_price" in data
        
        print(f"✅ Seller dashboard: ${data['total_revenue']} revenue, {data['total_sales']} sales")
        return True


def run_marketplace_tests():
    """Run all marketplace tests"""
    print("\n" + "="*60)
    print("DIGITAL MARKETPLACE TEST SUITE")
    print("="*60 + "\n")
    
    test_suite = TestDigitalMarketplace()
    test_suite.setup()
    
    results = []
    tests = [
        ("List Products", test_suite.test_01_list_products),
        ("Product Detail", test_suite.test_02_get_product_detail),
        ("Empty Cart", test_suite.test_03_get_empty_cart),
        ("Add to Cart", test_suite.test_04_add_to_cart),
        ("Checkout", test_suite.test_05_checkout),
        ("Seller Dashboard", test_suite.test_06_seller_dashboard),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, "PASS", None))
        except Exception as e:
            results.append((test_name, "FAIL", str(e)))
    
    # Print results
    print("\n" + "="*60)
    print("MARKETPLACE TEST RESULTS")
    print("="*60 + "\n")
    
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    
    for test_name, status, error in results:
        status_symbol = "✅" if status == "PASS" else "❌"
        print(f"{status_symbol} {test_name}: {status}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\nSuccess Rate: {(passed/len(results)*100):.1f}%")
    print("="*60 + "\n")
    
    return results


if __name__ == "__main__":
    run_marketplace_tests()
