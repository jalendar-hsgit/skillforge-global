import requests
import time

BASE = "http://127.0.0.1:8001"

# read simple cookies file at backend/cookies.txt (name=value per-line)
cookies = {}
try:
    with open('backend/cookies.txt') as f:
        for line in f:
            line=line.strip()
            if '=' in line:
                k,v = line.split('=',1)
                cookies[k]=v
except Exception as e:
    print('no cookies file:', e)

# get token
token = cookies.get('token')
if token:
    print('got token (len):', len(token))
else:
    print('no token, proceeding without auth')


def show(r):
    print(r.request.method, r.url)
    print('Status:', r.status_code)
    print('Response:', r.text)
    print('-'*60)

# auth/me using cookie
r = requests.get(f"{BASE}/api/v1/auth/me", cookies=cookies)
show(r)

# courses list
r = requests.get(f"{BASE}/api/v1/courses")
show(r)

# coins balance
r = requests.get(f"{BASE}/api/v1x/coins_db/balance", cookies=cookies)
show(r)

# add coins
r = requests.post(f"{BASE}/api/v1x/coins_db/add", json={"amount":5}, cookies=cookies)
show(r)

# coins balance again
r = requests.get(f"{BASE}/api/v1x/coins_db/balance", cookies=cookies)
show(r)

# progress GET (requires Authorization Bearer)
headers = {}
if token:
    headers['Authorization'] = 'Bearer ' + token
r = requests.get(f"{BASE}/api/v1/progress?path=python-ai", headers=headers)
show(r)

# mark progress
r = requests.post(f"{BASE}/api/v1/progress?path=python-ai&module_id=mod1", headers=headers)
show(r)

# progress GET again
r = requests.get(f"{BASE}/api/v1/progress?path=python-ai", headers=headers)
show(r)

# youtube health
r = requests.get(f"{BASE}/api/v1x/youtube/health")
show(r)

print('done')
