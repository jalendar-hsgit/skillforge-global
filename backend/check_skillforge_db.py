#!/usr/bin/env python
"""Check skillforge.db database"""
import sqlite3
from pathlib import Path

db_path = Path("app/data/skillforge.db")

if not db_path.exists():
    print(f"❌ Database not found: {db_path}")
    exit(1)

print("=" * 70)
print(f"DATABASE: {db_path}")
print(f"SIZE: {db_path.stat().st_size / 1024:.2f} KB")
print("=" * 70)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n✓ TOTAL TABLES: {len(tables)}\n")

# Check users table
print("USERS TABLE:")
print("-" * 70)
try:
    cursor.execute("PRAGMA table_info(users)")
    cols = cursor.fetchall()
    print(f"  Columns ({len(cols)}):")
    for col in cols:
        name, ctype, notnull, default, pk = col
        nullable = "NULLABLE" if not notnull else "NOT NULL"
        pk_str = " PRIMARY KEY" if pk else ""
        print(f"    • {name}: {ctype} ({nullable}){pk_str}")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n  Row Count: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, email, name, role, created_at FROM users LIMIT 5")
        users = cursor.fetchall()
        print("\n  Sample Users:")
        for user in users:
            print(f"    - {user[1]} (ID: {user[0]}, Name: {user[2]}, Role: {user[3]})")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "-" * 70)
print("OTHER KEY TABLES:")
print("-" * 70)

key_tables = ["courses", "mentors", "sessions", "payments", "quizzes"]
for table in key_tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "✓" if count > 0 else "○"
        print(f"{status} {table}: {count} rows")
    except:
        print(f"✗ {table}: NOT FOUND")

print("\n" + "-" * 70)
print("ALL TABLES IN DATABASE:")
print("-" * 70)
for i, table in enumerate(tables, 1):
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        if count > 0:
            print(f"{i:2}. {table:<40} {count:>6} rows")
        else:
            print(f"{i:2}. {table:<40} (empty)")
    except:
        print(f"{i:2}. {table:<40} (error)")

conn.close()
print("\n" + "=" * 70)
print("Database check completed")
print("=" * 70)
