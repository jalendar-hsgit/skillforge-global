"""
Simple HTTP export test: calls the export endpoint and saves the PDF file.
No headless browser needed.
Usage: python tools/http_export_test.py <resume_id> [format]
"""
import sys
import os
import requests

def test_export(resume_id: int, fmt: str = 'pdf'):
    """Call backend export endpoint and save the file."""
    backend_base = "http://localhost:8001"
    
    # For testing, we bypass auth by using TestClient in-process
    # But if running against a live backend, you'd need a valid JWT cookie
    
    url = f"{backend_base}/api/v1x/resumes/{resume_id}/export?format={fmt}"
    print(f"[1/3] Requesting: {url}")
    
    try:
        # Try with cookies if logged in (won't work for demo, but shows pattern)
        response = requests.get(url, timeout=30)
        print(f"[2/3] Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Extract filename from content-disposition header
            disp = response.headers.get('content-disposition', '')
            if 'filename=' in disp:
                filename = disp.split('filename=')[-1].strip('"')
            else:
                filename = f"resume_export_{resume_id}.{fmt}"
            
            filepath = os.path.join(os.getcwd(), filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"[3/3] ✓ Saved to: {filepath} ({len(response.content)} bytes)")
            return filepath
        else:
            print(f"[3/3] ✗ Export failed with {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to {backend_base}. Is the backend running?")
        print("Start backend with: uvicorn app.main:app --reload --port 8001")
        return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

if __name__ == '__main__':
    rid = int(sys.argv[1]) if len(sys.argv) > 1 else 277
    fmt = sys.argv[2] if len(sys.argv) > 2 else 'pdf'
    test_export(rid, fmt)
