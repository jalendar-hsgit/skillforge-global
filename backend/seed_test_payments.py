#!/usr/bin/env python
"""Seed test data: Create an approved mentor and process payments"""

import sqlite3
from datetime import datetime, timedelta

DATABASE = "app/data/skillforge.db"
conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n🔧 SEEDING TEST DATA FOR MENTOR PAYMENTS\n")

# Check if we have any users
cur.execute("SELECT id FROM users LIMIT 1")
user = cur.fetchone()

if not user:
    print("❌ No users found in database. Run seed_all_demo_data.py first.")
    exit(1)

# Create or get a mentor
cur.execute("SELECT id, user_id FROM mentors LIMIT 1")
mentor = cur.fetchone()

if not mentor:
    # Create a mentor from first user
    cur.execute("SELECT id FROM users WHERE id != 1 LIMIT 1")
    user_id = cur.fetchone()['id']
    
    cur.execute("""
        INSERT INTO mentors
        (user_id, bio, expertise, hourly_rate, status, approved_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, "Test mentor bio", "python-ai,web-dev", 75.0, "approved",
          datetime.now(), datetime.now(), datetime.now()))
    
    conn.commit()
    print(f"✅ Created mentor for user {user_id}")
    mentor_id = cur.lastrowid
else:
    mentor_id = mentor['id']
    # Approve if not approved
    cur.execute("""
        UPDATE mentors SET status = 'approved', approved_at = ?
        WHERE id = ? AND status != 'approved'
    """, (datetime.now(), mentor_id))
    conn.commit()
    print(f"✅ Using existing mentor {mentor_id}")

# Get some mentor sessions
cur.execute("""
    SELECT id FROM mentor_sessions
    WHERE mentor_id = ? AND price > 0
    LIMIT 5
""", (mentor_id,))
sessions = cur.fetchall()

if not sessions:
    print("❌ No priced mentor sessions found")
else:
    print(f"Found {len(sessions)} mentor sessions to process\n")
    
    # Process each session
    count = 0
    for session in sessions:
        session_id = session['id']
        
        # Check if already has earnings
        cur.execute("SELECT id FROM mentor_earnings WHERE session_id = ?", (session_id,))
        if cur.fetchone():
            continue
        
        # Get session price
        cur.execute("SELECT price FROM mentor_sessions WHERE id = ?", (session_id,))
        price_row = cur.fetchone()
        if not price_row or price_row['price'] <= 0:
            continue
        
        price = price_row['price']
        
        # Create earning
        cur.execute("""
            INSERT INTO mentor_earnings
            (mentor_id, session_id, gross_amount, platform_fee, net_amount, earned_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (mentor_id, session_id, price, price*0.20, price*0.80, datetime.now()))
        
        count += 1
        print(f"  ✅ Session {session_id}: ${price:.2f} → Mentor: ${price*0.80:.2f}, Platform: ${price*0.20:.2f}")
    
    conn.commit()
    print(f"\n✅ Created {count} mentor earnings records\n")

# Get seller earnings
cur.execute("""
    SELECT id, product_id, seller_id FROM product_purchases
    WHERE status = 'completed'
    LIMIT 1
""")
purchase = cur.fetchone()

if purchase:
    product_id = purchase['product_id']
    seller_id = purchase['seller_id']
    
    # Get purchase price
    cur.execute("SELECT purchase_price FROM product_purchases WHERE id = ?", (purchase['id'],))
    price_row = cur.fetchone()
    price = price_row['purchase_price'] if price_row else 0
    
    # Check if already has earnings
    cur.execute("""
        SELECT id FROM seller_earnings
        WHERE seller_id = ? AND product_id = ?
    """, (seller_id, product_id))
    
    if not cur.fetchone() and price > 0:
        # Use product purchase id as order_id equivalent
        cur.execute("""
            INSERT INTO seller_earnings
            (seller_id, order_id, product_id, gross_amount, platform_fee, net_amount, earned_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (seller_id, purchase['id'], product_id, price, price*0.20, price*0.80,
              datetime.now()))
        
        conn.commit()
        print(f"✅ Seller earnings: ${price:.2f} → Seller: ${price*0.80:.2f}, Platform: ${price*0.20:.2f}\n")

conn.close()
print("✅ Test data seeded successfully!\n")
