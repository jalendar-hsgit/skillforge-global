"""Create a test coupon for marketplace testing."""
from app.core.db import SessionLocal
from app.modelsx.order import Coupon
from decimal import Decimal
from datetime import datetime, timedelta

db = SessionLocal()

# Check if coupon exists
existing = db.query(Coupon).filter(Coupon.code == 'WELCOME10').first()

if not existing:
    coupon = Coupon(
        code='WELCOME10',
        discount_type='percentage',
        discount_value=Decimal('10'),
        is_active=True,
        valid_from=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(days=30),
        usage_limit=100,
        usage_count=0
    )
    db.add(coupon)
    db.commit()
    print('✓ Created coupon: WELCOME10 (10% off)')
else:
    print('✓ Coupon already exists: WELCOME10')

db.close()
