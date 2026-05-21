from app.core.db import SessionLocal
from app.modelsx.coding_practice import CodingChallenge

db = SessionLocal()
count = db.query(CodingChallenge).count()
print(f'✅ Total challenges in database: {count}')

if count > 0:
    challenges = db.query(CodingChallenge).limit(10).all()
    for c in challenges:
        print(f'  - {c.title} ({c.difficulty}, {c.points} pts, {c.category})')
else:
    print('❌ No challenges found')

db.close()
