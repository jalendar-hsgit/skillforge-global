#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = "backend/app/data/skillforge.db"

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    exit(1)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Database Tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check critical tables
    critical = ['users', 'mentors', 'digital_products', 'product_purchases', 'seller_accounts']
    
    print("\nCritical Table Data:")
    for table in critical:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")
    
    conn.close()
    print("\n✅ Database is healthy")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
