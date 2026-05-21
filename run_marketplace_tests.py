#!/usr/bin/env python3
"""
Marketplace Test Runner with Formatted Results
Runs all tests and produces a clean summary report
"""
import subprocess
import sys
from datetime import datetime
import json

class TestRunner:
    def __init__(self):
        self.results = {
            'backend': None,
            'integration': None,
            'timestamp': datetime.now().isoformat(),
            'passed': 0,
            'failed': 0,
            'total': 0
        }
    
    def header(self, text):
        print(f"\n{'='*70}")
        print(f"  {text}")
        print(f"{'='*70}\n")
    
    def run_test(self, script_name, test_name):
        """Run a single test script"""
        print(f"\n▶️  Running {test_name}...")
        print(f"   Command: python {script_name}")
        print(f"   {'─'*60}")
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=False,
                timeout=600  # 10 minute timeout
            )
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"❌ Test timeout after 10 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running test: {e}")
            return False
    
    def run_all(self):
        """Run all tests"""
        self.header("MARKETPLACE COMPLETE TEST SUITE")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Backend: http://localhost:8001")
        print(f"Frontend: http://localhost:3000")
        
        # Check if servers are running
        print("\n[Checking Prerequisites]")
        import requests
        
        try:
            r = requests.get("http://localhost:8001/api/v1/courses", timeout=2)
            backend_ok = r.status_code == 200
            print(f"{'✅' if backend_ok else '❌'} Backend: {'Running' if backend_ok else 'NOT RUNNING'}")
        except:
            backend_ok = False
            print("❌ Backend: NOT RUNNING")
        
        try:
            r = requests.get("http://localhost:3000", timeout=2)
            frontend_ok = r.status_code == 200
            print(f"{'✅' if frontend_ok else '❌'} Frontend: {'Running' if frontend_ok else 'NOT RUNNING'}")
        except:
            frontend_ok = False
            print("❌ Frontend: NOT RUNNING")
        
        if not (backend_ok and frontend_ok):
            print("\n⚠️  SERVERS NOT RUNNING")
            print("Please start:")
            print("  1. Backend: cd backend && uvicorn app.main:app --reload --port 8001")
            print("  2. Frontend: npm run dev")
            return False
        
        # Run tests
        print("\n" + "="*70)
        print("RUNNING TEST SUITES")
        print("="*70)
        
        # Test 1: Backend Complete
        self.header("TEST 1: MARKETPLACE COMPLETE (BACKEND)")
        test1_ok = self.run_test('test_marketplace_complete.py', 'Backend System Test')
        self.results['backend'] = test1_ok
        
        # Test 2: Integration
        self.header("TEST 2: MARKETPLACE INTEGRATION (FRONTEND + BACKEND)")
        test2_ok = self.run_test('test_marketplace_integration.py', 'Frontend Integration Test')
        self.results['integration'] = test2_ok
        
        # Print summary
        self.print_summary()
        
        return test1_ok and test2_ok
    
    def print_summary(self):
        """Print formatted summary"""
        self.header("FINAL REPORT")
        
        print(f"Test Run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Results table
        print("TEST RESULTS:")
        print("┌─────────────────────────────────────┬──────────────────┬──────────┐")
        print("│ Test Suite                          │ Status           │ Result   │")
        print("├─────────────────────────────────────┼──────────────────┼──────────┤")
        
        test_data = [
            ("Marketplace Complete (20 tests)", self.results['backend']),
            ("Integration Test (7 tests)", self.results['integration']),
        ]
        
        passed_count = sum(1 for _, r in test_data if r)
        total_count = len(test_data)
        
        for name, result in test_data:
            status = "✅ PASSED" if result else "❌ FAILED"
            result_text = "27+ tests" if result else "See output"
            print(f"│ {name:35} │ {status:16} │ {result_text:8} │")
        
        print("└─────────────────────────────────────┴──────────────────┴──────────┘")
        
        print(f"\nOVERALL PASS RATE: {passed_count}/{total_count} ({100*passed_count//total_count}%)")
        
        if passed_count == total_count:
            print("\n🎉 ALL TESTS PASSED - MARKETPLACE FULLY FUNCTIONAL!")
            status = "✅ READY FOR PRODUCTION"
        elif passed_count == 0:
            print("\n❌ ALL TESTS FAILED - CRITICAL ISSUES DETECTED")
            status = "🔴 NEEDS MAJOR FIXES"
        else:
            print(f"\n⚠️  {total_count - passed_count} test suite(s) need attention")
            status = "🟡 NEEDS REVIEW"
        
        print(f"Status: {status}")
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        
        if passed_count == total_count:
            print("✅ Marketplace is fully functional and ready to deploy")
            print("   - All features tested and working")
            print("   - Ready for production")
        else:
            print("❌ Please review failed tests and fix issues:")
            print("   1. Check console output above for failed tests")
            print("   2. Identify root causes")
            print("   3. Fix critical issues first")
            print("   4. Re-run tests after fixes")
        
        print("\n" + "="*70)
        print("DOCUMENTATION:")
        print("="*70)
        print("""
Created test files:
  - test_marketplace_complete.py (20 tests)
  - test_marketplace_integration.py (7 tests)

Documentation:
  - MARKETPLACE_FEATURES_AUDIT.md (Complete feature checklist)
  - MARKETPLACE_COMPLETE_TESTING_GUIDE.md (Detailed guide)
  - MARKETPLACE_TESTING_SUMMARY.md (Quick reference)

To run again:
  python test_marketplace_complete.py
  python test_marketplace_integration.py
  
Or use this runner:
  python run_marketplace_tests.py
""")
        
        print("="*70)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all()
    sys.exit(0 if success else 1)
