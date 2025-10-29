import json, os
base = os.path.dirname(__file__)
p = os.path.join(base, "app", "data", "courses.json")
with open(p, "r", encoding="utf-8") as f:
    items = json.load(f)
existing = {x["id"] for x in items}

NEW = [
  # Python & AI
  {"id": "py-010", "path":"python-ai", "title":"Python OOP Crash Course", "youtubeId":"JeznW_7DlB0", "duration":"1h"},
  {"id": "py-011", "path":"python-ai", "title":"scikit-learn Tutorial", "youtubeId":"0Lt9w-BxKFQ", "duration":"2h"},
  {"id": "py-012", "path":"python-ai", "title":"Matplotlib & Seaborn", "youtubeId":"wB9C0Mz9gSo", "duration":"1h"},
  # Fullstack
  {"id": "fs-010", "path":"fullstack", "title":"Node + Express REST API", "youtubeId":"Oe421EPjeBE", "duration":"2h"},
  {"id": "fs-011", "path":"fullstack", "title":"JWT Auth Explained", "youtubeId":"mbsmsi7l3r4", "duration":"25m"},
  {"id": "fs-012", "path":"fullstack", "title":"Next.js Basics", "youtubeId":"A63UxsQsEbU", "duration":"1h"},
  # AWS / DevOps
  {"id": "aws-010", "path":"aws-devops", "title":"Docker in 100 Seconds", "youtubeId":"Gjnup-PuquQ", "duration":"7m"},
  {"id": "aws-011", "path":"aws-devops", "title":"CI/CD with GitHub Actions", "youtubeId":"R8_veQiYBjI", "duration":"1h"},
  {"id": "aws-012", "path":"aws-devops", "title":"Kubernetes Crash Course", "youtubeId":"X48VuDVv0do", "duration":"45m"},
  # Cybersecurity
  {"id": "sec-010", "path":"cybersec", "title":"OWASP Top 10 Overview", "youtubeId":"E6ZTZ2ZSlm8", "duration":"30m"},
  {"id": "sec-011", "path":"cybersec", "title":"Burp Suite Basics", "youtubeId":"u7nP01ZrF2o", "duration":"40m"},
  {"id": "sec-012", "path":"cybersec", "title":"Network Security Basics", "youtubeId":"qWcGgRFRAPM", "duration":"50m"},
  # Flutter
  {"id": "fl-010", "path":"flutter", "title":"Flutter in 100 Seconds", "youtubeId":"PDVn8xjFzCI", "duration":"2m"},
  {"id": "fl-011", "path":"flutter", "title":"Flutter Widgets 101", "youtubeId":"x0uinJvhNxI", "duration":"1h"},
  {"id": "fl-012", "path":"flutter", "title":"State Management Overview", "youtubeId":"d_m5csmrf7I", "duration":"35m"}
]

for it in NEW:
    if it["id"] not in existing:
        items.append(it)

with open(p, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Added up to {len(NEW)} items. Total now: {len(items)}")
