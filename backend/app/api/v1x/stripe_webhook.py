"""
Stripe Webhook Handler
Receives and processes events from Stripe in real-time
"""
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import stripe
import json

from app.core.db import get_db
from app.core.config import settings
from app.modelsx.order import Order
from app.modelsx.mentor import MentorSession, SessionStatus
from app.modelsx.progress import VideoProgress
from app.modelsx.video import Video
from app.modelsx.course import Course
from app.modelsx.marketplace import SellerEarning, DigitalProduct
from app.modelsx.payout import MentorEarning
from app.services.email_service import email_service

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)

router = APIRouter(prefix="", tags=["webhook"])


@router.post("/webhook/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    Events handled:
    - payment_intent.succeeded: Order payment successful
    - charge.refunded: Refund processed
    - payment_intent.payment_failed: Payment failed
    - payment_intent.canceled: Payment canceled
    """
    
    # Get webhook signature from header
    sig_header = request.headers.get("stripe-signature")
    body = await request.body()
    
    if not stripe.api_key:
        print("WARNING: Stripe is not configured. Set STRIPE_SECRET_KEY in environment.")
        return {"status": "webhook active but Stripe not configured"}
    
    # Verify webhook signature
    try:
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                body, 
                sig_header, 
                webhook_secret
            )
        else:
            # If no webhook secret configured, still process but log warning
            event = json.loads(body)
            print("WARNING: STRIPE_WEBHOOK_SECRET not set. Webhook signature not verified!")
    
    except ValueError as e:
        print(f"Invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print(f"Invalid signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event.get('type')
    event_data = event.get('data', {}).get('object', {})
    
    print(f"Received Stripe webhook: {event_type}")
    
    try:
        # Handle payment_intent.succeeded event
        if event_type == 'payment_intent.succeeded':
            payment_intent_id = event_data.get('id')
            amount = event_data.get('amount') / 100  # Convert cents to dollars
            metadata = event_data.get('metadata', {})
            
            print(f"Processing payment_intent.succeeded: {payment_intent_id}, amount: ${amount}")
            
            # Check if this is a course order payment
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order:
                print(f"Found order {order.id} ({order.order_number}), updating status")
                
                # Update order status
                order.status = 'completed'
                order.payment_status = 'completed'
                order.paid_at = datetime.utcnow()
                
                # Determine if this is a course or marketplace order
                is_course_order = order.course_id is not None
                
                # Enroll user in course (if course purchase)
                if is_course_order:
                    print(f"Creating VideoProgress for user {order.user_id}, course {order.course_id}")
                    
                    # Get all videos in course
                    videos = db.query(Video).filter(
                        Video.course_id == order.course_id
                    ).all()
                    
                    print(f"Found {len(videos)} videos to create progress for")
                    
                    for video in videos:
                        # Check if progress already exists
                        existing = db.query(VideoProgress).filter(
                            VideoProgress.user_id == order.user_id,
                            VideoProgress.video_id == video.id
                        ).first()
                        
                        if not existing:
                            progress = VideoProgress(
                                user_id=order.user_id,
                                video_id=video.id,
                                progress_percent=0,
                                completed=False,
                                created_at=datetime.utcnow()
                            )
                            db.add(progress)
                            print(f"Created VideoProgress for video {video.id}")
                
                db.commit()
                print(f"Order {order.id} updated successfully")
                
                # Create earning records
                try:
                    if is_course_order:
                        # Course orders: Platform keeps 100% (no seller earnings)
                        print(f"Course order - no seller earnings created")
                    else:
                        # Marketplace order: Create SellerEarning record
                        # Get the digital product and seller
                        if order.digital_product_id:
                            product = db.query(DigitalProduct).filter(
                                DigitalProduct.id == order.digital_product_id
                            ).first()
                            
                            if product and product.seller_id:
                                # Calculate 80/20 split (seller gets 80%)
                                gross_amount = float(order.amount)
                                platform_fee = gross_amount * 0.20  # Platform: 20%
                                net_amount = gross_amount * 0.80    # Seller: 80%
                                
                                seller_earning = SellerEarning(
                                    seller_id=product.seller_id,
                                    order_id=order.id,
                                    product_id=order.digital_product_id,
                                    gross_amount=gross_amount,
                                    platform_fee=platform_fee,
                                    net_amount=net_amount,
                                    earned_at=datetime.utcnow()
                                )
                                db.add(seller_earning)
                                db.commit()
                                print(f"Created SellerEarning: seller={product.seller_id}, amount=${net_amount:.2f}")
                except Exception as e:
                    print(f"Failed to create earning records: {e}")
                
                # Send confirmation email (course or marketplace)
                try:
                    if is_course_order:
                        # Send course order confirmation
                        course_title = order.course.title if order.course else "Digital Product"
                        await email_service.send_order_confirmation(
                            to_email=order.user.email,
                            user_name=order.user.name or "Student",
                            course_title=course_title,
                            order_id=order.id,
                            order_number=order.order_number,
                            amount=float(order.amount),
                            order_date=order.created_at
                        )
                        print(f"Course order confirmation email sent to {order.user.email}")
                    else:
                        # This is a marketplace order - send marketplace receipt
                        # Note: In a production system, you'd load the actual product names
                        product_names = ["Digital Product(s)"]  # Would fetch actual product names
                        await email_service.send_marketplace_order_confirmation(
                            to_email=order.user.email,
                            user_name=order.user.name or "Customer",
                            product_names=product_names,
                            order_id=order.id,
                            order_number=order.order_number,
                            amount=float(order.amount),
                            order_date=order.created_at
                        )
                        print(f"Marketplace order confirmation email sent to {order.user.email}")
                except Exception as e:
                    print(f"Failed to send confirmation email: {e}")
            
            # Check if this is a mentor session payment
            session = db.query(MentorSession).filter(
                MentorSession.payment_intent_id == payment_intent_id
            ).first()
            
            if session:
                print(f"Found mentor session {session.id}, updating payment status")
                
                session.payment_status = 'paid'
                session.status = SessionStatus.CONFIRMED  # Confirm the session after payment
                
                # Create MentorEarning record for mentor session payment
                try:
                    # Calculate 80/20 split (mentor gets 80%)
                    gross_amount = session.price
                    platform_fee = gross_amount * 0.20   # Platform: 20%
                    net_amount = gross_amount * 0.80      # Mentor: 80%
                    
                    mentor_earning = MentorEarning(
                        mentor_id=session.mentor_id,
                        session_id=session.id,
                        gross_amount=gross_amount,
                        platform_fee=platform_fee,
                        net_amount=net_amount,
                        earned_at=datetime.utcnow()
                    )
                    db.add(mentor_earning)
                    print(f"Created MentorEarning: mentor={session.mentor_id}, amount=${net_amount:.2f}")
                except Exception as e:
                    print(f"Failed to create mentor earning: {e}")
                
                db.commit()
                
                print(f"Session {session.id} payment status updated to 'paid' and status to 'confirmed'")
        
        # Handle charge.refunded event
        elif event_type == 'charge.refunded':
            payment_intent_id = event_data.get('payment_intent')
            amount = event_data.get('amount_refunded') / 100 if event_data.get('amount_refunded') else None
            
            print(f"Processing charge.refunded: payment_intent {payment_intent_id}, amount refunded: ${amount}")
            
            # Find and update order
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order:
                order.status = 'refunded'
                order.payment_status = 'refunded'
                db.commit()
                print(f"Order {order.id} marked as refunded")
                
                # Send refund email
                try:
                    email_service.send_refund_notification(
                        to_email=order.user.email,
                        order_number=order.order_number,
                        amount=float(order.amount)
                    )
                    print(f"Refund notification sent to {order.user.email}")
                except Exception as e:
                    print(f"Failed to send refund email: {e}")
        
        # Handle payment_intent.payment_failed event
        elif event_type == 'payment_intent.payment_failed':
            payment_intent_id = event_data.get('id')
            last_payment_error = event_data.get('last_payment_error', {})
            error_message = last_payment_error.get('message', 'Unknown error')
            
            print(f"Processing payment_intent.payment_failed: {payment_intent_id}, error: {error_message}")
            
            # Find and update order
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order:
                order.status = 'failed'
                order.payment_status = 'failed'
                db.commit()
                print(f"Order {order.id} marked as failed")
                
                # Send failure email
                try:
                    email_service.send_payment_failed(
                        to_email=order.user.email,
                        order_number=order.order_number,
                        error_message=error_message
                    )
                    print(f"Payment failed notification sent to {order.user.email}")
                except Exception as e:
                    print(f"Failed to send payment failed email: {e}")
        
        # Handle payment_intent.canceled event
        elif event_type == 'payment_intent.canceled':
            payment_intent_id = event_data.get('id')
            
            print(f"Processing payment_intent.canceled: {payment_intent_id}")
            
            # Find and update order
            order = db.query(Order).filter(
                Order.payment_intent_id == payment_intent_id
            ).first()
            
            if order and order.status == 'pending':
                order.status = 'cancelled'
                order.payment_status = 'cancelled'
                db.commit()
                print(f"Order {order.id} cancelled")
        
        return {"status": "success", "event_id": event.get('id')}
    
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        # Don't raise error - Stripe expects 200 response even on error
        # Log the error for debugging
        return {"status": "error", "message": str(e), "event_id": event.get('id')}


@router.get("/webhook/stripe/test")
async def test_webhook():
    """Test endpoint to verify webhook is working"""
    return {
        "status": "webhook endpoint is active",
        "stripe_configured": stripe.api_key is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
