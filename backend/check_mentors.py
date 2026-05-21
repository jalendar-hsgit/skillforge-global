import sqlite3

conn = sqlite3.connect('./app/data/skillforge.db')
cursor = conn.cursor()

# Check mentors
cursor.execute('SELECT id, user_id, bio, expertise, hourly_rate, status FROM mentors LIMIT 5')
mentors = cursor.fetchall()
print(f"\n=== MENTORS ({len(mentors)} found) ===")
for m in mentors:
    print(f"ID: {m[0]}, User: {m[1]}, Rate: ${m[4]}, Status: {m[5]}")
    print(f"  Expertise: {m[3]}")
    print(f"  Bio: {m[2][:80]}...")
    print()

# Check users
cursor.execute('SELECT id, email FROM users WHERE id IN (SELECT user_id FROM mentors)')
users = cursor.fetchall()
print(f"=== MENTOR USERS ({len(users)} found) ===")
for u in users:
    print(f"  {u[0]}: {u[1]}")

# Check availability
cursor.execute('SELECT mentor_id, COUNT(*) FROM mentor_availability GROUP BY mentor_id')
avail = cursor.fetchall()
print(f"\n=== AVAILABILITY BY MENTOR ===")
for a in avail:
    print(f"  Mentor {a[0]}: {a[1]} slots")

# Check sessions
cursor.execute('SELECT COUNT(*) FROM mentor_sessions')
sessions = cursor.fetchone()[0]
print(f"\n=== SESSIONS: {sessions} total ===")

conn.close()
