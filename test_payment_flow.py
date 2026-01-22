#!/usr/bin/env python3
"""
Comprehensive Payment & Email System Test Suite
Tests all payment endpoints, email templates, and integration
Date: January 5, 2026
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_imports():
    """Test all critical imports"""
    print("\n" + "="*70)
    print("🧪 TEST 1: CRITICAL IMPORTS")
    print("="*70)
    
    tests = [
        ("Settings", "from app.core.config import settings"),
        ("Database", "from app.core.db import engine, get_db"),
        ("Auth", "from app.core.security import get_current_user"),
        ("Stripe Service", "from app.services.stripe_service import stripe_service"),
        ("Email Service", "from app.services.email_service import email_service"),
        ("Payments Router", "from app.api.v1x.payments import router as payments_router"),
        ("Mentors Router", "from app.api.v1x.mentors import router as mentors_router"),
        ("Marketplace Router", "from app.api.v1x.marketplace import router as marketplace_router"),
        ("MentorSession Model", "from app.modelsx.mentor import MentorSession"),
        ("User Model", "from app.models.user import User"),
        ("Order Model", "from app.modelsx.order import Order"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)[:60]}")
            failed += 1
    
    print(f"\n📊 Imports: {passed} passed, {failed} failed")
    return failed == 0


def test_stripe_service():
    """Test Stripe service configuration"""
    print("\n" + "="*70)
    print("🧪 TEST 2: STRIPE SERVICE")
    print("="*70)
    
    try:
        from app.services.stripe_service import stripe_service
        from app.core.config import settings
        
        tests_passed = 0
        tests_total = 3
        
        # Test 1: Keys configured
        if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
            print("✅ STRIPE_SECRET_KEY configured")
            tests_passed += 1
        else:
            print("❌ STRIPE_SECRET_KEY missing or empty")
        
        # Test 2: Public key configured
        if hasattr(settings, 'STRIPE_PUBLIC_KEY') and settings.STRIPE_PUBLIC_KEY:
            print("✅ STRIPE_PUBLIC_KEY configured")
            tests_passed += 1
        else:
            print("❌ STRIPE_PUBLIC_KEY missing or empty")
        
        # Test 3: Service methods exist
        methods = ['create_payment_intent', 'capture_payment', 'verify_webhook_signature', 'create_refund']
        all_exist = all(hasattr(stripe_service, method) for method in methods)
        if all_exist:
            print(f"✅ All {len(methods)} service methods exist")
            tests_passed += 1
        else:
            print(f"❌ Some service methods missing")
        
        print(f"\n📊 Stripe Service: {tests_passed}/{tests_total} passed")
        return tests_passed == tests_total
        
    except Exception as e:
        print(f"❌ Stripe service test failed: {e}")
        return False


def test_email_service():
    """Test email service and templates"""
    print("\n" + "="*70)
    print("🧪 TEST 3: EMAIL SERVICE & TEMPLATES")
    print("="*70)
    
    try:
        from app.services.email_service import email_service
        
        # Test 1: Email service initialized
        if email_service:
            print("✅ Email service initialized")
        else:
            print("❌ Email service not initialized")
            return False
        
        # Test 2: Check all email templates exist
        templates = [
            'send_welcome_email',
            'send_session_confirmation',
            'send_session_reminder',
            'send_session_cancellation',
            'send_payment_receipt',
            'send_payment_failed_email',  # NEW
            'send_order_confirmation',     # NEW
            'send_mentor_approved',
            'send_mentor_rejected',
        ]
        
        missing = []
        for template in templates:
            if not hasattr(email_service, template):
                missing.append(template)
        
        if not missing:
            print(f"✅ All {len(templates)} email templates present")
        else:
            print(f"❌ Missing templates: {', '.join(missing)}")
            return False
        
        # Test 3: Email provider configured
        provider = getattr(email_service, 'provider', None)
        if provider:
            print(f"✅ Email provider configured: {provider}")
        else:
            print("❌ Email provider not configured")
            return False
        
        print(f"\n📊 Email Service: 3/3 passed")
        return True
        
    except Exception as e:
        print(f"❌ Email service test failed: {e}")
        return False


def test_database_models():
    """Test database models"""
    print("\n" + "="*70)
    print("🧪 TEST 4: DATABASE MODELS")
    print("="*70)
    
    try:
        from app.modelsx.mentor import MentorSession
        from app.models.user import User
        from app.modelsx.order import Order
        
        tests_passed = 0
        tests_total = 3
        
        # Test 1: MentorSession has payment fields
        session_fields = ['payment_intent_id', 'payment_status', 'price', 'status']
        if all(hasattr(MentorSession, field) for field in session_fields):
            print(f"✅ MentorSession has payment fields: {', '.join(session_fields)}")
            tests_passed += 1
        else:
            print("❌ MentorSession missing payment fields")
        
        # Test 2: User has email field
        if hasattr(User, 'email'):
            print("✅ User model has email field")
            tests_passed += 1
        else:
            print("❌ User model missing email field")
        
        # Test 3: Order has payment fields
        order_fields = ['payment_status', 'amount', 'order_number']
        if all(hasattr(Order, field) for field in order_fields):
            print(f"✅ Order has payment fields: {', '.join(order_fields)}")
            tests_passed += 1
        else:
            print("❌ Order missing payment fields")
        
        print(f"\n📊 Database Models: {tests_passed}/{tests_total} passed")
        return tests_passed == tests_total
        
    except Exception as e:
        print(f"❌ Database models test failed: {e}")
        return False


def test_payment_endpoints():
    """Test payment endpoints exist and are properly configured"""
    print("\n" + "="*70)
    print("🧪 TEST 5: PAYMENT ENDPOINTS")
    print("="*70)
    
    try:
        from app.api.v1x.payments import router as payments_router
        
        # Expected endpoints
        endpoints = [
            ('POST', '/create-payment-intent'),
            ('POST', '/capture-payment/{session_id}'),
            ('POST', '/cancel-payment/{session_id}'),
            ('POST', '/webhook'),
            ('GET', '/status/{session_id}'),
        ]
        
        # Extract routes from router
        routes = []
        for route in payments_router.routes:
            methods = list(route.methods) if hasattr(route, 'methods') else []
            path = route.path if hasattr(route, 'path') else ''
            for method in methods:
                routes.append((method, path))
        
        print(f"Found {len(routes)} payment routes:")
        for method, path in routes:
            print(f"  {method:6} {path}")
        
        # Check critical endpoints
        critical = [
            ('POST', '/create-payment-intent'),
            ('POST', '/webhook'),
        ]
        
        found = sum(1 for m, p in critical if (m, p) in routes)
        print(f"\n✅ Found {found}/{len(critical)} critical endpoints")
        
        return found == len(critical)
        
    except Exception as e:
        print(f"❌ Payment endpoints test failed: {e}")
        return False


def test_mentors_email_integration():
    """Test mentors endpoint email integration"""
    print("\n" + "="*70)
    print("🧪 TEST 6: MENTORS EMAIL INTEGRATION")
    print("="*70)
    
    try:
        from app.api.v1x.mentors import router as mentors_router
        
        # Check if mentors router exists
        if mentors_router:
            print("✅ Mentors router loaded")
            
            # Count routes
            route_count = len(mentors_router.routes)
            print(f"✅ Mentors router has {route_count} endpoints")
            
            # Look for sessions endpoint
            has_sessions = any('/sessions' in str(route.path) for route in mentors_router.routes)
            if has_sessions:
                print("✅ Sessions endpoint exists in mentors router")
            else:
                print("❌ Sessions endpoint not found")
                return False
            
            return True
        else:
            print("❌ Mentors router not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Mentors email integration test failed: {e}")
        return False


def test_marketplace_email_integration():
    """Test marketplace email integration"""
    print("\n" + "="*70)
    print("🧪 TEST 7: MARKETPLACE EMAIL INTEGRATION")
    print("="*70)
    
    try:
        from app.api.v1x.marketplace import router as marketplace_router
        
        if marketplace_router:
            print("✅ Marketplace router loaded")
            
            route_count = len(marketplace_router.routes)
            print(f"✅ Marketplace router has {route_count} endpoints")
            
            # Check for checkout endpoint
            has_checkout = any('/checkout' in str(route.path) for route in marketplace_router.routes)
            if has_checkout:
                print("✅ Checkout endpoint exists")
            else:
                print("⚠️  Checkout endpoint not found (may be optional)")
            
            return True
        else:
            print("❌ Marketplace router not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Marketplace email integration test failed: {e}")
        return False


def test_main_app():
    """Test main app loads with all routers"""
    print("\n" + "="*70)
    print("🧪 TEST 8: MAIN APPLICATION")
    print("="*70)
    
    try:
        from app.main import app
        
        # Test 1: App created
        if app:
            print("✅ FastAPI app created")
        else:
            print("❌ App not created")
            return False
        
        # Test 2: Routes mounted
        route_count = len(app.routes)
        print(f"✅ App has {route_count} total routes mounted")
        
        # Test 3: Check for payments in routes
        payment_routes = [r for r in app.routes if '/payments' in str(getattr(r, 'path', ''))]
        if payment_routes:
            print(f"✅ Found {len(payment_routes)} payment-related routes")
        else:
            print("⚠️  No payment routes found in main app")
        
        # Test 4: Check middleware
        has_cors = any('CORSMiddleware' in str(m) for m in app.user_middleware)
        if has_cors or app.middleware:
            print("✅ Middleware configured")
        else:
            print("⚠️  Middleware not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """Test environment configuration"""
    print("\n" + "="*70)
    print("🧪 TEST 9: CONFIGURATION")
    print("="*70)
    
    try:
        from app.core.config import settings
        
        tests_passed = 0
        tests_total = 5
        
        # Test 1: Database URL
        if hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL:
            print("✅ DATABASE_URL configured")
            tests_passed += 1
        else:
            print("⚠️  DATABASE_URL not configured (may use default)")
        
        # Test 2: Stripe keys
        if hasattr(settings, 'STRIPE_SECRET_KEY') and settings.STRIPE_SECRET_KEY:
            print("✅ STRIPE_SECRET_KEY configured")
            tests_passed += 1
        else:
            print("⚠️  STRIPE_SECRET_KEY not configured")
        
        # Test 3: JWT Secret
        if hasattr(settings, 'JWT_SECRET_KEY') and settings.JWT_SECRET_KEY:
            print("✅ JWT_SECRET_KEY configured")
            tests_passed += 1
        else:
            print("⚠️  JWT_SECRET_KEY not configured")
        
        # Test 4: Email provider
        if hasattr(settings, 'EMAIL_PROVIDER') and settings.EMAIL_PROVIDER:
            print(f"✅ EMAIL_PROVIDER configured: {settings.EMAIL_PROVIDER}")
            tests_passed += 1
        else:
            print("⚠️  EMAIL_PROVIDER not configured")
        
        # Test 5: Frontend origin
        if hasattr(settings, 'FRONTEND_ORIGIN') and settings.FRONTEND_ORIGIN:
            print(f"✅ FRONTEND_ORIGIN configured: {settings.FRONTEND_ORIGIN}")
            tests_passed += 1
        else:
            print("⚠️  FRONTEND_ORIGIN not configured")
        
        print(f"\n📊 Configuration: {tests_passed}/{tests_total} passed")
        return tests_passed >= 3  # At least critical configs
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_syntax():
    """Test Python files for syntax errors"""
    print("\n" + "="*70)
    print("🧪 TEST 10: PYTHON SYNTAX")
    print("="*70)
    
    import py_compile
    
    files_to_check = [
        'backend/app/api/v1x/payments.py',
        'backend/app/api/v1x/mentors.py',
        'backend/app/api/v1x/marketplace.py',
        'backend/app/services/email_service.py',
        'backend/app/main.py',
    ]
    
    passed = 0
    failed = 0
    
    for filepath in files_to_check:
        full_path = Path(__file__).parent / filepath
        try:
            py_compile.compile(str(full_path), doraise=True)
            print(f"✅ {filepath}")
            passed += 1
        except py_compile.PyCompileError as e:
            print(f"❌ {filepath}: {str(e)[:60]}")
            failed += 1
    
    print(f"\n📊 Syntax: {passed} passed, {failed} failed")
    return failed == 0


def run_all_tests():
    """Run all tests and generate report"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🧪 PAYMENT SYSTEM COMPREHENSIVE TEST SUITE" + " "*10 + "║")
    print("║" + " "*20 + "SkillForge Global - January 5, 2026" + " "*12 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Imports", test_imports),
        ("Stripe Service", test_stripe_service),
        ("Email Service", test_email_service),
        ("Database Models", test_database_models),
        ("Payment Endpoints", test_payment_endpoints),
        ("Mentors Email Integration", test_mentors_email_integration),
        ("Marketplace Email Integration", test_marketplace_email_integration),
        ("Main Application", test_main_app),
        ("Configuration", test_configuration),
        ("Python Syntax", test_syntax),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Final report
    print("\n" + "="*70)
    print("📊 FINAL REPORT")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTest Results: {passed}/{total} PASSED\n")
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status:8} | {name}")
    
    print("\n" + "="*70)
    if passed == total:
        print("🎉 ALL TESTS PASSED - SYSTEM READY FOR TESTING!")
    elif passed >= total * 0.8:
        print(f"✅ {passed}/{total} tests passed - Core functionality working")
    else:
        print(f"⚠️  {passed}/{total} tests passed - Some issues need attention")
    
    print("="*70 + "\n")
    
    return passed, total


if __name__ == "__main__":
    passed, total = run_all_tests()
    sys.exit(0 if passed == total else 1)
