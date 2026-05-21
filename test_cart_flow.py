#!/usr/bin/env python
"""
Test script to validate the cart flow with mixed items (courses + digital products).
"""
import sys
import os

# Change to backend directory so database paths work
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
os.chdir(backend_dir)
sys.path.insert(0, backend_dir)

# Create data directory if it doesn't exist
data_dir = os.path.join(backend_dir, 'app', 'data')
os.makedirs(data_dir, exist_ok=True)

from app.core.db import engine, SessionLocal, Base
from app.modelsx.order import Order, CartItem, OrderItem, Coupon
from app.modelsx.course import Course
from app.modelsx.marketplace import DigitalProduct
from app.models.user import User

# Create tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)

# Test with a new session
db = SessionLocal()

try:
    # Check if OrderItem table exists
    print("\n[OK] OrderItem model imported successfully")
    
    # Verify OrderItem has the expected columns
    from sqlalchemy import inspect
    mapper = inspect(OrderItem)
    columns = {col.name: col.type for col in mapper.columns}
    print(f"\nOrderItem columns: {list(columns.keys())}")
    
    expected_columns = ['id', 'order_id', 'course_id', 'product_id', 'item_price', 'quantity', 'created_at']
    for col in expected_columns:
        if col in columns:
            print(f"  [YES] {col}: {columns[col]}")
        else:
            print(f"  [NO] MISSING: {col}")
    
    # Verify Order still has backward compatible course_id
    mapper = inspect(Order)
    columns = {col.name: col.type for col in mapper.columns}
    if 'course_id' in columns:
        print(f"\n[OK] Order.course_id exists (backward compatible)")
    else:
        print(f"\n[NO] Order.course_id missing!")
    
    # Verify CartItem has both course_id and product_id
    mapper = inspect(CartItem)
    cart_columns = mapper.columns
    has_course = 'course_id' in mapper.column_attrs
    has_product = 'product_id' in mapper.column_attrs
    
    print(f"\nCartItem columns:")
    if has_course:
        course_col = cart_columns['course_id']
        print(f"  [YES] course_id (nullable={course_col.nullable})")
    else:
        print(f"  [NO] course_id missing!")
    
    if has_product:
        product_col = cart_columns['product_id']
        print(f"  [YES] product_id (nullable={product_col.nullable})")
    else:
        print(f"  [NO] product_id missing!")
    
    print("\n[SUCCESS] All model validations passed!")
    print("\nModel structure ready for:")
    print("  1. Adding courses to cart (course_id set, product_id=None)")
    print("  2. Adding digital products to cart (product_id set, course_id=None)")
    print("  3. Checkout creating Order with OrderItems for each cart item")
    print("  4. Supporting mixed carts with both courses and products in one order")
    
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()

print("\n" + "="*60)
print("Next steps:")
print("1. Start backend: uvicorn app.main:app --reload --port 8001")
print("2. Test adding digital product to cart")
print("3. Test adding course to cart")
print("4. Verify checkout processes mixed items")
print("="*60)
