"""
Create a test coupon for marketplace E2E testing.
"""
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import datetime, timedelta
from pathlib import Path

from app.core.config import settings
from app.modelsx.order import Coupon


def create_test_coupon(session: Session) -> Coupon:
    # Check if coupon already exists
    existing = session.query(Coupon).filter(Coupon.code == 'WELCOME10').first()
    if existing:
        print(f"Coupon 'WELCOME10' already exists (ID: {existing.id})")
        return existing

    # Create new coupon
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
    session.add(coupon)
    session.commit()
    session.refresh(coupon)
    
    print(f"✓ Created coupon: {coupon.code} - {coupon.discount_value}% off")
    return coupon


def main():
    # Ensure DB file directory exists for sqlite
    if settings.DATABASE_URL.startswith("sqlite"):
        p = settings.DATABASE_URL.split("sqlite:///")[-1]
        path = Path(p)
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(settings.DATABASE_URL, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        coupon = create_test_coupon(session)
        print({
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": float(coupon.discount_value),
            "valid_until": coupon.valid_until.isoformat() if coupon.valid_until else None
        })


if __name__ == "__main__":
    main()
