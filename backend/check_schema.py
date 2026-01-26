#!/usr/bin/env python
"""Quick schema checker"""
import sqlite3

conn = sqlite3.connect('app/data/skillforge.db')
cur = conn.cursor()

# Get all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]

print("Available tables:")
for t in tables:
    print(f"  - {t}")

# Get orders schema
cur.execute("PRAGMA table_info(orders)")
columns = cur.fetchall()
print("\nOrders table columns:")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

conn.close()
