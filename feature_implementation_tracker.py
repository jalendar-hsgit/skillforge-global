#!/usr/bin/env python3
"""
Feature Implementation Tracker & Tester
Systematically implements and tests priority features
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import colorama
from colorama import Fore, Back, Style

colorama.init()

BASE_URL = "http://localhost:8001"

class FeatureTracker:
    def __init__(self):
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.session = requests.Session()
        
    def log(self, level: str, feature: str, message: str, data: Any = None):
        """Log implementation step"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "INFO": Fore.BLUE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "PROGRESS": Fore.CYAN
        }
        
        color = color_map.get(level, Fore.WHITE)
        print(f"{color}[{timestamp}] [{level:8}] {feature:<40} {message}{Style.RESET_ALL}")
        
        self.results.append({
            "timestamp": timestamp,
            "level": level,
            "feature": feature,
            "message": message,
            "data": data
        })
    
    def test_endpoint(self, feature: str, method: str, endpoint: str, expected_status: int = 200, **kwargs) -> bool:
        """Test an API endpoint"""
        try:
            url = f"{BASE_URL}{endpoint}"
            response = self.session.request(method, url, timeout=5, **kwargs)
            
            success = response.status_code == expected_status
            status_text = f"{response.status_code}"
            
            if success:
                self.log("SUCCESS", feature, f"{method} {endpoint} -> {status_text}")
            else:
                self.log("WARNING", feature, f"{method} {endpoint} -> {status_text} (expected {expected_status})")
                if response.text:
                    self.log("ERROR", feature, f"Response: {response.text[:200]}")
            
            return success, response
        except Exception as e:
            self.log("ERROR", feature, f"{method} {endpoint} failed: {str(e)}")
            return False, None
    
    def run_priority_1_tests(self):
        """Test PRIORITY 1: Critical fixes"""
        print(f"\n{Back.RED}{Fore.WHITE} PRIORITY 1: CRITICAL FIXES {Style.RESET_ALL}\n")
        
        # Test 1: Authentication
        self.log("PROGRESS", "Authentication", "Testing login endpoint...")
        success, resp = self.test_endpoint(
            "Authentication",
            "POST",
            "/api/v1/auth/login",
            expected_status=422,  # Expected to fail with validation error (no data)
        )
        
        # Test 2: Coding Practice Challenges
        self.log("PROGRESS", "Coding Practice", "Testing challenges endpoint...")
        success, resp = self.test_endpoint(
            "Coding Practice",
            "GET",
            "/api/v1x/coding-practice/challenges",
            expected_status=200
        )
        
        if success and resp:
            try:
                data = resp.json()
                count = len(data) if isinstance(data, list) else 0
                self.log("SUCCESS", "Coding Practice", f"Retrieved {count} challenges")
            except:
                self.log("WARNING", "Coding Practice", "Could not parse response as JSON")
        
        # Test 3: Missing v1x endpoints
        self.log("PROGRESS", "v1x Routes", "Testing snippets endpoint...")
        self.test_endpoint(
            "Code Snippets",
            "GET",
            "/api/v1x/code-snippets",
            expected_status=200
        )
        
        self.log("PROGRESS", "v1x Routes", "Testing learning paths endpoint...")
        self.test_endpoint(
            "Learning Paths",
            "GET",
            "/api/v1x/learning-paths",
            expected_status=200
        )
    
    def run_priority_2_tests(self):
        """Test PRIORITY 2: High priority features"""
        print(f"\n{Back.YELLOW}{Fore.WHITE} PRIORITY 2: HIGH PRIORITY FEATURES {Style.RESET_ALL}\n")
        
        # Test video progress
        self.log("PROGRESS", "Video Progress", "Testing video progress endpoint...")
        self.test_endpoint(
            "Video Progress",
            "GET",
            "/api/v1/progress",
            expected_status=401  # Expect auth error without token
        )
        
        # Test quizzes
        self.log("PROGRESS", "Quiz System", "Testing quizzes list endpoint...")
        self.test_endpoint(
            "Quiz System",
            "GET",
            "/api/v1x/quizzes",
            expected_status=200
        )
        
        # Test mentors
        self.log("PROGRESS", "Mentors", "Testing mentors list endpoint...")
        self.test_endpoint(
            "Mentor System",
            "GET",
            "/api/v1x/mentors",
            expected_status=200
        )
    
    def run_priority_3_tests(self):
        """Test PRIORITY 3: Medium priority enhancements"""
        print(f"\n{Back.CYAN}{Fore.WHITE} PRIORITY 3: MEDIUM PRIORITY ENHANCEMENTS {Style.RESET_ALL}\n")
        
        # Test resumes
        self.log("PROGRESS", "Resumes", "Testing resumes endpoint...")
        self.test_endpoint(
            "Resume Builder",
            "GET",
            "/api/v1x/resumes",
            expected_status=401  # Expect auth without token
        )
        
        # Test coins
        self.log("PROGRESS", "Gamification", "Testing coins endpoint...")
        self.test_endpoint(
            "Coin System",
            "GET",
            "/api/v1x/coins/balance",
            expected_status=401  # Expect auth without token
        )
        
        # Test admin
        self.log("PROGRESS", "Admin", "Testing admin metrics endpoint...")
        self.test_endpoint(
            "Admin Dashboard",
            "GET",
            "/api/v1x/admin/metrics",
            expected_status=401  # Expect auth without token
        )
    
    def test_health_check(self):
        """Test basic health endpoints"""
        print(f"\n{Back.GREEN}{Fore.WHITE} HEALTH CHECK {Style.RESET_ALL}\n")
        
        self.log("PROGRESS", "Health Check", "Testing healthz endpoint...")
        self.test_endpoint(
            "Health Check",
            "GET",
            "/healthz",
            expected_status=200
        )
    
    def generate_report(self):
        """Generate implementation report"""
        print(f"\n{Back.BLUE}{Fore.WHITE} IMPLEMENTATION REPORT {Style.RESET_ALL}\n")
        
        success_count = sum(1 for r in self.results if r["level"] == "SUCCESS")
        warning_count = sum(1 for r in self.results if r["level"] == "WARNING")
        error_count = sum(1 for r in self.results if r["level"] == "ERROR")
        
        print(f"Total Tests: {len(self.results)}")
        print(f"{Fore.GREEN}✓ Success: {success_count}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚠ Warning: {warning_count}{Style.RESET_ALL}")
        print(f"{Fore.RED}✗ Error: {error_count}{Style.RESET_ALL}")
        
        # Save detailed report
        report = {
            "timestamp": self.timestamp,
            "summary": {
                "total_tests": len(self.results),
                "success": success_count,
                "warning": warning_count,
                "error": error_count
            },
            "details": self.results
        }
        
        with open("feature_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to feature_test_report.json")
        
        return report


def main():
    print(f"\n{Back.MAGENTA}{Fore.WHITE} SKILLFORGE FEATURE IMPLEMENTATION TRACKER {Style.RESET_ALL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tracker = FeatureTracker()
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/healthz", timeout=2)
            if response.status_code == 200:
                print(f"{Fore.GREEN}✓ Server is ready!{Style.RESET_ALL}\n")
                break
        except:
            time.sleep(1)
            if i == 9:
                print(f"{Fore.RED}✗ Server failed to start{Style.RESET_ALL}")
                return
    
    # Run all tests
    tracker.test_health_check()
    tracker.run_priority_1_tests()
    tracker.run_priority_2_tests()
    tracker.run_priority_3_tests()
    
    # Generate report
    tracker.generate_report()
    
    print(f"\n{Fore.GREEN}✓ Feature testing complete!{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
