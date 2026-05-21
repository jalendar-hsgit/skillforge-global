"""Sanity check using urllib (no external deps).
Writes results to sanity_results_py.txt
"""
import http.cookiejar, urllib.request, urllib.parse, json, os, sys

OUT = 'sanity_results_py.txt'
if os.path.exists(OUT):
    os.remove(OUT)

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

base = 'http://127.0.0.1:8001'

def write(s):
    with open(OUT,'a',encoding='utf-8') as f:
        f.write(s+"\n")
    print(s)

write('Sanity check started')
# login
login_url = base + '/api/v1/auth/login'
login_data = json.dumps({'email':'superadmin@skillforge.com','password':'super123'}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={'Content-Type':'application/json'})
try:
    resp = opener.open(req, timeout=10)
    body = resp.read().decode('utf-8')
    write('LOGIN: OK')
    try:
        j = json.loads(body)
        write('LOGIN JSON: '+ json.dumps(j))
    except:
        write('LOGIN: non-json response')
except Exception as e:
    write('LOGIN FAILED: '+repr(e))
    sys.exit(1)

endpoints = [
  '/api/v1/auth/me',
  '/api/v1/courses',
  '/api/v1x/courses-db',
  '/api/quizzes/list',
  '/api/v1x/quizzes-db',
  '/api/v1x/coins_db/balance',
  '/api/v1x/mentors/all',
  '/api/v1x/mentor-portal/sessions',
  '/api/v1x/subscriptions/plans',
  '/api/session/resumes',
  '/api/v1x/job-applications',
  '/api/v1x/cover-letters',
  '/api/v1x/marketplace/courses',
  '/api/v1x/youtube-sync/status',
  '/api/v1x/chat/files',
  '/api/v1x/student-dashboard/stats',
  '/api/v1x/admin/users',
  '/api/v1x/admin/notifications/templates',
  '/api/v1x/admin/analytics'
]

for ep in endpoints:
    url = base + ep
    write('\nCALL: '+url)
    try:
        r = opener.open(url, timeout=10)
        status = r.getcode()
        content = r.read()
        write('  STATUS: '+str(status)+' LEN:'+str(len(content)))
        # try JSON
        try:
            j = json.loads(content.decode('utf-8'))
            if isinstance(j, list):
                write('  JSON: array count='+str(len(j)))
            elif isinstance(j, dict):
                write('  JSON keys: '+', '.join(list(j.keys())[:10]))
            else:
                write('  JSON type: '+str(type(j)))
        except Exception:
            write('  (not json)')
    except Exception as e:
        write('  ERROR: '+repr(e))

write('\nSanity check finished')
print('\nResults written to', OUT)
