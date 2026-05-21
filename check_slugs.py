import sqlite3

conn = sqlite3.connect('backend/app/data/skillforge.db')
cursor = conn.cursor()

# Get all challenges
cursor.execute('SELECT id, title, slug, difficulty FROM coding_challenges ORDER BY id LIMIT 15')
rows = cursor.fetchall()

print(f"{'ID':3} {'Title':30} {'Slug':30} {'Difficulty':10}")
print("=" * 75)
for row in rows:
    print(f"{row[0]:<3} {row[1]:<30} {row[2]:<30} {row[3]:<10}")

# Check for duplicate slugs
cursor.execute('SELECT slug, COUNT(*) FROM coding_challenges GROUP BY slug HAVING COUNT(*) > 1')
dups = cursor.fetchall()
if dups:
    print("\nDUPLICATE SLUGS FOUND:")
    for slug, count in dups:
        print(f"  {slug}: {count} challenges")
else:
    print("\nAll slugs are unique ✓")

conn.close()
