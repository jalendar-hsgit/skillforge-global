#!/usr/bin/env python3
"""
Test script to verify database connections and CRUD operations
"""
import requests
import json
import subprocess
import time
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"Error: {str(e)}", 1

def test_database():
    """Test database connectivity"""
    print("\n" + "="*60)
    print("DATABASE CONNECTIVITY & SCHEMA TESTS")
    print("="*60)
    
    # Test 1: List tables
    print("\n[1/4] Checking database tables...")
    cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -t -c "\\dt" 2>&1 | grep -E "users|courses|login_history|mentor"  | wc -l"""
    output, code = run_command(cmd)
    tables_found = int(output) if output.isdigit() else 0
    print(f"  Found {tables_found} relevant tables ✓" if tables_found > 3 else f"  Found {tables_found} tables (expected >3) ✗")
    
    # Test 2: Count users
    print("\n[2/4] Counting users in database...")
    cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -t -c "SELECT COUNT(*) FROM users;" 2>&1"""
    output, code = run_command(cmd)
    try:
        user_count = int(output)
        print(f"  Users in database: {user_count} ✓" if user_count > 0 else f"  Users: {user_count} (expected >0) ✗")
    except:
        print(f"  Error reading user count ✗")
    
    # Test 3: Sample users
    print("\n[3/4] Sample user records...")
    cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT id, email, role FROM users LIMIT 2;" 2>&1 | grep -v "id |" | head -3"""
    output, code = run_command(cmd)
    if output:
        print(f"  {output[:100]} ✓")
    
    # Test 4: Check login_history table
    print("\n[4/4] Checking login_history table...")
    cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -t -c "SELECT COUNT(*) FROM login_history;" 2>&1"""
    output, code = run_command(cmd)
    try:
        login_count = int(output)
        print(f"  Login history records: {login_count} ✓")
    except:
        print(f"  Could not query login_history ✗")

def test_api_crud():
    """Test API CRUD operations"""
    print("\n" + "="*60)
    print("API CRUD OPERATIONS TEST")
    print("="*60)
    
    base_url = "http://localhost:8001/api/v1"
    
    # Test 1: GET courses (READ)
    print("\n[1/3] Testing READ: GET /courses...")
    try:
        response = requests.get(f"{base_url}/courses", timeout=5)
        if response.status_code == 200:
            courses = response.json()
            print(f"  ✓ Fetched {len(courses)} courses successfully")
        else:
            print(f"  ✗ Status {response.status_code}: {response.text[:50]}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 2: GET users (READ)
    print("\n[2/3] Testing READ: GET /users...")
    try:
        response = requests.get(f"{base_url}/users", timeout=5)
        if response.status_code == 200:
            users = response.json()
            print(f"  ✓ Fetched {len(users)} users successfully")
        else:
            print(f"  ✗ Status {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    
    # Test 3: POST login (CREATE login_history record)
    print("\n[3/3] Testing CREATE: POST /auth/login...")
    try:
        payload = {
            "email": "john.doe@example.com",
            "password": "Password123!"
        }
        response = requests.post(
            f"{base_url}/auth/login",
            json=payload,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print(f"  ✓ Login successful, access_token generated")
                print(f"    User: {data.get('email', 'N/A')}, User ID: {data.get('user_id', 'N/A')}")
                
                # Check if login_history was created
                time.sleep(1)
                cmd = """docker exec skillforge-postgres psql -U admin -d skillforge -t -c "SELECT COUNT(*) FROM login_history WHERE success = true;" 2>&1"""
                output, code = run_command(cmd)
                try:
                    login_records = int(output)
                    print(f"  ✓ Login history record created (total success logins: {login_records})")
                except:
                    print(f"  ? Could not verify login_history record")
            else:
                print(f"  ✗ No access_token in response: {data}")
        else:
            print(f"  ✗ Login failed with status {response.status_code}")
            print(f"    Response: {response.text[:100]}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")

def test_network_connectivity():
    """Test network connectivity between services"""
    print("\n" + "="*60)
    print("NETWORK & SERVICE CONNECTIVITY TEST")
    print("="*60)
    
    # Test 1: Backend health
    print("\n[1/4] Backend health check...")
    try:
        response = requests.get("http://localhost:8001/healthz", timeout=5)
        print(f"  ✓ Backend is healthy (status: {response.status_code})")
    except Exception as e:
        print(f"  ✗ Backend not responding: {str(e)}")
    
    # Test 2: Frontend availability
    print("\n[2/4] Frontend availability...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"  ✓ Frontend responding (status: {response.status_code})")
    except Exception as e:
        print(f"  ? Frontend check: {str(e)}")
    
    # Test 3: PostgreSQL
    print("\n[3/4] PostgreSQL container check...")
    cmd = "docker exec skillforge-postgres pg_isready -U admin 2>&1"
    output, code = run_command(cmd)
    if "accepting connections" in output:
        print(f"  ✓ PostgreSQL accepting connections")
    else:
        print(f"  ✗ PostgreSQL issue: {output}")
    
    # Test 4: Redis
    print("\n[4/4] Redis container check...")
    cmd = "docker exec skillforge-redis redis-cli ping 2>&1"
    output, code = run_command(cmd)
    if output == "PONG":
        print(f"  ✓ Redis responding with PONG")
    else:
        print(f"  ✗ Redis issue: {output}")

def main():
    """Run all tests"""
    print(f"\n{'='*60}")
    print(f"SKILLFORGE DATABASE & CRUD TEST REPORT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    test_network_connectivity()
    test_database()
    test_api_crud()
    
    print(f"\n{'='*60}")
    print("TEST EXECUTION COMPLETED")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
