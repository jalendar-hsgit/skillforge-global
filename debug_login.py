#!/usr/bin/env python3
"""Debug login issues."""

import sqlite3
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Check database
print("=" * 60)
print("CHECKING DATABASE FOR USERS")
print("=" * 60)

db_path = 'backend/app/data/skillforge.db'
if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables first
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name LIMIT 15")
tables = cursor.fetchall()

total_tables = cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table"').fetchone()[0]
print(f"\nTotal tables: {total_tables}")
print("\nFirst 15 tables:")
for table in tables:
    print(f"  - {table[0]}")

# Find user-related tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%user%'")
user_tables = cursor.fetchall()

if user_tables:
    print("\nTables with 'user' in name:")
    for table in user_tables:
        print(f"  - {table[0]}")
else:
    print("\n⚠️  No tables with 'user' in name found!")

# Get all users
cursor.execute("SELECT id, email, role FROM users")
users = cursor.fetchall()

print(f"\nTotal users: {len(users)}")
if users:
    for user in users:
        print(f"  ID: {user[0]:<3} Email: {user[1]:<40} Role: {user[2]}")
else:
    print("⚠️  NO USERS FOUND!")

# Check specific test users
print("\n" + "=" * 60)
print("TEST USER CREDENTIALS")
print("=" * 60)

test_emails = [
    'admin@skillforge.com',
    'charlie.brown@example.com',
    'mentor.sarah@skillforge.com',
    'jane.smith@example.com'
]

for email in test_emails:
    cursor.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    if result:
        has_pwd = "✅" if result[2] else "❌"
        print(f"{has_pwd} {email:<40} [ID: {result[0]}]")
    else:
        print(f"❌ {email:<40} NOT FOUND")

conn.close()

# Try logging in
print("\n" + "=" * 60)
print("TESTING LOGIN API")
print("=" * 60)

try:
    import requests
    
    response = requests.post(
        'http://localhost:8001/api/v1/auth/login',
        json={'email': 'admin@skillforge.com', 'password': 'admin123'},
        timeout=5
    )
    print(f"Admin Login: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text}")
    else:
        print(f"✅ Login successful!")
        print(f"Response keys: {list(response.json().keys())}")
        
except Exception as e:
    print(f"❌ API request failed: {e}")
