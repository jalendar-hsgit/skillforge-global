#!/usr/bin/env python3
"""
Test Runner for Pending Features

Orchestrates and runs all pending feature tests with formatted output.

Run: python run_pending_features_tests.py
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

class PendingFeaturesTestRunner:
    """Runs pending features test suite"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {}
        
    def header(self, title: str):
        """Print section header"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level:8} {message}")
    
    def check_prerequisites(self) -> bool:
        """Check if backend and frontend are running"""
        self.header("Checking Prerequisites")
        
        # Check backend
        self.log("Checking backend at localhost:8001...", "CHECK")
        try:
            import requests
            response = requests.get("http://localhost:8001/api/v1x/auth/health", timeout=3)
            self.log("✅ Backend is running", "OK")
            backend_ok = True
        except Exception as e:
            self.log(f"❌ Backend not running: {str(e)}", "ERROR")
            backend_ok = False
        
        # Check frontend
        self.log("Checking frontend at localhost:3000...", "CHECK")
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=3)
            self.log("✅ Frontend is running", "OK")
            frontend_ok = True
        except Exception as e:
            self.log(f"❌ Frontend not running: {str(e)}", "WARN")
            frontend_ok = False
        
        if not backend_ok:
            self.log("\n⚠️  Backend is required. Start it with:", "WARN")
            self.log("    cd backend && uvicorn app.main:app --reload --port 8001", "INFO")
            return False
        
        return True
    
    def run_test_suite(self, test_file: str, description: str) -> bool:
        """Run a test suite file"""
        self.log(f"Running {description}...", "RUN")
        self.log(f"Executing: python {test_file}", "CMD")
        
        try:
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=False,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                self.log(f"✅ {description} completed successfully", "PASS")
                self.results[test_file] = "PASS"
                return True
            else:
                self.log(f"⚠️  {description} completed with issues", "WARN")
                self.results[test_file] = "PARTIAL"
                return True  # Still return True as suite ran
        except subprocess.TimeoutExpired:
            self.log(f"❌ {description} timed out (>300s)", "ERROR")
            self.results[test_file] = "TIMEOUT"
            return False
        except Exception as e:
            self.log(f"❌ {description} failed: {str(e)}", "ERROR")
            self.results[test_file] = "ERROR"
            return False
    
    def print_summary(self):
        """Print final summary"""
        self.header("Test Execution Summary")
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        minutes = int(elapsed / 60)
        seconds = int(elapsed % 60)
        
        print(f"Execution Time: {minutes}m {seconds}s")
        print(f"\nTest Suites Run:")
        
        for test_file, status in self.results.items():
            if status == "PASS":
                symbol = "✅"
            elif status == "PARTIAL":
                symbol = "⚠️"
            elif status == "TIMEOUT":
                symbol = "⏱️"
            else:
                symbol = "❌"
            print(f"  {symbol} {test_file}: {status}")
        
        # Success criteria
        self.header("Success Criteria")
        
        print("✅ Passed: All tests executed without errors")
        print("⚠️  Partial: Some tests failed, check logs above")
        print("❌ Failed: Test suite did not run")
        
        self.header("Next Steps")
        
        print("1. Review the test output above")
        print("2. Identify which features returned 404 (not implemented)")
        print("3. Identify which features returned errors (broken)")
        print("4. Prioritize implementation based on importance")
        print("\nPending Feature Categories:")
        print("  - Search & Filtering (CRITICAL)")
        print("  - Wishlist (HIGH)")
        print("  - Reviews & Ratings (HIGH)")
        print("  - Recommendations (MEDIUM)")
        print("  - Coupons & Discounts (MEDIUM)")
        print("  - Seller Analytics (HIGH)")
        print("  - Order Management (HIGH)")
        print("  - Admin Financial (MEDIUM)")
        print("  - Notifications (LOW)")
        
        self.header("Quick Reference")
        
        print("Re-run individual test:")
        print("  python test_pending_features_e2e.py")
        print("\nRe-run all tests:")
        print("  python run_pending_features_tests.py")
        print("\nFrontend + Backend integration:")
        print("  python test_marketplace_integration.py")
    
    def run(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("  PENDING FEATURES TEST SUITE RUNNER")
        print("  Comprehensive end-to-end testing")
        print("="*70)
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.log("\n⚠️  Cannot proceed without backend", "ERROR")
            sys.exit(1)
        
        # Run test suites
        self.header("Running Test Suites")
        
        self.run_test_suite(
            "test_pending_features_e2e.py",
            "Pending Features E2E Tests"
        )
        
        # Print summary
        self.print_summary()
        
        self.header("Test Run Complete")
        print("Review the output above to understand what's working and what needs to be built.")


if __name__ == "__main__":
    try:
        runner = PendingFeaturesTestRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test runner interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        sys.exit(1)
