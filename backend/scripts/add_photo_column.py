import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parents[1] / 'app' / 'data' / 'skillforge.db'
print('DB path:', db_path)
conn = sqlite3.connect(str(db_path), timeout=5)
try:
    c = conn.cursor()
    c.execute("PRAGMA table_info(resumes)")
    cols = [r[1] for r in c.fetchall()]
    print('COLUMNS:', cols)
    if 'photo_url' not in cols:
        print('Adding photo_url column')
        c.execute('ALTER TABLE resumes ADD COLUMN photo_url TEXT')
        conn.commit()
        print('photo_url added')
    else:
        print('photo_url already present')
except Exception as e:
    print('ERROR:', e)
finally:
    conn.close()
