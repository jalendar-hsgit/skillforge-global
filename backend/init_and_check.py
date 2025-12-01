from app.main import app
print("App imported, tables should be created...")

import sqlite3
conn = sqlite3.connect('skillforge.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

if 'mentor_sessions' in tables:
    cursor.execute('PRAGMA table_info(mentor_sessions)')
    columns = [row[1] for row in cursor.fetchall()]
    print("mentor_sessions columns:", columns)
else:
    print("mentor_sessions table not found")
    
conn.close()
