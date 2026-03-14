#!/usr/bin/env python3
"""
Diagnostic script to test backend API endpoints
"""
import sys
import subprocess
import json
import time

def run_command(cmd, description):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"\nOK {description}")
        print(f"  Status: {result.returncode}")
        if result.stdout:
            print(f"  Output:\n{result.stdout[:500]}")
        if result.stderr and result.returncode != 0:
            print(f"  Error:\n{result.stderr[:500]}")
        return result.stdout
    except Exception as e:
        print(f"\nFAIL {description}")
        print(f"  Error: {e}")
        return None

def test_container_imports():
    """Test if Python imports work in backend container"""
    cmd = """docker exec skillforge-backend python3 << 'EOF'
try:
    from app.api.v1x.mentors import router as mentors_router
    print(f"OK Mentors router loaded")
    print(f"  Routes count: {len(mentors_router.routes) if hasattr(mentors_router, 'routes') else 'N/A'}")
except ImportError as e:
    print(f"FAIL Import error: {e}")
except Exception as e:
    print(f"FAIL Error: {e}")
    import traceback
    traceback.print_exc()
EOF
"""
    return run_command(cmd, "Testing mentors module import in backend")

def test_api_endpoints():
    """Test if API endpoints are returning data"""
    endpoints = [
        ('http://localhost:8001/healthz', 'Health Check'),
        ('http://localhost:8001/api/v1/courses', 'Courses (v1)'),
        ('http://localhost:8001/api/v1x/mentors', 'Mentors (v1x)'),
        ('http://localhost:8001/api/v1/users', 'Users Endpoint'),
    ]
    
    for url, desc in endpoints:
        # Using PowerShell version of curl check
        cmd = f'powershell -Command "(Invoke-WebRequest -Uri {url} -UseBasicParsing -TimeoutSec 5).StatusCode"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status = result.stdout.strip()
                print(f"OK {desc}: {status}")
            else:
                print(f"FAIL {desc}: Failed")
                if result.stderr:
                    print(f"    {result.stderr[:100]}")
        except Exception as e:
            print(f"FAIL {desc}: {e}")

def test_database():
    """Test database connectivity"""
    cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT COUNT(*) FROM courses;" 2>&1"""
    run_command(cmd, "Database courses count")

def main():
    print("=" * 60)
    print("SKILLFORGE BACKEND DIAGNOSTICS")
    print("=" * 60)
    
    # Wait a bit for containers to fully start
    print("\nWaiting 5 seconds for containers to stabilize...")
    time.sleep(5)
    
    # Test container status
    print("\n[1] Checking Container Status...")
    run_command("docker ps --filter 'name=skillforge' --format '{{.Names}}\\t{{.Status}}'", "Container status")
    
    # Test imports
    print("\n[2] Testing Module Imports...")
    test_container_imports()
    
    # Test database
    print("\n[3] Testing Database...")
    test_database()
    
    # Test endpoints
    print("\n[4] Testing API Endpoints...")
    test_api_endpoints() 
    
    print("\n" + "=" * 60)
    print("DIAGNOSTICS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
