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
    def retrieve_payment_intent(payment_intent_id: str) -> Dict:
        """
        Retrieve payment intent details from Stripe
        
        Args:
            payment_intent_id: The PaymentIntent ID
        
        Returns:
            Dict with payment intent details
        """
        if not stripe.api_key:
            raise ValueError("Stripe is not configured. Set STRIPE_SECRET_KEY in environment.")
        
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': intent.amount / 100,  # Convert from cents
                'currency': intent.currency,
                'status': intent.status,
                'created': intent.created,
                'metadata': intent.metadata
            }
        
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            raise Exception(f"Failed to retrieve payment intent: {str(e)}")
    
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
    
    @staticmethod
    def create_subscription(
        user_id: int,
        email: str,
        payment_method_id: str,
        plan: str,
        price_cents: int,
        billing_cycle: str = "monthly"
    ) -> Dict:
        """
        Create a Stripe subscription for a user
        
        Args:
            user_id: User ID
            email: User email
            payment_method_id: Stripe payment method ID
            plan: Subscription plan name
            price_cents: Price in cents
            billing_cycle: monthly or annual
        
        Returns:
            Dict with subscription details
        """
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        
        try:
            # Create or retrieve customer
            customer = stripe.Customer.create(
                email=email,
                payment_method=payment_method_id,
                invoice_settings={'default_payment_method': payment_method_id},
                metadata={'user_id': user_id}
            )
            
            # Create price if it doesn't exist (in production, create these manually in Stripe)
            price = stripe.Price.create(
                unit_amount=price_cents,
                currency="usd",
                recurring={
                    "interval": "year" if billing_cycle == "annual" else "month"
                },
                product_data={
                    "name": f"SkillForge {plan.capitalize()} Plan"
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price.id}],
                metadata={
                    'user_id': user_id,
                    'plan': plan
                }
            )
            
            return {
                'id': subscription.id,
                'customer': customer.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end
            }
        
        except stripe.error.StripeError as e:
            print(f"Stripe subscription error: {e}")
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    @staticmethod
    def cancel_subscription(subscription_id: str, cancel_immediately: bool = False) -> bool:
        """
        Cancel a Stripe subscription
        
        Args:
            subscription_id: Stripe subscription ID
            cancel_immediately: Cancel now or at period end
        
        Returns:
            bool: True if successful
        """
        if not stripe.api_key:
            return False
        
        try:
            if cancel_immediately:
                stripe.Subscription.delete(subscription_id)
            else:
                stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            return True
        
        except stripe.error.StripeError as e:
            print(f"Error cancelling subscription: {e}")
            return False
    
    @staticmethod
    def verify_webhook(payload: bytes, signature: str) -> Dict:
        """Alias for verify_webhook_signature for consistency"""
        return StripeService.verify_webhook_signature(payload, signature)

    # ========= Stripe Connect (Mentor payouts) =========
    @staticmethod
    def create_connect_account(email: str, user_id: int) -> Dict:
        """Create a Stripe Connect Express account for a mentor"""
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        try:
            account = stripe.Account.create(
                type="express",
                email=email,
                metadata={"user_id": user_id}
            )
            return account
        except stripe.error.StripeError as e:
            print(f"Stripe Connect create account error: {e}")
            raise Exception(str(e))

    @staticmethod
    def create_connect_onboarding_link(account_id: str, refresh_url: str, return_url: str) -> Dict:
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        try:
            link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type="account_onboarding",
            )
            return link
        except stripe.error.StripeError as e:
            print(f"Stripe Connect onboarding link error: {e}")
            raise Exception(str(e))

    @staticmethod
    def get_connect_account(account_id: str) -> Dict:
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        try:
            return stripe.Account.retrieve(account_id)
        except stripe.error.StripeError as e:
            print(f"Stripe Connect get account error: {e}")
            raise Exception(str(e))

    @staticmethod
    def create_connect_login_link(account_id: str) -> Dict:
        if not stripe.api_key:
            raise ValueError("Stripe is not configured")
        try:
            return stripe.Account.create_login_link(account_id)
        except stripe.error.StripeError as e:
            print(f"Stripe Connect login link error: {e}")
            raise Exception(str(e))


# Singleton instance
stripe_service = StripeService()


# ============================================================
# Helper functions for session payment and mentor payout
# ============================================================

async def process_session_payment(
    session_id: int,
    amount: float,
    student_id: int,
    mentor_id: int,
    db = None
) -> dict:
    """
    Process payment for a mentor session.
    
    Args:
        session_id: The mentor session ID
        amount: Payment amount in dollars
        student_id: Student user ID
        mentor_id: Mentor user ID
        db: Database session (optional)
    
    Returns:
        Dict with payment result
    """
    try:
        result = StripeService.create_payment_intent(
            amount=amount,
            session_id=session_id,
            mentor_id=mentor_id,
            student_id=student_id
        )
        return {
            'success': True,
            'payment_intent_id': result.get('client_secret', '').split('_secret_')[0] if result.get('client_secret') else None,
            'client_secret': result.get('client_secret'),
            'amount': amount
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def process_mentor_payout(
    mentor_id: int,
    amount: float,
    mentor_stripe_account: str = None,
    session_id: int = None,
    db = None
) -> dict:
    """
    Process payout to mentor.
    
    Args:
        mentor_id: Mentor user ID
        amount: Payout amount in dollars
        mentor_stripe_account: Mentor's Stripe Connect account ID
        session_id: Related session ID (optional)
        db: Database session (optional)
    
    Returns:
        Dict with payout result
    """
    if not mentor_stripe_account:
        return {
            'success': False,
            'error': 'Mentor Stripe account not configured'
        }
    
    try:
        result = StripeService.create_transfer_to_mentor(
            amount=amount,
            mentor_stripe_account=mentor_stripe_account,
            session_id=session_id or 0
        )
        return {
            'success': True,
            'transfer_id': result.get('id'),
            'amount': result.get('amount'),
            'platform_fee': result.get('platform_fee')
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

