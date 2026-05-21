# Test Payment Flow
# Run with: pytest backend/test_payment_flow.py -v

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import get_db, Base, engine
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.modelsx.course import Course
from app.modelsx.order import Order
from decimal import Decimal
from datetime import datetime

client = TestClient(app)

# Test fixtures
@pytest.fixture(scope="function")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_user(setup_database):
    """Create test user"""
    db = next(get_db())
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash="hashed_password",
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_course():
    """Create test course"""
    db = next(get_db())
    course = Course(
        path="python-101",
        title="Python 101",
        description="Learn Python basics",
        is_paid=True,
        price=Decimal("49.99"),
        difficulty="beginner"
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.fixture(scope="function")
def auth_token(test_user):
    """Get auth token for test user"""
    from app.core.security import create_access_token
    return create_access_token(test_user.id)


# Tests
class TestOrderCreation:
    """Test order creation flow"""
    
    def test_create_order_success(self, test_user, test_course, auth_token):
        """Test creating an order successfully"""
        response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": test_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert data["data"]["course_id"] == test_course.id
        assert data["data"]["amount"] == 49.99
        assert data["data"]["status"] == "pending"
    
    def test_create_order_course_not_found(self, test_user, auth_token):
        """Test creating order with non-existent course"""
        response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": 99999, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_create_order_free_course(self, test_user, auth_token):
        """Test creating order for free course"""
        db = next(get_db())
        free_course = Course(
            path="free-course",
            title="Free Course",
            description="A free course",
            is_paid=False,
            difficulty="beginner"
        )
        db.add(free_course)
        db.commit()
        db.refresh(free_course)
        
        response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": free_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400


class TestPaymentIntentCreation:
    """Test payment intent creation"""
    
    def test_create_payment_intent_success(self, test_user, test_course, auth_token):
        """Test creating payment intent"""
        # First create order
        order_response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": test_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        order_id = order_response.json()["data"]["id"]
        
        # Then create payment intent
        response = client.post(
            "/api/v1x/orders/create-payment-intent",
            json={"order_id": order_id},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "client_secret" in data["data"]
        assert "payment_intent_id" in data["data"]
        assert data["data"]["amount"] == 49.99
    
    def test_create_payment_intent_order_not_found(self, test_user, auth_token):
        """Test payment intent with non-existent order"""
        response = client.post(
            "/api/v1x/orders/create-payment-intent",
            json={"order_id": 99999},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404


class TestOrderRetrieval:
    """Test order retrieval"""
    
    def test_get_my_orders(self, test_user, test_course, auth_token):
        """Test getting user's orders"""
        # Create order
        client.post(
            "/api/v1x/orders/create",
            json={"course_id": test_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Retrieve orders
        response = client.get(
            "/api/v1x/orders/my-orders",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "orders" in data["data"]
        assert len(data["data"]["orders"]) == 1
    
    def test_get_order_details(self, test_user, test_course, auth_token):
        """Test getting specific order"""
        # Create order
        order_response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": test_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        order_id = order_response.json()["data"]["id"]
        
        # Get order
        response = client.get(
            f"/api/v1x/orders/{order_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["id"] == order_id


class TestEndToEndPaymentFlow:
    """Test full payment flow"""
    
    def test_complete_order_flow(self, test_user, test_course, auth_token):
        """Test from order creation to payment intent"""
        # 1. Create order
        create_response = client.post(
            "/api/v1x/orders/create",
            json={"course_id": test_course.id, "payment_method": "stripe"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert create_response.status_code == 200
        order_id = create_response.json()["data"]["id"]
        
        # 2. Create payment intent
        intent_response = client.post(
            "/api/v1x/orders/create-payment-intent",
            json={"order_id": order_id},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert intent_response.status_code == 200
        payment_intent_id = intent_response.json()["data"]["payment_intent_id"]
        
        # 3. Verify order can be retrieved
        order_response = client.get(
            f"/api/v1x/orders/{order_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert order_response.status_code == 200
        assert order_response.json()["data"]["status"] == "pending"
        
        print(f"\n✅ Order flow successful:")
        print(f"   Order ID: {order_id}")
        print(f"   Payment Intent ID: {payment_intent_id}")
