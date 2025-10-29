import json, os, sys
DATA = [
    {"id":"py-003","path":"python-ai","title":"Pandas Tutorial","youtubeId":"vmEHCJofslg","duration":"1h"},
    {"id":"fs-002","path":"fullstack","title":"Node.js Crash Course","youtubeId":"fBNz5xF-Kx4","duration":"1h"},
]
base = os.path.dirname(__file__)
p = os.path.join(base, "app", "data", "courses.json")
with open(p, "r", encoding="utf-8") as f:
    items = json.load(f)
# add new ones if not exists
existing = {x["id"] for x in items}
for it in DATA:
    if it["id"] not in existing:
        items.append(it)
with open(p, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
print(f"Seeded {len(DATA)} items into {p}")
