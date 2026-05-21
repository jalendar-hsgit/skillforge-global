"""Comprehensive backend test - check DB tables and test endpoints"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text
from app.core.db import engine, get_db
import requests
from datetime import datetime

def check_database():
    """Check database tables and row counts"""
    print("=" * 70)
    print("DATABASE INSPECTION")
    print("=" * 70)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\nTotal tables in database: {len(tables)}\n")
    
    # Get row counts for each table
    with engine.connect() as conn:
        tables_with_data = []
        empty_tables = []
        
        for table in sorted(tables):
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                if count > 0:
                    tables_with_data.append((table, count))
                else:
                    empty_tables.append(table)
            except Exception as e:
                print(f"  [!] Error checking {table}: {e}")
        
        print("TABLES WITH DATA:")
        print("-" * 70)
        for table, count in tables_with_data:
            print(f"  [*] {table:<40} {count:>6} rows")
        
        print(f"\n\nEMPTY TABLES ({len(empty_tables)}):")
        print("-" * 70)
        for table in empty_tables:
            print(f"  [ ] {table}")
        
        print(f"\n\nSUMMARY:")
        print("-" * 70)
        print(f"  Tables with data: {len(tables_with_data)}")
        print(f"  Empty tables: {len(empty_tables)}")
        print(f"  Total tables: {len(tables)}")

def test_backend_endpoints():
    """Test key backend endpoints"""
    print("\n\n" + "=" * 70)
    print("BACKEND API TESTS")
    print("=" * 70)
    
    base_url = "http://localhost:8001"
    
    endpoints = [
        ("GET", "/healthz", "Health Check"),
        ("GET", "/api/v1/paths", "Learning Paths"),
        ("GET", "/api/v1/courses", "Courses List"),
        ("GET", "/api/v1x/coding-practice/challenges", "Coding Challenges"),
        ("GET", "/api/v1x/snippets", "Code Snippets"),
    ]
    
    print("\nTesting endpoints...\n")
    
    results = []
    for method, endpoint, name in endpoints:
        try:
            url = base_url + endpoint
            response = requests.get(url, timeout=5)
            status = "[PASS]" if response.status_code == 200 else f"[FAIL] ({response.status_code})"
            results.append((status, name, endpoint, response.status_code))
            
            # Show response sample if successful
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        info = f"{len(data)} items"
                    elif isinstance(data, dict):
                        info = f"{len(data)} keys"
                    else:
                        info = str(type(data).__name__)
                    print(f"{status} {name:<30} -> {info}")
                except:
                    print(f"{status} {name:<30} -> {len(response.content)} bytes")
            else:
                print(f"{status} {name:<30} -> Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"[CONN] {name:<30} -> Backend not running!")
            results.append(("[CONN]", name, endpoint, "N/A"))
        except Exception as e:
            print(f"[ERROR] {name:<30} -> {e}")
            results.append(("[ERROR]", name, endpoint, str(e)))
    
    print("\n\nSUMMARY:")
    print("-" * 70)
    passed = sum(1 for r in results if r[0] == "[PASS]")
    failed = len(results) - passed
    print(f"  Passed: {passed}/{len(results)}")
    print(f"  Failed: {failed}/{len(results)}")

if __name__ == "__main__":
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        check_database()
    except Exception as e:
        print(f"\n[ERROR] Database check failed: {e}")
    
    try:
        test_backend_endpoints()
    except Exception as e:
        print(f"\n[ERROR] API tests failed: {e}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
