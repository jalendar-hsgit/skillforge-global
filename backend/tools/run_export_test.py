"""Call the app export endpoint in-process using TestClient and save the returned file (if any).
Usage: python tools/run_export_test.py <resume_id> [pdf|docx|txt]
"""
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_current_user

class DummyUser:
    def __init__(self, id):
        self.id = id

def run(resume_id: int, fmt: str = 'pdf'):
    client = TestClient(app)
    # override current user dependency to avoid auth
    client.app.dependency_overrides[get_current_user] = lambda: DummyUser(1)

    url = f"/api/v1x/resumes/{resume_id}/export?format={fmt}"
    print('Requesting', url)
    r = client.get(url)
    print('Status', r.status_code)
    if r.status_code == 200:
        content_disp = r.headers.get('content-disposition', '')
        filename = 'exported_resume.' + (fmt if fmt != 'docx' else 'docx')
        # try to parse filename
        if 'filename=' in content_disp:
            filename = content_disp.split('filename=')[-1].strip('"')
        path = os.path.join(os.getcwd(), filename)
        with open(path, 'wb') as f:
            f.write(r.content)
        print('Saved to', path)
    else:
        print('Response:', r.text)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python run_export_test.py <resume_id> [format]')
        sys.exit(1)
    rid = int(sys.argv[1])
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'pdf'
    run(rid, fmt)
