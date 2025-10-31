"""
Stripe Payment Integration
"""
import stripe
from typing import Dict, Optional
from decimal import Decimal
from app.core.config import settings
from app.modelsx.mentor import MentorSession
from sqlalchemy.orm import Session

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)


class StripeService:
    """Service for handling Stripe payments"""
    
    @staticmethod
    def create_payment_intent(
        amount: float,
        currency: str = "usd",
        session_id: int = None,
        mentor_id: int = None,
        student_id: int = None
    ) -> Dict:
        """
        Create a Stripe PaymentIntent for a mentor session
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            session_id: MentorSession ID
            mentor_id: Mentor ID
            student_id: Student ID
        
        Returns:
            Dict with payment intent details
        """
        if not stripe.api_key:
            raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY in environment.")
        
        try:
            # Convert dollars to cents
            amount_cents = int(amount * 100)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    'session_id': session_id,
                    'mentor_id': mentor_id,
                    'student_id': student_id,
                    'type': 'mentor_session'
                },
                # Enable automatic payment methods
                automatic_payment_methods={
                    'enabled': True
                },
                # Hold funds until session is completed
                capture_method='manual'
            )
            
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': amount,
                'currency': currency,
                'status': intent.status
            }
        
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception(f"Payment failed: {str(e)}")
    
    @staticmethod
    def capture_payment(payment_intent_id: str) -> bool:
        """
        Capture/complete a payment after session is completed
        
        Args:
            payment_intent_id: The PaymentIntent ID
        
        Returns:
            bool: True if successful
        """
        if not stripe.api_key:
            return False
        
        try:
            intent = stripe.PaymentIntent.capture(payment_intent_id)
            return intent.status == 'succeeded'
        
        except stripe.error.StripeError as e:
            print(f"Error capturing payment: {e}")
            return False
    
    @staticmethod
    def cancel_payment(payment_intent_id: str) -> bool:
        """
        Cancel a payment (for cancelled sessions)
        
        Args:
            payment_intent_id: The PaymentIntent ID
        
        Returns:
            bool: True if successful
        """
        if not stripe.api_key:
            return False
        
        try:
            intent = stripe.PaymentIntent.cancel(payment_intent_id)
            return intent.status == 'canceled'
        
        except stripe.error.StripeError as e:
            print(f"Error canceling payment: {e}")
            return False
    
    @staticmethod
    def create_refund(payment_intent_id: str, amount: Optional[float] = None) -> Dict:
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: The PaymentIntent ID
            amount: Amount to refund in dollars (None for full refund)
        
        Returns:
            Dict with refund details
        """
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        
        try:
            refund_params = {'payment_intent': payment_intent_id}
            
            if amount is not None:
                refund_params['amount'] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                'id': refund.id,
                'status': refund.status,
                'amount': refund.amount / 100 if refund.amount else 0
            }
        
        except stripe.error.StripeError as e:
            print(f"Error creating refund: {e}")
            raise Exception(f"Refund failed: {str(e)}")
    
    @staticmethod
    def create_transfer_to_mentor(
        amount: float,
        mentor_stripe_account: str,
        session_id: int
    ) -> Dict:
        """
        Transfer funds to mentor's Stripe Connect account
        
        Args:
            amount: Amount in dollars
            mentor_stripe_account: Mentor's Stripe Connect account ID
            session_id: MentorSession ID
        
        Returns:
            Dict with transfer details
        """
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        
        try:
            # Calculate platform fee (e.g., 15%)
            platform_fee = amount * 0.15
            mentor_amount = amount - platform_fee
            
            transfer = stripe.Transfer.create(
                amount=int(mentor_amount * 100),
                currency='usd',
                destination=mentor_stripe_account,
                metadata={
                    'session_id': session_id,
                    'type': 'mentor_payout'
                }
            )
            
            return {
                'id': transfer.id,
                'amount': mentor_amount,
                'platform_fee': platform_fee,
                'status': 'success'
            }
        
        except stripe.error.StripeError as e:
            print(f"Error creating transfer: {e}")
            raise Exception(f"Transfer failed: {str(e)}")
    
    @staticmethod
    def get_payment_status(payment_intent_id: str) -> Dict:
        """Get the status of a payment"""
        if not stripe.api_key:
            return {'status': 'unknown'}
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                'id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100 if intent.amount else 0,
                'currency': intent.currency
            }
        
        except stripe.error.StripeError as e:
            print(f"Error retrieving payment: {e}")
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> Dict:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            signature: Stripe-Signature header value
        
        Returns:
            Dict: The webhook event data
        """
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
        
        if not webhook_secret:
            raise ValueError("Stripe webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return event
        
        except ValueError as e:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise Exception("Invalid signature")


# Singleton instance
stripe_service = StripeService()
