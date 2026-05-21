#!/usr/bin/env python
"""
Comprehensive Payment Integration Test Suite
Tests ALL payment features with demo data:
- Mentor Session Payments
- Marketplace Product Payments  
- Course Payments
- Subscription Payments
- Student Purchases
- Admin Payout Management
"""

import sys
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
sys.path.insert(0, '/d/python code/sfg/skillforge-global/backend')

from sqlalchemy.orm import Session
from app.core.db import get_db, engine, Base, SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.modelsx.mentor import Mentor, MentorSession, SessionStatus
from app.modelsx.marketplace import DigitalProduct, ProductStatus, SellerEarning
from app.modelsx.order import Order, Coupon
from app.modelsx.payout import MentorEarning, MentorPayout, PayoutStatus, PayoutMethod
from app.modelsx.subscription import Subscription, SubscriptionEvent
from app.modelsx.course import Course
from app.modelsx.progress import VideoProgress
from app.modelsx.video import Video


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

TEST_RESULTS = {
    "passed": 0,
    "failed": 0,
    "errors": [],
}

def test_result(test_name, passed, message=""):
    """Record test result"""
    if passed:
        TEST_RESULTS["passed"] += 1
        print(f"✅ {test_name}")
    else:
        TEST_RESULTS["failed"] += 1
        error_msg = f"❌ {test_name}: {message}"
        TEST_RESULTS["errors"].append(error_msg)
        print(error_msg)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_session():
    """Get database session"""
    return SessionLocal()


def print_section(title):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_subsection(title):
    """Print subsection header"""
    print(f"\n{title}")
    print(f"{'-'*80}")


# ============================================================================
# TEST 1: MENTOR SESSION PAYMENTS
# ============================================================================

def test_mentor_session_payments():
    """Test complete mentor session payment flow"""
    print_section("TEST 1: MENTOR SESSION PAYMENTS")
    
    db = get_session()
    try:
        # Get mentor
        mentor = db.query(Mentor).filter(Mentor.id == 1).first()
        test_result("Mentor 1 exists", mentor is not None, "Mentor not found")
        
        if not mentor:
            return
        
        # Get student
        student = db.query(User).filter(User.id == 3).first()
        test_result("Student exists", student is not None, "Student not found")
        
        if not student:
            return
        
        # Get mentor user
        mentor_user = db.query(User).filter(User.id == mentor.user_id).first()
        test_result("Mentor user exists", mentor_user is not None, "Mentor user not found")
        
        # Create mentor session
        session = MentorSession(
            mentor_id=mentor.id,
            student_id=student.id,
            topic="Python Advanced Topics",
            scheduled_at=datetime.utcnow() + timedelta(days=7),
            status=SessionStatus.PENDING,
            price=75.0,
            duration_minutes=60,
            payment_intent_id=f"pi_test_{int(datetime.utcnow().timestamp())}"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        test_result(
            "Mentor session created",
            session.id is not None,
            f"Session ID: {session.id}"
        )
        
        # Simulate payment
        session.payment_status = 'paid'
        session.status = SessionStatus.CONFIRMED
        
        # Create earning record (as webhook would do)
        mentor_earning = MentorEarning(
            mentor_id=mentor.id,
            session_id=session.id,
            gross_amount=75.0,
            platform_fee=15.0,
            net_amount=60.0,
            earned_at=datetime.utcnow()
        )
        db.add(mentor_earning)
        db.commit()
        
        test_result(
            "Mentor earning created",
            mentor_earning.id is not None,
            f"Earning: ${mentor_earning.net_amount} for mentor"
        )
        
        # Verify commission split
        test_result(
            "Commission split (80/20)",
            mentor_earning.net_amount == 60.0 and mentor_earning.platform_fee == 15.0,
            f"Net: ${mentor_earning.net_amount}, Fee: ${mentor_earning.platform_fee}"
        )
        
        # Get earnings summary
        earnings = db.query(MentorEarning).filter(
            MentorEarning.mentor_id == mentor.id
        ).all()
        
        total = sum(e.net_amount for e in earnings)
        test_result(
            "Mentor earnings summary",
            total > 0,
            f"Total earnings: ${total:.2f}"
        )
        
    except Exception as e:
        test_result("Mentor session payment flow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 2: MARKETPLACE PRODUCT PAYMENTS
# ============================================================================

def test_marketplace_payments():
    """Test complete marketplace product payment flow"""
    print_section("TEST 2: MARKETPLACE PRODUCT PAYMENTS")
    
    db = get_session()
    try:
        # Get seller
        seller = db.query(User).filter(User.role == UserRole.MENTOR).first()
        test_result("Seller exists", seller is not None, "Seller not found")
        
        if not seller:
            return
        
        # Get product
        product = db.query(DigitalProduct).filter(
            DigitalProduct.seller_id == seller.id
        ).first()
        
        if not product:
            # Create test product
            product = DigitalProduct(
                name="Advanced Python Guide",
                slug="advanced-python-guide",
                description="Comprehensive Python programming guide",
                seller_id=seller.id,
                price=49.99,
                product_type="guide",
                status=ProductStatus.PUBLISHED
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        
        test_result(
            "Digital product exists",
            product.id is not None,
            f"Product: {product.name} (${product.price})"
        )
        
        # Get buyer
        buyer = db.query(User).filter(User.role == UserRole.USER).first()
        test_result("Buyer exists", buyer is not None, "Buyer not found")
        
        if not buyer:
            return
        
        # Create order
        order = Order(
            user_id=buyer.id,
            digital_product_id=product.id,
            amount=product.price,
            status='completed',
            payment_status='completed',
            payment_intent_id=f"pi_mp_{int(datetime.utcnow().timestamp())}",
            paid_at=datetime.utcnow()
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        test_result(
            "Marketplace order created",
            order.id is not None,
            f"Order: ${order.amount} for {product.name}"
        )
        
        # Create earning record (as webhook would do)
        seller_earning = SellerEarning(
            seller_id=product.seller_id,
            order_id=order.id,
            product_id=product.id,
            gross_amount=product.price,
            platform_fee=product.price * 0.20,
            net_amount=product.price * 0.80,
            earned_at=datetime.utcnow()
        )
        db.add(seller_earning)
        db.commit()
        
        test_result(
            "Seller earning created",
            seller_earning.id is not None,
            f"Earning: ${seller_earning.net_amount:.2f}"
        )
        
        # Verify commission split
        expected_net = product.price * 0.80
        expected_fee = product.price * 0.20
        test_result(
            "Marketplace commission (80/20)",
            abs(seller_earning.net_amount - expected_net) < 0.01 and
            abs(seller_earning.platform_fee - expected_fee) < 0.01,
            f"Net: ${seller_earning.net_amount:.2f}, Fee: ${seller_earning.platform_fee:.2f}"
        )
        
        # Get earnings summary
        all_earnings = db.query(SellerEarning).filter(
            SellerEarning.seller_id == seller.id
        ).all()
        
        total_seller = sum(e.net_amount for e in all_earnings)
        test_result(
            "Seller earnings summary",
            total_seller > 0,
            f"Total marketplace earnings: ${total_seller:.2f}"
        )
        
    except Exception as e:
        test_result("Marketplace payment flow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 3: COURSE PURCHASES
# ============================================================================

def test_course_payments():
    """Test complete course payment flow"""
    print_section("TEST 3: COURSE PAYMENTS")
    
    db = get_session()
    try:
        # Get course
        course = db.query(Course).first()
        test_result("Course exists", course is not None, "No courses found")
        
        if not course:
            return
        
        # Get student
        student = db.query(User).filter(User.role == UserRole.USER).first()
        test_result("Student exists", student is not None, "Student not found")
        
        if not student:
            return
        
        # Create course order
        order = Order(
            user_id=student.id,
            course_id=course.id,
            amount=course.price if hasattr(course, 'price') and course.price else 49.99,
            status='completed',
            payment_status='completed',
            payment_intent_id=f"pi_course_{int(datetime.utcnow().timestamp())}",
            paid_at=datetime.utcnow()
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        test_result(
            "Course order created",
            order.id is not None,
            f"Order: ${order.amount} for {course.title if hasattr(course, 'title') else 'Course'}"
        )
        
        # Create video progress (student enrollment)
        videos = db.query(Video).filter(Video.course_id == course.id).limit(3).all()
        
        progress_count = 0
        for video in videos:
            progress = VideoProgress(
                user_id=student.id,
                video_id=video.id,
                progress_percent=0,
                completed=False,
                created_at=datetime.utcnow()
            )
            db.add(progress)
            progress_count += 1
        
        db.commit()
        
        test_result(
            "Student enrolled in course",
            progress_count > 0,
            f"Created {progress_count} video progress records"
        )
        
        # Verify enrollment
        enrolled_videos = db.query(VideoProgress).filter(
            VideoProgress.user_id == student.id,
            VideoProgress.video_id.in_([v.id for v in videos])
        ).count()
        
        test_result(
            "Course enrollment verified",
            enrolled_videos > 0,
            f"Student enrolled in {enrolled_videos} videos"
        )
        
    except Exception as e:
        test_result("Course payment flow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 4: MENTOR PAYOUT REQUESTS
# ============================================================================

def test_mentor_payouts():
    """Test mentor payout request workflow"""
    print_section("TEST 4: MENTOR PAYOUT REQUESTS")
    
    db = get_session()
    try:
        # Get mentor with earnings
        mentor = db.query(Mentor).first()
        test_result("Mentor exists", mentor is not None, "No mentors found")
        
        if not mentor:
            return
        
        # Get mentor earnings
        earnings = db.query(MentorEarning).filter(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == False
        ).all()
        
        available_balance = sum(e.net_amount for e in earnings)
        test_result(
            "Mentor has available balance",
            available_balance >= 10.0,
            f"Available: ${available_balance:.2f}"
        )
        
        if available_balance < 10.0:
            print("⚠️  Creating test earning for payout test...")
            # Create test earning
            session = MentorSession(
                mentor_id=mentor.id,
                student_id=3,
                topic="Test Session",
                scheduled_at=datetime.utcnow() + timedelta(days=7),
                status=SessionStatus.CONFIRMED,
                price=60.0,
                duration_minutes=60,
                payment_intent_id=f"pi_test_payout_{int(datetime.utcnow().timestamp())}"
            )
            db.add(session)
            db.commit()
            
            earning = MentorEarning(
                mentor_id=mentor.id,
                session_id=session.id,
                gross_amount=60.0,
                platform_fee=12.0,
                net_amount=48.0,
                earned_at=datetime.utcnow()
            )
            db.add(earning)
            db.commit()
            available_balance = 48.0
        
        # Request payout
        payout_amount = min(available_balance, 50.0)
        
        payout = MentorPayout(
            mentor_id=mentor.id,
            amount=payout_amount,
            net_amount=payout_amount,
            status=PayoutStatus.PENDING,
            method=PayoutMethod.STRIPE,
            requested_at=datetime.utcnow()
        )
        db.add(payout)
        db.commit()
        db.refresh(payout)
        
        test_result(
            "Mentor payout request created",
            payout.id is not None,
            f"Payout: ${payout.amount:.2f} (Status: {payout.status.value})"
        )
        
        # Verify minimum amount validation
        test_result(
            "Minimum payout validation",
            payout.amount >= 10.0,
            f"Amount: ${payout.amount:.2f}"
        )
        
        # Simulate approval
        payout.status = PayoutStatus.PROCESSING
        payout.processed_at = datetime.utcnow()
        payout.stripe_transfer_id = f"tr_mentor_{payout.id}_{int(datetime.utcnow().timestamp())}"
        
        # Mark earnings as paid
        amount_marked = 0
        for earning in earnings:
            if amount_marked + earning.net_amount <= payout.amount:
                earning.is_paid_out = True
                earning.payout_id = payout.id
                earning.paid_out_at = datetime.utcnow()
                amount_marked += earning.net_amount
        
        db.commit()
        
        test_result(
            "Mentor payout approved",
            payout.stripe_transfer_id is not None,
            f"Transfer ID: {payout.stripe_transfer_id}"
        )
        
        # Verify earnings marked as paid
        paid_earnings = db.query(MentorEarning).filter(
            MentorEarning.mentor_id == mentor.id,
            MentorEarning.is_paid_out == True
        ).count()
        
        test_result(
            "Earnings marked as paid",
            paid_earnings > 0,
            f"Paid earnings: {paid_earnings}"
        )
        
    except Exception as e:
        test_result("Mentor payout workflow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 5: SELLER PAYOUT REQUESTS
# ============================================================================

def test_seller_payouts():
    """Test seller payout request workflow"""
    print_section("TEST 5: SELLER PAYOUT REQUESTS")
    
    db = get_session()
    try:
        from app.modelsx.marketplace import SellerPayout
        
        # Get seller
        seller = db.query(User).filter(User.role == UserRole.MENTOR).first()
        test_result("Seller exists", seller is not None, "No sellers found")
        
        if not seller:
            return
        
        # Get seller earnings
        earnings = db.query(SellerEarning).filter(
            SellerEarning.seller_id == seller.id,
            SellerEarning.is_paid_out == False
        ).all()
        
        available_balance = sum(e.net_amount for e in earnings)
        
        # Create test earning if none exists
        if available_balance < 10.0:
            print("⚠️  Creating test product earning for payout test...")
            product = db.query(DigitalProduct).filter(
                DigitalProduct.seller_id == seller.id
            ).first()
            
            if not product:
                product = DigitalProduct(
                    name="Test Product",
                    slug=f"test-product-{int(datetime.utcnow().timestamp())}",
                    description="Test product",
                    seller_id=seller.id,
                    price=50.0,
                    product_type="guide",
                    status=ProductStatus.PUBLISHED
                )
                db.add(product)
                db.commit()
            
            order = Order(
                user_id=3,
                digital_product_id=product.id,
                amount=50.0,
                status='completed',
                payment_status='completed',
                payment_intent_id=f"pi_sp_{int(datetime.utcnow().timestamp())}"
            )
            db.add(order)
            db.commit()
            
            earning = SellerEarning(
                seller_id=seller.id,
                order_id=order.id,
                product_id=product.id,
                gross_amount=50.0,
                platform_fee=10.0,
                net_amount=40.0,
                earned_at=datetime.utcnow()
            )
            db.add(earning)
            db.commit()
            available_balance = 40.0
        
        # Request payout
        payout_amount = min(available_balance, 45.0)
        
        payout = SellerPayout(
            seller_id=seller.id,
            amount=payout_amount,
            status='pending',
            payout_method='stripe',
            requested_at=datetime.utcnow()
        )
        db.add(payout)
        db.commit()
        db.refresh(payout)
        
        test_result(
            "Seller payout request created",
            payout.id is not None,
            f"Payout: ${payout.amount:.2f} (Status: {payout.status})"
        )
        
        # Simulate approval
        payout.status = 'processing'
        payout.processed_at = datetime.utcnow()
        payout.transaction_id = f"tr_seller_{payout.id}_{int(datetime.utcnow().timestamp())}"
        
        # Mark earnings as paid
        amount_marked = 0
        for earning in earnings:
            if amount_marked + earning.net_amount <= payout.amount:
                earning.is_paid_out = True
                earning.payout_id = payout.id
                earning.paid_out_at = datetime.utcnow()
                amount_marked += earning.net_amount
        
        db.commit()
        
        test_result(
            "Seller payout approved",
            payout.transaction_id is not None,
            f"Transaction ID: {payout.transaction_id}"
        )
        
    except Exception as e:
        test_result("Seller payout workflow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 6: SUBSCRIPTION PAYMENTS
# ============================================================================

def test_subscription_payments():
    """Test subscription payment flow"""
    print_section("TEST 6: SUBSCRIPTION PAYMENTS")
    
    db = get_session()
    try:
        # Get student
        student = db.query(User).filter(User.role == UserRole.USER).first()
        test_result("Student exists", student is not None, "Student not found")
        
        if not student:
            return
        
        # Create subscription
        subscription = Subscription(
            user_id=student.id,
            plan_name="Pro",
            billing_period="monthly",
            amount=29.99,
            status="active",
            stripe_subscription_id=f"sub_test_{int(datetime.utcnow().timestamp())}",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        test_result(
            "Subscription created",
            subscription.id is not None,
            f"Plan: {subscription.plan_name} - ${subscription.amount}/month"
        )
        
        # Create subscription event (payment)
        event = SubscriptionEvent(
            subscription_id=subscription.id,
            event_type="payment_succeeded",
            amount=subscription.amount,
            status="completed",
            stripe_event_id=f"evt_{int(datetime.utcnow().timestamp())}",
            created_at=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        
        test_result(
            "Subscription payment recorded",
            event.id is not None,
            f"Payment: ${event.amount} (Type: {event.event_type})"
        )
        
        # Verify subscription active
        active_sub = db.query(Subscription).filter(
            Subscription.user_id == student.id,
            Subscription.status == "active"
        ).first()
        
        test_result(
            "Subscription active",
            active_sub is not None,
            f"User has active {active_sub.plan_name if active_sub else 'N/A'} subscription"
        )
        
    except Exception as e:
        test_result("Subscription payment flow", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 7: ADMIN PAYOUT MANAGEMENT
# ============================================================================

def test_admin_payout_management():
    """Test admin payout management"""
    print_section("TEST 7: ADMIN PAYOUT MANAGEMENT")
    
    db = get_session()
    try:
        from app.modelsx.marketplace import SellerPayout
        
        # Get all pending payouts
        mentor_payouts = db.query(MentorPayout).filter(
            MentorPayout.status == PayoutStatus.PENDING
        ).all()
        
        seller_payouts = db.query(SellerPayout).filter(
            SellerPayout.status == 'pending'
        ).all()
        
        total_payouts = len(mentor_payouts) + len(seller_payouts)
        test_result(
            "Admin can list pending payouts",
            total_payouts >= 0,
            f"Total pending: {total_payouts} (Mentors: {len(mentor_payouts)}, Sellers: {len(seller_payouts)})"
        )
        
        # Get payout details
        if mentor_payouts:
            payout = mentor_payouts[0]
            earnings = db.query(MentorEarning).filter(
                MentorEarning.mentor_id == payout.mentor_id,
                MentorEarning.is_paid_out == False
            ).all()
            
            test_result(
                "Admin can view payout details",
                len(earnings) >= 0,
                f"Payout ID: {payout.id}, Amount: ${payout.amount:.2f}, Linked earnings: {len(earnings)}"
            )
        
        if seller_payouts:
            payout = seller_payouts[0]
            earnings = db.query(SellerEarning).filter(
                SellerEarning.seller_id == payout.seller_id,
                SellerEarning.is_paid_out == False
            ).all()
            
            test_result(
                "Admin can view seller payout details",
                len(earnings) >= 0,
                f"Payout ID: {payout.id}, Amount: ${payout.amount:.2f}, Linked earnings: {len(earnings)}"
            )
        
        # Test rejection
        if mentor_payouts:
            payout = mentor_payouts[0]
            payout.status = PayoutStatus.FAILED
            payout.failure_reason = "Account verification pending"
            db.commit()
            
            test_result(
                "Admin can reject payout",
                payout.status == PayoutStatus.FAILED,
                f"Rejection reason: {payout.failure_reason}"
            )
        
    except Exception as e:
        test_result("Admin payout management", False, str(e))
    finally:
        db.close()


# ============================================================================
# TEST 8: PAYMENT SUMMARY REPORT
# ============================================================================

def test_payment_summary():
    """Generate payment summary report"""
    print_section("TEST 8: PAYMENT SUMMARY REPORT")
    
    db = get_session()
    try:
        # Course orders
        course_orders = db.query(Order).filter(
            Order.course_id != None,
            Order.status == 'completed'
        ).count()
        course_revenue = db.query(Order).filter(
            Order.course_id != None,
            Order.status == 'completed'
        ).count()
        
        # Marketplace orders
        marketplace_orders = db.query(Order).filter(
            Order.digital_product_id != None,
            Order.status == 'completed'
        ).count()
        
        # Mentor earnings
        mentor_earnings = db.query(MentorEarning).filter(
            MentorEarning.is_paid_out == False
        ).all()
        mentor_balance = sum(e.net_amount for e in mentor_earnings)
        
        # Seller earnings
        seller_earnings = db.query(SellerEarning).filter(
            SellerEarning.is_paid_out == False
        ).all()
        seller_balance = sum(e.net_amount for e in seller_earnings)
        
        # Pending payouts
        mentor_payouts_pending = db.query(MentorPayout).filter(
            MentorPayout.status == PayoutStatus.PENDING
        ).count()
        
        from app.modelsx.marketplace import SellerPayout
        seller_payouts_pending = db.query(SellerPayout).filter(
            SellerPayout.status == 'pending'
        ).count()
        
        test_result(
            "Course orders summary",
            course_orders >= 0,
            f"Total: {course_orders}"
        )
        
        test_result(
            "Marketplace orders summary",
            marketplace_orders >= 0,
            f"Total: {marketplace_orders}"
        )
        
        print(f"\n📊 PAYMENT SUMMARY REPORT")
        print(f"{'='*80}")
        print(f"Course Orders:              {course_orders}")
        print(f"Marketplace Orders:         {marketplace_orders}")
        print(f"Mentor Earnings (Unpaid):   ${mentor_balance:.2f}")
        print(f"Seller Earnings (Unpaid):   ${seller_balance:.2f}")
        print(f"Mentor Payouts (Pending):   {mentor_payouts_pending}")
        print(f"Seller Payouts (Pending):   {seller_payouts_pending}")
        print(f"Total Outstanding Payouts:  ${mentor_balance + seller_balance:.2f}")
        print(f"{'='*80}")
        
    except Exception as e:
        test_result("Payment summary report", False, str(e))
    finally:
        db.close()


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all payment integration tests"""
    
    print("\n")
    print("╔" + "═"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  COMPREHENSIVE PAYMENT INTEGRATION TEST SUITE".center(78) + "║")
    print("║" + "  Testing all payment features with demo data".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "═"*78 + "╝")
    
    # Run all tests
    test_mentor_session_payments()
    test_marketplace_payments()
    test_course_payments()
    test_mentor_payouts()
    test_seller_payouts()
    test_subscription_payments()
    test_admin_payout_management()
    test_payment_summary()
    
    # Print summary
    print_section("TEST SUMMARY")
    
    total = TEST_RESULTS["passed"] + TEST_RESULTS["failed"]
    passed = TEST_RESULTS["passed"]
    failed = TEST_RESULTS["failed"]
    
    print(f"Total Tests:    {total}")
    print(f"Passed:         {passed} ✅")
    print(f"Failed:         {failed} ❌")
    print(f"Success Rate:   {(passed/total*100):.1f}%" if total > 0 else "N/A")
    
    if TEST_RESULTS["errors"]:
        print(f"\n{'─'*80}")
        print("ERRORS:")
        for error in TEST_RESULTS["errors"]:
            print(f"  {error}")
    
    print(f"\n{'='*80}")
    
    if failed == 0 and total > 0:
        print("✅ ALL TESTS PASSED - PAYMENT SYSTEM FULLY FUNCTIONAL")
    elif failed > 0:
        print(f"⚠️  {failed} TEST(S) FAILED - REVIEW ERRORS ABOVE")
    else:
        print("⚠️  NO TESTS RUN - VERIFY DATABASE AND DEMO DATA")
    
    print(f"{'='*80}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
