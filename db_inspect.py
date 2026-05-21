import sqlite3
p='backend/app/data/skillforge.db'
conn=sqlite3.connect(p)
cur=conn.cursor()
print('tables:', [t[0] for t in cur.execute("select name from sqlite_master where type='table'").fetchall()])
for t in ['progress','coin_ledger','user']:
    try:
        rows=cur.execute(f'select * from {t} limit 5').fetchall()
        print(f'{t} rows:', rows)
    except Exception as e:
        print(f'{t} error:', e)
conn.close()
