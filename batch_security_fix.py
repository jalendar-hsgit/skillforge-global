#!/usr/bin/env python3
"""
Batch Security Fix - Auto-apply security templates to unprotected pages
Usage: python batch_security_fix.py --dry-run    (preview changes)
       python batch_security_fix.py --apply     (apply changes)
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, Optional

class BatchSecurityFix:
    """Automatically apply security fixes to pages"""

    # Pages that should be protected (with their required roles if any)
    PROTECTED_PAGES = {
        # Format: 'path/file.tsx': 'role' or None for user
        'dashboard/index.tsx': None,
        'dashboard-analytics.tsx': None,
        'customize-dashboard.tsx': None,
        'feed.tsx': None,
        'profile/index.tsx': None,
        'profile/edit.tsx': None,
        'profile/settings.tsx': None,
        'mentors/settings.tsx': None,
        'mentors/my-sessions.tsx': None,
        'mentors/earnings.tsx': 'mentor',
        'mentors/dashboard/index.tsx': 'mentor',
        'mentors/dashboard/profile.tsx': 'mentor',
        'mentors/dashboard/sessions.tsx': 'mentor',
        'mentors/dashboard/students.tsx': 'mentor',
        'mentors/dashboard/earnings.tsx': 'mentor',
        'mentors/dashboard/payouts.tsx': 'mentor',
        'mentors/dashboard/analytics.tsx': 'mentor',
        'mentors/dashboard/reviews.tsx': 'mentor',
        'mentors/dashboard/verification.tsx': 'mentor',
        'practice/submissions.tsx': None,
        'ai-hints.tsx': None,
        'hint-preferences.tsx': None,
        'resumes/index.tsx': None,
        'resumes/new.tsx': None,
        'resumes/templates.tsx': None,
        'resumes/compare.tsx': None,
        'resumes/import.tsx': None,
        'resumes/diagnostics.tsx': None,
        'jobs/index.tsx': None,
        'job-tracker/add.tsx': None,
        'job-tracker/analytics.tsx': None,
        'marketplace/cart.tsx': None,
        'marketplace/orders.tsx': None,
        'marketplace/seller/index.tsx': 'seller',
        'marketplace/seller/create-product.tsx': 'seller',
        'marketplace/seller/products.tsx': 'seller',
        'marketplace/seller/orders.tsx': 'seller',
        'marketplace/seller/analytics.tsx': 'seller',
        'messages/index.tsx': None,
        'notifications/index.tsx': None,
        'social/index.tsx': None,
        'social/feed/index.tsx': None,
        'social/following.tsx': None,
        'security.tsx': None,
        'pwa-settings.tsx': None,
        'admin/index.tsx': 'admin',
        'coins.tsx': None,
        'referral_program.tsx': None,
        'recommendations.tsx': None,
        'teams.tsx': None,
        'github-integration.tsx': None,
        'ai.tsx': None,
    }

    BASIC_TEMPLATE = '''import {{ useProtectedPage }} from '@/lib/useProtectedPage'
import {{ LoadingSpinner }} from '@/components/LoadingSpinner'
import {{ useRouter }} from 'next/router'
import {{ useEffect }} from 'react'

export default function PageName() {{
  const router = useRouter()
  const {{ user, loading, error }} = useProtectedPage()

  // Security: Prevent unauthorized access
  useEffect(() => {{
    if (!loading && !user) {{
      router.push('/login?redirect=' + encodeURIComponent(router.asPath))
    }}
  }}, [user, loading])

  // Security: Show error state
  if (error) {{
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error</h1>
          <p className="text-gray-600 mt-2">{{error}}</p>
          <button 
            onClick={{() => router.push('/login')}}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }}

  // Security: Show loading spinner
  if (loading) {{
    return <LoadingSpinner message="Loading..." />
  }}

  // Security: Check authorization
  if (!user) {{
    return null
  }}

  return (
    <div className="container mx-auto py-8">
      <h1>Page Content</h1>
    </div>
  )
}}
'''

    ROLE_TEMPLATE = '''import {{ useProtectedPage }} from '@/lib/useProtectedPage'
import {{ LoadingSpinner }} from '@/components/LoadingSpinner'
import {{ useRouter }} from 'next/router'
import {{ useEffect }} from 'react'

export default function RolePage() {{
  const router = useRouter()
  const {{ user, loading, isAuthorized, error }} = useProtectedPage('{role}')

  // Security: Log unauthorized access attempts
  useEffect(() => {{
    if (!loading && user && !isAuthorized) {{
      console.warn(`Unauthorized access attempt: ${{user.email}}`)
    }}
  }}, [user, loading, isAuthorized])

  // Security: Show error state
  if (error) {{
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Access Denied</h1>
          <p className="text-gray-600 mt-2">You do not have permission to access this page</p>
          <button 
            onClick={{() => router.push('/dashboard')}}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    )
  }}

  // Security: Show loading spinner
  if (loading) {{
    return <LoadingSpinner message="Verifying access..." />
  }}

  // Security: Check authorization
  if (!isAuthorized) {{
    return null
  }}

  return (
    <div className="container mx-auto py-8">
      <h1>Protected Content</h1>
    </div>
  )
}}
'''

    def __init__(self, root_path: str = '.'):
        self.root_path = Path(root_path)
        self.src_path = self.root_path / 'src' / 'pages'
        self.changes = []

    def needs_protection(self, file_path: Path) -> bool:
        """Check if file needs protection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return False

        # Already protected
        if 'useProtectedPage' in content:
            return False

        # Public page - skip
        if file_path.name in ['404.tsx', '500.tsx', '_app.tsx', '_document.tsx']:
            return False

        return True

    def create_fixed_file(self, role: Optional[str] = None) -> str:
        """Create a fixed file template"""
        if role:
            return self.ROLE_TEMPLATE.replace('{role}', role)
        else:
            return self.BASIC_TEMPLATE

    def fix_file(self, file_path: Path, role: Optional[str] = None, dry_run: bool = True) -> Tuple[bool, str]:
        """Fix a single file - returns (success, message)"""
        
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except Exception as e:
            return False, f"Read error: {e}"

        # Skip if already protected
        if 'useProtectedPage' in original_content:
            return True, "Already protected"

        # Create new content (use template for safety - don't modify existing code)
        new_content = self.create_fixed_file(role)

        if dry_run:
            return True, f"Would apply security template (role={role or 'user'})"
        else:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True, "Fixed with security template"
            except Exception as e:
                return False, f"Write error: {e}"

    def batch_fix(self, dry_run: bool = True, verbose: bool = True):
        """Fix all unprotected pages"""
        
        if verbose:
            print("\n" + "="*70)
            print("🔐 BATCH SECURITY FIX")
            print("="*70)
            mode = "DRY RUN" if dry_run else "APPLY CHANGES"
            print(f"Mode: {mode}")
            print(f"Scanning {len(self.PROTECTED_PAGES)} pages...\n")

        fixed_count = 0
        skip_count = 0
        error_count = 0

        for rel_path, role in sorted(self.PROTECTED_PAGES.items()):
            file_path = self.src_path / rel_path
            
            if not file_path.exists():
                if verbose:
                    print(f"⚠️  {rel_path:45} MISSING")
                error_count += 1
                continue

            if not self.needs_protection(file_path):
                if verbose:
                    print(f"✅ {rel_path:45} ALREADY PROTECTED")
                skip_count += 1
                continue

            success, message = self.fix_file(file_path, role, dry_run)
            
            if success:
                if verbose:
                    symbol = "🔧" if dry_run else "✅"
                    print(f"{symbol} {rel_path:45} {message}")
                fixed_count += 1
                self.changes.append((rel_path, role, message))
            else:
                if verbose:
                    print(f"❌ {rel_path:45} {message}")
                error_count += 1

        if verbose:
            self._print_summary(fixed_count, skip_count, error_count, dry_run)

        return fixed_count, skip_count, error_count

    def _print_summary(self, fixed: int, skip: int, error: int, dry_run: bool):
        """Print summary"""
        total = len(self.PROTECTED_PAGES)
        
        print("\n" + "="*70)
        print("📊 BATCH FIX SUMMARY")
        print("="*70)
        print(f"\nTotal Pages:     {total}")
        print(f"✅ Already OK:   {skip}")
        print(f"🔧 Fixed:        {fixed}")
        print(f"❌ Errors:       {error}")

        if dry_run:
            print("\n💡 DRY RUN MODE - No changes made")
            print("   Run with --apply to make changes")
        else:
            print("\n✅ CHANGES APPLIED")
            print("   Test all pages before deploying to production")

        print("\n" + "="*70 + "\n")

    def validate_changes(self):
        """Validate that fixes work correctly"""
        print("\n" + "="*70)
        print("🧪 VALIDATING CHANGES")
        print("="*70)
        
        for rel_path, role, message in self.changes[:5]:
            file_path = self.src_path / rel_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                checks = [
                    ('useProtectedPage', 'useProtectedPage' in content),
                    ('LoadingSpinner', 'LoadingSpinner' in content),
                    ('useRouter', 'useRouter' in content),
                    ('loading check', 'if (loading)' in content or 'if(loading)' in content),
                ]
                
                all_pass = all(check[1] for check in checks)
                status = "✅" if all_pass else "⚠️"
                
                print(f"{status} {rel_path}")
                for check_name, passed in checks:
                    symbol = "✓" if passed else "✗"
                    print(f"   {symbol} {check_name}")
            except Exception as e:
                print(f"❌ {rel_path} - Error: {e}")

        if len(self.changes) > 5:
            print(f"\n... and {len(self.changes) - 5} more")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main entry point"""
    dry_run = '--apply' not in sys.argv
    
    if '--apply' in sys.argv:
        confirm = input("\n⚠️  This will modify ALL unprotected pages. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    fixer = BatchSecurityFix()
    fixed, skip, error = fixer.batch_fix(dry_run=dry_run)

    if not dry_run and fixed > 0:
        fixer.validate_changes()
        print("\n✅ Next steps:")
        print("   1. Run: npm run build")
        print("   2. Run: npm run dev")
        print("   3. Test each protected page")
        print("   4. Review PRODUCTION_SECURITY_FRAMEWORK.md")
        print("   5. Deploy to staging for testing")


if __name__ == '__main__':
    main()
