import sqlite3
conn = sqlite3.connect('backend/app/data/skillforge.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [t[0] for t in c.fetchall()]
print("Tables in database:", tables)

if 'user' in tables:
    c.execute('PRAGMA table_info(user)')
    cols = c.fetchall()
    print("\nUser table structure:")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
conn.close()
