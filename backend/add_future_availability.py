"""Add future availability slots for testing booking flow."""
from datetime import datetime, timedelta
from app.core.db import SessionLocal
from app.modelsx.mentor import MentorAvailability

def add_future_slots():
    db = SessionLocal()
    try:
        # Get current mentors
        existing_avail = db.query(MentorAvailability).all()
        print(f"Existing slots: {len(existing_avail)}")
        
        # Delete old/past slots
        now = datetime.utcnow()
        deleted = db.query(MentorAvailability).filter(
            MentorAvailability.start_time < now
        ).delete()
        db.commit()
        print(f"Deleted {deleted} past slots")
        
        # Add future slots for next 14 days for each mentor
        for mentor_id in [1, 2, 3]:
            print(f"\nAdding slots for Mentor {mentor_id}:")
            for day_offset in range(1, 15):  # Next 14 days
                slot_date = now + timedelta(days=day_offset)
                
                # Morning slot: 10:00 - 11:00
                morning_start = slot_date.replace(hour=10, minute=0, second=0, microsecond=0)
                morning_end = slot_date.replace(hour=11, minute=0, second=0, microsecond=0)
                
                morning_slot = MentorAvailability(
                    mentor_id=mentor_id,
                    day_of_week=slot_date.strftime('%A'),
                    date=slot_date.date(),
                    start_time=morning_start,
                    end_time=morning_end,
                    is_available=True,
                    is_booked=False,
                    timezone='UTC'
                )
                db.add(morning_slot)
                
                # Afternoon slot: 14:00 - 15:00
                afternoon_start = slot_date.replace(hour=14, minute=0, second=0, microsecond=0)
                afternoon_end = slot_date.replace(hour=15, minute=0, second=0, microsecond=0)
                
                afternoon_slot = MentorAvailability(
                    mentor_id=mentor_id,
                    day_of_week=slot_date.strftime('%A'),
                    date=slot_date.date(),
                    start_time=afternoon_start,
                    end_time=afternoon_end,
                    is_available=True,
                    is_booked=False,
                    timezone='UTC'
                )
                db.add(afternoon_slot)
            
            print(f"  Added 28 slots (2 per day for 14 days)")
        
        db.commit()
        
        # Verify
        future_slots = db.query(MentorAvailability).filter(
            MentorAvailability.start_time > now
        ).all()
        print(f"\n✅ Total future slots: {len(future_slots)}")
        
        # Show sample
        print("\nSample slots:")
        for slot in future_slots[:5]:
            print(f"  Mentor {slot.mentor_id}: {slot.start_time} - {slot.end_time}")
            
    finally:
        db.close()

if __name__ == "__main__":
    add_future_slots()
