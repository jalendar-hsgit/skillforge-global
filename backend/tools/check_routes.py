import sys
sys.path.insert(0, r"D:\python code\sfg\skillforge-global\backend")

from app.main import app

print("All mentor routes:")
routes = [r for r in app.routes if hasattr(r, 'path') and 'mentor' in r.path.lower()]
for r in sorted(routes, key=lambda x: x.path):
    methods = r.methods if hasattr(r, 'methods') else '?'
    print(f"{methods} {r.path}")
