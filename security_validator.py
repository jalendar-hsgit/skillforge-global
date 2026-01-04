#!/usr/bin/env python3
"""
Production Security Validator - Check all protected pages for security best practices
Usage: python security_validator.py
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class SecurityValidator:
    """Validates frontend pages for production security compliance"""
    
    # Security checks (file must contain these)
    REQUIRED_CHECKS = {
        'useProtectedPage': 'import.*useProtectedPage|from.*useProtectedPage',
        'LoadingSpinner': 'import.*LoadingSpinner|from.*LoadingSpinner',
        'loading_check': 'if\\s*\\(\\s*loading\\s*\\)',
        'user_check': 'if\\s*\\(!user\\)|if\\s*\\(!me\\)',
        'useRouter': 'useRouter|useRouter()',
        'error_handling': 'error.*\\?|catch\\s*\\(|error_state',
    }
    
    # Security warnings (should contain these)
    RECOMMENDED_CHECKS = {
        'useEffect': 'useEffect',
        'async_auth': 'async|await',
        'auth_headers': 'Authorization|Bearer',
        'token_validation': 'token|verify',
    }
    
    # Pages that should be protected
    PROTECTED_PAGES = {
        # Dashboard & Core
        '/dashboard': 'dashboard/index.tsx',
        '/dashboard-analytics': 'dashboard-analytics.tsx',
        '/customize-dashboard': 'customize-dashboard.tsx',
        '/feed': 'feed.tsx',
        
        # Profile
        '/profile': 'profile/index.tsx',
        '/profile/edit': 'profile/edit.tsx',
        '/profile/settings': 'profile/settings.tsx',
        
        # Mentorship
        '/mentors/settings': 'mentors/settings.tsx',
        '/mentors/my-sessions': 'mentors/my-sessions.tsx',
        '/mentors/earnings': 'mentors/earnings.tsx',
        '/mentors/dashboard': 'mentors/dashboard/index.tsx',
        '/mentors/dashboard/profile': 'mentors/dashboard/profile.tsx',
        '/mentors/dashboard/sessions': 'mentors/dashboard/sessions.tsx',
        '/mentors/dashboard/students': 'mentors/dashboard/students.tsx',
        '/mentors/dashboard/earnings': 'mentors/dashboard/earnings.tsx',
        '/mentors/dashboard/payouts': 'mentors/dashboard/payouts.tsx',
        '/mentors/dashboard/analytics': 'mentors/dashboard/analytics.tsx',
        '/mentors/dashboard/reviews': 'mentors/dashboard/reviews.tsx',
        '/mentors/dashboard/verification': 'mentors/dashboard/verification.tsx',
        
        # Practice
        '/practice/submissions': 'practice/submissions.tsx',
        '/ai-hints': 'ai-hints.tsx',
        '/hint-preferences': 'hint-preferences.tsx',
        
        # Resumes
        '/resumes': 'resumes/index.tsx',
        '/resumes/new': 'resumes/new.tsx',
        '/resumes/templates': 'resumes/templates.tsx',
        '/resumes/compare': 'resumes/compare.tsx',
        '/resumes/import': 'resumes/import.tsx',
        '/resumes/diagnostics': 'resumes/diagnostics.tsx',
        
        # Job Tracking
        '/jobs': 'jobs/index.tsx',
        '/job-tracker/add': 'job-tracker/add.tsx',
        '/job-tracker/analytics': 'job-tracker/analytics.tsx',
        
        # Marketplace
        '/marketplace/cart': 'marketplace/cart.tsx',
        '/marketplace/orders': 'marketplace/orders.tsx',
        '/marketplace/seller': 'marketplace/seller/index.tsx',
        '/marketplace/seller/create-product': 'marketplace/seller/create-product.tsx',
        '/marketplace/seller/products': 'marketplace/seller/products.tsx',
        '/marketplace/seller/orders': 'marketplace/seller/orders.tsx',
        '/marketplace/seller/analytics': 'marketplace/seller/analytics.tsx',
        
        # Community/Social
        '/messages': 'messages/index.tsx',
        '/notifications': 'notifications/index.tsx',
        '/social': 'social/index.tsx',
        '/social/feed': 'social/feed/index.tsx',
        '/social/following': 'social/following.tsx',
        
        # Settings
        '/security': 'security.tsx',
        '/pwa-settings': 'pwa-settings.tsx',
        
        # Admin
        '/admin': 'admin/index.tsx',
        
        # Other Protected
        '/coins': 'coins.tsx',
        '/referral_program': 'referral_program.tsx',
        '/recommendations': 'recommendations.tsx',
        '/teams': 'teams.tsx',
        '/github-integration': 'github-integration.tsx',
        '/ai': 'ai.tsx',
    }

    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.src_path = self.root_path / 'src' / 'pages'
        self.results = {
            'compliant': [],
            'warnings': [],
            'errors': [],
            'missing': [],
        }

    def check_file(self, file_path: Path) -> Tuple[str, List[str], List[str]]:
        """Check a single file for security compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return 'error', [str(e)], []

        missing = []
        warnings = []

        # Check required items
        for check_name, pattern in self.REQUIRED_CHECKS.items():
            if not re.search(pattern, content, re.IGNORECASE):
                missing.append(check_name)

        # Check recommended items
        for check_name, pattern in self.RECOMMENDED_CHECKS.items():
            if not re.search(pattern, content, re.IGNORECASE):
                warnings.append(check_name)

        # Determine status
        if missing:
            status = 'error'
        elif warnings:
            status = 'warning'
        else:
            status = 'ok'

        return status, missing, warnings

    def validate(self) -> Dict:
        """Validate all protected pages"""
        
        print("\n" + "="*70)
        print("🔐 PRODUCTION SECURITY VALIDATOR")
        print("="*70)
        print(f"\nScanning {len(self.PROTECTED_PAGES)} protected pages...")
        print(f"Source path: {self.src_path}\n")

        # Check each protected page
        for url, relative_path in sorted(self.PROTECTED_PAGES.items()):
            file_path = self.src_path / relative_path
            
            if not file_path.exists():
                status = 'error'
                missing = ['FILE_NOT_FOUND']
                warnings = []
                self.results['missing'].append((url, relative_path))
                status_symbol = '❌'
                status_text = 'MISSING'
            else:
                status, missing, warnings = self.check_file(file_path)
                if status == 'ok':
                    self.results['compliant'].append((url, relative_path))
                    status_symbol = '✅'
                    status_text = 'COMPLIANT'
                elif status == 'warning':
                    self.results['warnings'].append((url, relative_path, warnings))
                    status_symbol = '⚠️'
                    status_text = 'WARNING'
                else:
                    self.results['errors'].append((url, relative_path, missing))
                    status_symbol = '❌'
                    status_text = 'FAIL'

            print(f"{status_symbol} {url:40} {status_text:12}", end='')
            
            if missing:
                print(f"  Missing: {', '.join(missing)}")
            elif warnings:
                print(f"  Warnings: {', '.join(warnings)}")
            else:
                print()

        return self.results

    def print_summary(self):
        """Print validation summary"""
        total = len(self.PROTECTED_PAGES)
        compliant = len(self.results['compliant'])
        warnings = len(self.results['warnings'])
        errors = len(self.results['errors'])
        missing = len(self.results['missing'])

        compliance_percent = (compliant / total * 100) if total > 0 else 0

        print("\n" + "="*70)
        print("📊 SECURITY COMPLIANCE REPORT")
        print("="*70)
        print(f"\nTotal Pages:    {total}")
        print(f"✅ Compliant:   {compliant} ({compliance_percent:.1f}%)")
        print(f"⚠️  Warnings:    {warnings} ({warnings/total*100:.1f}%)")
        print(f"❌ Errors:      {errors} ({errors/total*100:.1f}%)")
        print(f"🔍 Missing:     {missing} ({missing/total*100:.1f}%)")

        # Detailed sections
        if self.results['compliant']:
            print(f"\n✅ COMPLIANT PAGES ({len(self.results['compliant'])}):")
            for url, path in self.results['compliant'][:5]:
                print(f"   {url}")
            if len(self.results['compliant']) > 5:
                print(f"   ... and {len(self.results['compliant']) - 5} more")

        if self.results['warnings']:
            print(f"\n⚠️ PAGES WITH WARNINGS ({len(self.results['warnings'])}):")
            for url, path, warns in self.results['warnings'][:5]:
                print(f"   {url}")
                print(f"      Missing: {', '.join(warns)}")
            if len(self.results['warnings']) > 5:
                print(f"   ... and {len(self.results['warnings']) - 5} more")

        if self.results['errors']:
            print(f"\n❌ PAGES WITH ERRORS ({len(self.results['errors'])}):")
            for url, path, missing in self.results['errors'][:5]:
                print(f"   {url}")
                print(f"      Missing: {', '.join(missing)}")
            if len(self.results['errors']) > 5:
                print(f"   ... and {len(self.results['errors']) - 5} more")

        if self.results['missing']:
            print(f"\n🔍 MISSING PAGES ({len(self.results['missing'])}):")
            for url, path in self.results['missing'][:5]:
                print(f"   {url} (expected: {path})")
            if len(self.results['missing']) > 5:
                print(f"   ... and {len(self.results['missing']) - 5} more")

        # Recommendations
        print("\n" + "="*70)
        print("📋 ACTION ITEMS")
        print("="*70)
        
        if errors > 0:
            print(f"\n1. FIX {errors} PAGES with critical security issues:")
            print("   - Add useProtectedPage hook")
            print("   - Add LoadingSpinner component")
            print("   - Add loading and user checks")
            print("   Reference: PRODUCTION_SECURITY_FRAMEWORK.md")

        if warnings > 0:
            print(f"\n2. REVIEW {warnings} PAGES with warnings:")
            print("   - Add missing security checks")
            print("   - Ensure proper error handling")
            print("   - Add audit logging")

        if missing > 0:
            print(f"\n3. CREATE {missing} MISSING PAGES:")
            for url, path in self.results['missing']:
                print(f"   - {path}")

        if compliance_percent < 50:
            print("\n⚠️  WARNING: Low compliance rate - Security audit recommended!")
        elif compliance_percent < 80:
            print("\n⚠️  WARNING: Partial compliance - Address remaining issues")
        else:
            print("\n✅ Good progress - Continue fixing remaining pages")

        print("\n" + "="*70)
        print(f"Overall Compliance: {compliance_percent:.1f}%")
        print("="*70 + "\n")

    def print_next_steps(self):
        """Print next steps for remediation"""
        print("\n" + "="*70)
        print("🚀 NEXT STEPS - PRODUCTION DEPLOYMENT")
        print("="*70)

        print("\n1. IMMEDIATE (This Week):")
        print("   ☐ Fix all 5 CRITICAL pages")
        print("   ☐ Review PRODUCTION_SECURITY_FRAMEWORK.md")
        print("   ☐ Use provided templates for fixes")
        print("   ☐ Test each page after fixing")

        print("\n2. SHORT-TERM (Next 3 Days):")
        print("   ☐ Fix all HIGH-PRIORITY pages")
        print("   ☐ Run this validator after each fix")
        print("   ☐ Verify 100% compliance")

        print("\n3. BEFORE PRODUCTION:")
        print("   ☐ Run full security audit")
        print("   ☐ Perform penetration testing")
        print("   ☐ Check security headers")
        print("   ☐ Enable rate limiting")
        print("   ☐ Enable audit logging")
        print("   ☐ Get security team approval")

        print("\n4. DEPLOYMENT:")
        print("   ☐ Deploy with monitoring active")
        print("   ☐ Monitor error logs (24 hours)")
        print("   ☐ Monitor security events")
        print("   ☐ Verify all redirects working")

        print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    validator = SecurityValidator()
    validator.validate()
    validator.print_summary()
    validator.print_next_steps()


if __name__ == '__main__':
    main()
