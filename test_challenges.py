import requests

r = requests.get('http://localhost:8001/api/v1x/coding-practice/challenges?limit=15')
data = r.json()
print(f'API returned {len(data)} challenges:')
for item in data[:5]:
    print(f'  - {item["title"]} ({item["difficulty"]})')
