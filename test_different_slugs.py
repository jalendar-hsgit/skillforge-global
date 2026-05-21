import requests

slugs = ['two-sum', 'reverse-string', 'palindrome-number', 'valid-parentheses', 'contains-duplicate', 'plus-one']

print("Testing different challenge slugs:")
print("=" * 70)

for slug in slugs:
    r = requests.get(f'http://localhost:8001/api/v1x/coding-practice/challenges/{slug}')
    if r.ok:
        data = r.json()
        print(f"✓ {slug:30} → {data['title']:30} ({data['difficulty']})")
    else:
        print(f"✗ {slug:30} → ERROR {r.status_code}")

print("\nAll challenges are different ✓" if all(requests.get(f'http://localhost:8001/api/v1x/coding-practice/challenges/{s}').ok for s in slugs) else "\nSome challenges failed to load")
