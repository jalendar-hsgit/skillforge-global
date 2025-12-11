"""Seed demo coins and job applications if missing (non-destructive)."""
from app.core.db import SessionLocal
from app.models.user import User
from app.modelsx.coins import CoinLedger
from sqlalchemy import text
from datetime import datetime

def seed_coins_and_jobs():
    db = SessionLocal()
    try:
        # Check coins
        coin_count = db.query(CoinLedger).count()
        if coin_count == 0:
            print("⚡ Coin ledger is empty, seeding demo coins...")
            users = db.query(User).filter(User.email.in_([
                'superadmin@skillforge.com',
                'admin@skillforge.com',
                'mentor@skillforge.com',
                'user@skillforge.com'
            ])).all()
            
            for user in users:
                for i in range(2):
                    ledger = CoinLedger(
                        user_id=user.id,
                        delta=100 if i == 0 else 50,
                        reason="Demo credit" if i == 0 else "Activity bonus",
                        created_at=datetime.now()
                    )
                    db.add(ledger)
            db.commit()
            print(f"✓ Created coin ledger entries for {len(users)} users")
        else:
            print(f"✓ Coin ledger already has {coin_count} entries, skipping seed")
        
        # Check job applications
        try:
            job_count = db.query(text("SELECT COUNT(*) FROM job_applications")).scalar()
        except:
            print("⚠ job_applications table not found or accessible")
            job_count = None
        
        if job_count is not None and job_count == 0:
            print("⚡ Job applications table is empty, would seed but table structure varies")
            # Skip for now - job_applications schema varies; user can manually add
        elif job_count is not None:
            print(f"✓ Job applications table already has {job_count} rows, skipping seed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_coins_and_jobs()
