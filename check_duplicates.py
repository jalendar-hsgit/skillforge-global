import sqlite3
from collections import Counter

conn = sqlite3.connect('backend/app/data/skillforge.db')
cursor = conn.cursor()

# Get all slugs
cursor.execute('SELECT slug, title, difficulty FROM coding_challenges ORDER BY id')
rows = cursor.fetchall()

# Count slugs
slugs = [row[0] for row in rows]
slug_counts = Counter(slugs)

print(f"Total challenges: {len(rows)}")
print(f"Unique slugs: {len(slug_counts)}")
print()

# Show first 10
print("First 10 challenges:")
print(f"{'ID':3} {'Slug':30} {'Title':30} {'Difficulty':10}")
print("-" * 75)
for i, (slug, title, difficulty) in enumerate(rows[:10], 1):
    print(f"{i:<3} {slug:30} {title:30} {difficulty:10}")

# Check for duplicates
duplicates = {slug: count for slug, count in slug_counts.items() if count > 1}
if duplicates:
    print(f"\n⚠️ FOUND DUPLICATES:")
    for slug, count in duplicates.items():
        print(f"  {slug}: appears {count} times")
else:
    print(f"\n✓ All {len(slug_counts)} slugs are unique!")

conn.close()
