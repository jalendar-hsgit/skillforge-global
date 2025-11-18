"""
Navigation and Performance Test Suite for SkillForge Demo
Tests critical user flows and measures page load times
"""
import requests
import time
import json

BASE = "http://localhost:3000"
BACKEND = "http://127.0.0.1:8001"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_test(name, passed, duration_ms=None, details=""):
    status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
    duration_str = f"({duration_ms:.0f}ms)" if duration_ms else ""
    print(f"  {status} | {name:45} {duration_str}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.END}")

def test_navigation_flow():
    """Test critical navigation paths"""
    print_header("NAVIGATION FLOW TESTS")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'timings': {}
    }
    
    # Test 1: Homepage loads
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(BASE, timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
            results['timings']['Homepage'] = duration
        else:
            results['failed'] += 1
        print_test("Homepage loads", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Homepage loads", False, details=str(e))
    
    # Test 2: Login page loads
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/login", timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
            results['timings']['Login Page'] = duration
        else:
            results['failed'] += 1
        print_test("Login page loads", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Login page loads", False, details=str(e))
    
    # Test 3: Dashboard (auth required - should redirect)
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/dashboard", timeout=10, allow_redirects=False)
        duration = (time.time() - start) * 1000
        # Should either load (200) or redirect to login (302/307)
        passed = r.status_code in [200, 302, 307, 308]
        if passed:
            results['passed'] += 1
            results['timings']['Dashboard'] = duration
        else:
            results['failed'] += 1
        print_test("Dashboard route exists", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Dashboard route exists", False, details=str(e))
    
    # Test 4: Pricing page
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/pricing", timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
            results['timings']['Pricing'] = duration
        else:
            results['failed'] += 1
        print_test("Pricing page loads", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Pricing page loads", False, details=str(e))
    
    return results

def test_api_health():
    """Test backend API health"""
    print_header("API HEALTH TESTS")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
    
    # Test 1: Backend health endpoint
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BACKEND}/healthz", timeout=5)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
        else:
            results['failed'] += 1
        print_test("Backend health check", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Backend health check", False, details=str(e))
    
    # Test 2: Frontend API proxy (me endpoint - should be 401 without auth)
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/api/session/me", timeout=5)
        duration = (time.time() - start) * 1000
        # Expect 401 without auth, which means the route exists
        passed = r.status_code in [401, 200]
        if passed:
            results['passed'] += 1
        else:
            results['failed'] += 1
        print_test("Frontend API proxy responds", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Frontend API proxy responds", False, details=str(e))
    
    return results

def test_authenticated_flow():
    """Test resume flow with authentication"""
    print_header("AUTHENTICATED FLOW TESTS")
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'timings': {}
    }
    
    # Signup
    results['total'] += 1
    start = time.time()
    try:
        email = f"perf_test_{int(time.time())}@example.com"
        signup_data = {
            "email": email,
            "password": "TestPass123!",
            "full_name": "Performance Test User"
        }
        r = requests.post(f"{BASE}/api/session/signup", json=signup_data, timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code in [200, 429]  # 429 = rate limited (still working)
        if passed:
            results['passed'] += 1
            results['timings']['Signup'] = duration
        else:
            results['failed'] += 1
        print_test("User signup", passed, duration, f"Status: {r.status_code}")
        
        if r.status_code == 429:
            print(f"       {Colors.YELLOW}Note: Rate limited - using existing test user{Colors.END}")
            email = "test_1763188156@example.com"
    except Exception as e:
        results['failed'] += 1
        print_test("User signup", False, details=str(e))
        return results
    
    # Login
    results['total'] += 1
    start = time.time()
    try:
        login_data = {"email": email, "password": "TestPass123!"}
        r = requests.post(f"{BASE}/api/session/login", json=login_data, timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
            results['timings']['Login'] = duration
            cookies = r.cookies
        else:
            results['failed'] += 1
            cookies = None
        print_test("User login", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("User login", False, details=str(e))
        return results
    
    if not cookies:
        print(f"  {Colors.YELLOW}Skipping remaining tests - no auth cookie{Colors.END}")
        return results
    
    # Create resume
    results['total'] += 1
    start = time.time()
    try:
        resume_data = {
            "title": "Performance Test Resume",
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "123-456-7890",
            "summary": "Test resume for performance validation"
        }
        r = requests.post(f"{BASE}/api/session/resumes", json=resume_data, cookies=cookies, timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 201
        if passed:
            results['passed'] += 1
            results['timings']['Create Resume'] = duration
            resume_id = r.json().get('id')
        else:
            results['failed'] += 1
            resume_id = None
        print_test("Create resume", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Create resume", False, details=str(e))
        return results
    
    if not resume_id:
        print(f"  {Colors.YELLOW}Skipping export tests - no resume ID{Colors.END}")
        return results
    
    # Update resume
    results['total'] += 1
    start = time.time()
    try:
        update_data = {"title": "Updated Performance Test Resume"}
        r = requests.patch(f"{BASE}/api/session/resumes?id={resume_id}", json=update_data, cookies=cookies, timeout=10)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200
        if passed:
            results['passed'] += 1
            results['timings']['Update Resume'] = duration
        else:
            results['failed'] += 1
        print_test("Update resume", passed, duration, f"Status: {r.status_code}")
    except Exception as e:
        results['failed'] += 1
        print_test("Update resume", False, details=str(e))
    
    # Export PDF
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/api/session/v1x/resumes/{resume_id}/export?format=pdf", cookies=cookies, timeout=15)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200 and len(r.content) > 100
        if passed:
            results['passed'] += 1
            results['timings']['Export PDF'] = duration
        else:
            results['failed'] += 1
        print_test("Export PDF", passed, duration, f"Status: {r.status_code}, Size: {len(r.content)} bytes")
    except Exception as e:
        results['failed'] += 1
        print_test("Export PDF", False, details=str(e))
    
    # Export DOCX
    results['total'] += 1
    start = time.time()
    try:
        r = requests.get(f"{BASE}/api/session/v1x/resumes/{resume_id}/export?format=docx", cookies=cookies, timeout=15)
        duration = (time.time() - start) * 1000
        passed = r.status_code == 200 and len(r.content) > 100
        if passed:
            results['passed'] += 1
            results['timings']['Export DOCX'] = duration
        else:
            results['failed'] += 1
        print_test("Export DOCX", passed, duration, f"Status: {r.status_code}, Size: {len(r.content)} bytes")
    except Exception as e:
        results['failed'] += 1
        print_test("Export DOCX", False, details=str(e))
    
    return results

def print_performance_summary(all_results):
    """Print performance metrics summary"""
    print_header("PERFORMANCE SUMMARY")
    
    all_timings = {}
    for result_set in all_results:
        if 'timings' in result_set:
            all_timings.update(result_set['timings'])
    
    if all_timings:
        print(f"  {Colors.BOLD}Response Time Metrics:{Colors.END}")
        for name, duration in sorted(all_timings.items(), key=lambda x: x[1]):
            color = Colors.GREEN if duration < 500 else Colors.YELLOW if duration < 1500 else Colors.RED
            print(f"    {name:30} {color}{duration:7.0f}ms{Colors.END}")
        
        avg_time = sum(all_timings.values()) / len(all_timings)
        print(f"\n  {Colors.BOLD}Average Response Time: {Colors.BLUE}{avg_time:.0f}ms{Colors.END}")
    
    total_tests = sum(r.get('total', 0) for r in all_results)
    total_passed = sum(r.get('passed', 0) for r in all_results)
    total_failed = sum(r.get('failed', 0) for r in all_results)
    
    print(f"\n  {Colors.BOLD}Overall Results:{Colors.END}")
    print(f"    Total Tests:  {total_tests}")
    print(f"    {Colors.GREEN}Passed:       {total_passed}{Colors.END}")
    print(f"    {Colors.RED}Failed:       {total_failed}{Colors.END}")
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    color = Colors.GREEN if success_rate >= 90 else Colors.YELLOW if success_rate >= 70 else Colors.RED
    print(f"    Success Rate: {color}{success_rate:.1f}%{Colors.END}")

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║     SKILLFORGE NAVIGATION & PERFORMANCE TEST SUITE                 ║")
    print("║                    Demo Readiness Check                            ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    all_results = []
    
    try:
        # Run all test suites
        nav_results = test_navigation_flow()
        all_results.append(nav_results)
        
        api_results = test_api_health()
        all_results.append(api_results)
        
        auth_results = test_authenticated_flow()
        all_results.append(auth_results)
        
        # Print summary
        print_performance_summary(all_results)
        
        # Final verdict
        total_passed = sum(r.get('passed', 0) for r in all_results)
        total_tests = sum(r.get('total', 0) for r in all_results)
        
        print(f"\n{Colors.BOLD}")
        if total_passed == total_tests:
            print(f"{Colors.GREEN}✓ ALL TESTS PASSED - DEMO READY!{Colors.END}")
        elif total_passed / total_tests >= 0.9:
            print(f"{Colors.YELLOW}⚠ MOSTLY READY - {total_tests - total_passed} issues to review{Colors.END}")
        else:
            print(f"{Colors.RED}✗ CRITICAL ISSUES - {total_tests - total_passed} failures detected{Colors.END}")
        print(f"{Colors.END}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {e}{Colors.END}\n")

if __name__ == "__main__":
    main()
