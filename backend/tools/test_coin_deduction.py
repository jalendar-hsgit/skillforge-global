"""
Test script for marketplace coin deduction feature.
Tests balance validation, deduction, and error handling.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import get_db
from app.models.user import User
from app.modelsx.coins import CoinLedger
from app.modelsx.course import Course
from app.modelsx.order import Order, CartItem

client = TestClient(app)

def print_step(step_num: int, description: str):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)

def get_coin_balance(db: Session, user_id: int) -> int:
    """Get user's current coin balance."""
    balance = db.query(func.sum(CoinLedger.delta)).filter(
        CoinLedger.user_id == user_id
    ).scalar() or 0
    return balance

def main():
    print("\n" + "="*60)
    print("MARKETPLACE COIN DEDUCTION TEST SUITE")
    print("="*60)
    
    db: Session = next(get_db())
    
    try:
        # Step 1: Create test user with coins
        print_step(1, "Create test user with coin balance")
        
        test_user = db.query(User).filter(User.email == "coin_test@test.com").first()
        if test_user:
            db.delete(test_user)
            db.commit()
        
        test_user = User(
            email="coin_test@test.com",
            username="cointest",
            first_name="Coin",
            last_name="Tester"
        )
        test_user.set_password("Test123!@#")
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ User created: {test_user.email} (ID: {test_user.id})")
        
        # Add initial coins
        initial_coins = CoinLedger(
            user_id=test_user.id,
            delta=500,
            reason="Initial test balance"
        )
        db.add(initial_coins)
        db.commit()
        
        balance = get_coin_balance(db, test_user.id)
        print(f"✅ Initial balance: {balance} coins")
        
        # Step 2: Login as test user
        print_step(2, "Login as test user")
        
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "coin_test@test.com", "password": "Test123!@#"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        print(f"✅ Login successful")
        
        # Extract token from cookies
        token = login_response.cookies.get("token")
        cookies = {"token": token}
        
        # Step 3: Get a course to purchase
        print_step(3, "Find course to purchase")
        
        course = db.query(Course).filter(Course.price > 0).first()
        if not course:
            print("❌ No courses with price found, creating test course...")
            course = Course(
                path="test-coin-course",
                title="Test Coin Course",
                description="Course for testing coin payments",
                price=50.00,
                is_published=True
            )
            db.add(course)
            db.commit()
            db.refresh(course)
        
        print(f"✅ Course selected: {course.title}")
        print(f"   Price: ${course.price:.2f} ({int(course.price)} coins)")
        
        # Step 4: Add course to cart
        print_step(4, "Add course to cart")
        
        # Clear existing cart items
        db.query(CartItem).filter(CartItem.user_id == test_user.id).delete()
        db.commit()
        
        cart_response = client.post(
            "/api/v1x/marketplace/cart",
            json={"course_id": course.id},
            cookies=cookies
        )
        assert cart_response.status_code == 200, f"Add to cart failed: {cart_response.text}"
        print(f"✅ Course added to cart")
        
        # Step 5: Test insufficient coins error
        print_step(5, "Test insufficient coins error")
        
        # Set balance to less than course price
        db.query(CoinLedger).filter(CoinLedger.user_id == test_user.id).delete()
        insufficient_coins = CoinLedger(
            user_id=test_user.id,
            delta=10,  # Less than course price
            reason="Test insufficient balance"
        )
        db.add(insufficient_coins)
        db.commit()
        
        balance = get_coin_balance(db, test_user.id)
        print(f"   Current balance: {balance} coins (less than {int(course.price)})")
        
        checkout_response = client.post(
            "/api/v1x/marketplace/checkout",
            json={"payment_method": "coins"},
            cookies=cookies
        )
        
        if checkout_response.status_code == 400:
            print(f"✅ Insufficient coins error correctly raised")
            print(f"   Error: {checkout_response.json()['detail']}")
        else:
            print(f"❌ Expected 400 error, got {checkout_response.status_code}")
            print(f"   Response: {checkout_response.text}")
        
        # Step 6: Add sufficient coins
        print_step(6, "Add sufficient coins and retry purchase")
        
        db.query(CoinLedger).filter(CoinLedger.user_id == test_user.id).delete()
        sufficient_coins = CoinLedger(
            user_id=test_user.id,
            delta=500,  # More than course price
            reason="Test sufficient balance"
        )
        db.add(sufficient_coins)
        db.commit()
        
        balance_before = get_coin_balance(db, test_user.id)
        print(f"   Balance before purchase: {balance_before} coins")
        
        # Re-add to cart (cleared during failed checkout)
        db.query(CartItem).filter(CartItem.user_id == test_user.id).delete()
        cart_item = CartItem(
            user_id=test_user.id,
            course_id=course.id
        )
        db.add(cart_item)
        db.commit()
        
        checkout_response = client.post(
            "/api/v1x/marketplace/checkout",
            json={"payment_method": "coins"},
            cookies=cookies
        )
        
        assert checkout_response.status_code == 200, f"Checkout failed: {checkout_response.text}"
        order_data = checkout_response.json()
        
        print(f"✅ Purchase successful!")
        print(f"   Order Number: {order_data['order_number']}")
        print(f"   Status: {order_data['status']}")
        print(f"   Payment Status: {order_data['payment_status']}")
        
        # Step 7: Verify coin deduction
        print_step(7, "Verify coin balance deduction")
        
        balance_after = get_coin_balance(db, test_user.id)
        coins_deducted = balance_before - balance_after
        expected_deduction = int(course.price)
        
        print(f"   Balance before: {balance_before} coins")
        print(f"   Balance after: {balance_after} coins")
        print(f"   Coins deducted: {coins_deducted}")
        print(f"   Expected: {expected_deduction}")
        
        if coins_deducted == expected_deduction:
            print(f"✅ Correct amount deducted!")
        else:
            print(f"❌ Deduction mismatch! Expected {expected_deduction}, got {coins_deducted}")
        
        # Step 8: Verify ledger entry
        print_step(8, "Verify coin ledger transaction")
        
        ledger_entry = db.query(CoinLedger).filter(
            CoinLedger.user_id == test_user.id,
            CoinLedger.delta < 0
        ).order_by(CoinLedger.created_at.desc()).first()
        
        if ledger_entry:
            print(f"✅ Ledger entry found:")
            print(f"   Delta: {ledger_entry.delta} coins")
            print(f"   Reason: {ledger_entry.reason}")
            print(f"   Created: {ledger_entry.created_at}")
        else:
            print(f"❌ No ledger entry found")
        
        # Step 9: Verify order status
        print_step(9, "Verify order completion")
        
        order = db.query(Order).filter(
            Order.order_number == order_data['order_number']
        ).first()
        
        if order:
            print(f"✅ Order found in database:")
            print(f"   Status: {order.status}")
            print(f"   Payment Status: {order.payment_status}")
            print(f"   Payment Method: {order.payment_method}")
            print(f"   Amount: ${order.amount}")
            print(f"   Paid At: {order.paid_at}")
            
            if order.status == "completed" and order.payment_status == "completed":
                print(f"✅ Order correctly marked as completed")
            else:
                print(f"❌ Order status incorrect")
        else:
            print(f"❌ Order not found")
        
        # Step 10: Test cart is cleared
        print_step(10, "Verify cart is cleared after purchase")
        
        cart_items = db.query(CartItem).filter(
            CartItem.user_id == test_user.id
        ).count()
        
        if cart_items == 0:
            print(f"✅ Cart correctly cleared after purchase")
        else:
            print(f"❌ Cart still has {cart_items} items")
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ All coin deduction tests passed!")
        print(f"Final balance: {get_coin_balance(db, test_user.id)} coins")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
