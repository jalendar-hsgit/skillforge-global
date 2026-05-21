"""
Payment Integration Module
Support for Stripe and PayPal payment processing
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel
import os
import stripe
import hmac
import json
import hashlib
from urllib.request import Request as URLRequest


class PaymentProvider(str, Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    INTERNAL = "internal"  # For testing/demo


class PaymentStatus(str, Enum):
    """Payment status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentRequest(BaseModel):
    """Payment request model"""
    order_id: int
    amount: float
    currency: str = "USD"
    payment_method: str  # stripe, paypal, etc
    customer_email: str
    description: str = "Marketplace Purchase"


class PaymentResponse(BaseModel):
    """Payment response model"""
    payment_id: str
    order_id: int
    status: PaymentStatus
    amount: float
    currency: str
    provider: PaymentProvider
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class PaymentProcessor:
    """Base payment processor interface"""
    
    def __init__(self, provider: PaymentProvider):
        self.provider = provider
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process a payment"""
        raise NotImplementedError
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> PaymentResponse:
        """Refund a payment"""
        raise NotImplementedError
    
    def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get payment status"""
        raise NotImplementedError


class StripeProcessor(PaymentProcessor):
    """Stripe payment processor"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(PaymentProvider.STRIPE)
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
        stripe.api_key = self.api_key
        self.stripe = stripe
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process payment via Stripe.
        
        Creates a PaymentIntent and processes the payment.
        """
        
        try:
            # Create a payment intent
            intent = self.stripe.PaymentIntent.create(
                amount=int(float(request.amount) * 100),  # Convert to cents
                currency=request.currency.lower(),
                payment_method_types=["card"],
                metadata={
                    "order_id": request.order_id,
                    "customer_email": request.customer_email,
                    "description": request.description
                },
                description=request.description,
                receipt_email=request.customer_email
            )
            
            payment_id = intent.id
            status = PaymentStatus.COMPLETED if intent.status == "succeeded" else PaymentStatus.PROCESSING
            
            return PaymentResponse(
                payment_id=payment_id,
                order_id=request.order_id,
                status=status,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "stripe_charge_id": intent.get("charges", {}).data[0].id if intent.get("charges") else None,
                    "customer_email": request.customer_email,
                    "description": request.description,
                    "intent_id": intent.id,
                    "intent_status": intent.status,
                    "client_secret": intent.client_secret
                }
            )
        
        except self.stripe.error.CardError as e:
            # Card was declined
            return PaymentResponse(
                payment_id=f"stripe_error_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": e.user_message,
                    "error_code": e.code,
                    "customer_email": request.customer_email
                }
            )
        
        except self.stripe.error.RateLimitError:
            # Too many requests made to the API too quickly
            return PaymentResponse(
                payment_id=f"stripe_ratelimit_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.PROCESSING,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": "Rate limit exceeded, please try again",
                    "customer_email": request.customer_email
                }
            )
        
        except self.stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            return PaymentResponse(
                payment_id=f"stripe_invalid_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": str(e),
                    "customer_email": request.customer_email
                }
            )
        
        except self.stripe.error.AuthenticationError:
            # Authentication with Stripe's API failed
            return PaymentResponse(
                payment_id=f"stripe_auth_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": "Authentication failed",
                    "customer_email": request.customer_email
                }
            )
        
        except self.stripe.error.StripeError as e:
            # Generic Stripe error
            return PaymentResponse(
                payment_id=f"stripe_error_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": str(e),
                    "customer_email": request.customer_email
                }
            )
        
        except Exception as e:
            # Unknown error
            return PaymentResponse(
                payment_id=f"error_{request.order_id}",
                order_id=request.order_id,
                status=PaymentStatus.FAILED,
                amount=request.amount,
                currency=request.currency,
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "error": str(e),
                    "customer_email": request.customer_email
                }
            )
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> PaymentResponse:
        """Refund a Stripe payment"""
        
        try:
            # Refund the charge
            refund_data = {}
            if amount:
                refund_data["amount"] = int(float(amount) * 100)  # Convert to cents
            
            # Payment ID could be either a PaymentIntent ID or Charge ID
            # Try to refund by PaymentIntent first, then by Charge
            try:
                intent = self.stripe.PaymentIntent.retrieve(payment_id)
                if intent.charges.data:
                    charge_id = intent.charges.data[0].id
                    refund = self.stripe.Refund.create(charge=charge_id, **refund_data)
                else:
                    raise ValueError("No charges found for this payment intent")
            except:
                # Try as a charge ID directly
                refund = self.stripe.Refund.create(charge=payment_id, **refund_data)
            
            return PaymentResponse(
                payment_id=refund.id,
                order_id=0,
                status=PaymentStatus.REFUNDED,
                amount=float(refund.amount) / 100,
                currency=refund.currency.upper() if refund.currency else "USD",
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "refund_id": refund.id,
                    "refund_status": refund.status,
                    "reason": refund.reason
                }
            )
        
        except Exception as e:
            return PaymentResponse(
                payment_id=payment_id,
                order_id=0,
                status=PaymentStatus.FAILED,
                amount=0,
                currency="USD",
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )
    
    def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get Stripe payment status"""
        
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_id)
            
            # Map Stripe status to our status
            status_map = {
                "succeeded": PaymentStatus.COMPLETED,
                "processing": PaymentStatus.PROCESSING,
                "requires_payment_method": PaymentStatus.PENDING,
                "requires_action": PaymentStatus.PENDING,
                "requires_confirmation": PaymentStatus.PENDING,
                "canceled": PaymentStatus.CANCELLED,
            }
            
            status = status_map.get(intent.status, PaymentStatus.PENDING)
            
            charge_id = None
            amount = float(intent.amount) / 100 if intent.amount else 0
            
            if intent.charges.data:
                charge_id = intent.charges.data[0].id
            
            return PaymentResponse(
                payment_id=payment_id,
                order_id=intent.metadata.get("order_id") if intent.metadata else 0,
                status=status,
                amount=amount,
                currency=intent.currency.upper() if intent.currency else "USD",
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={
                    "intent_status": intent.status,
                    "charge_id": charge_id,
                    "client_secret": intent.client_secret
                }
            )
        
        except Exception as e:
            return PaymentResponse(
                payment_id=payment_id,
                order_id=0,
                status=PaymentStatus.PENDING,
                amount=0,
                currency="USD",
                provider=PaymentProvider.STRIPE,
                timestamp=datetime.utcnow(),
                metadata={"error": str(e)}
            )


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processor"""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        super().__init__(PaymentProvider.PAYPAL)
        self.client_id = client_id or "placeholder_client_id"
        self.client_secret = client_secret or "placeholder_client_secret"
        # In production: import paypalrestsdk; setup auth
        self.paypal = None  # Placeholder for PayPal SDK
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process payment via PayPal.
        
        In production, this would:
        1. Create a PayPal order
        2. Handle PayPal approval
        3. Capture the payment
        4. Return transaction ID
        """
        
        # TODO: Integrate actual PayPal API
        # For now, simulate successful payment
        
        payment_id = f"paypal_{request.order_id}_{int(datetime.utcnow().timestamp())}"
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=request.order_id,
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            provider=PaymentProvider.PAYPAL,
            timestamp=datetime.utcnow(),
            metadata={
                "paypal_transaction_id": f"txn_{payment_id}",
                "customer_email": request.customer_email,
                "description": request.description
            }
        )
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> PaymentResponse:
        """Refund a PayPal payment"""
        
        # TODO: Integrate actual PayPal refund API
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=0,
            status=PaymentStatus.REFUNDED,
            amount=amount or 0,
            currency="USD",
            provider=PaymentProvider.PAYPAL,
            timestamp=datetime.utcnow(),
            metadata={"refund_processed": True}
        )
    
    def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get PayPal payment status"""
        
        # TODO: Query PayPal API for actual status
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=0,
            status=PaymentStatus.COMPLETED,
            amount=0,
            currency="USD",
            provider=PaymentProvider.PAYPAL,
            timestamp=datetime.utcnow()
        )


class InternalProcessor(PaymentProcessor):
    """Internal payment processor for testing/demo"""
    
    def __init__(self):
        super().__init__(PaymentProvider.INTERNAL)
    
    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """Process payment internally (for testing)"""
        
        payment_id = f"internal_{request.order_id}_{int(datetime.utcnow().timestamp())}"
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=request.order_id,
            status=PaymentStatus.COMPLETED,
            amount=request.amount,
            currency=request.currency,
            provider=PaymentProvider.INTERNAL,
            timestamp=datetime.utcnow(),
            metadata={
                "test_mode": True,
                "customer_email": request.customer_email
            }
        )
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> PaymentResponse:
        """Refund internal payment"""
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=0,
            status=PaymentStatus.REFUNDED,
            amount=amount or 0,
            currency="USD",
            provider=PaymentProvider.INTERNAL,
            timestamp=datetime.utcnow(),
            metadata={"test_mode": True}
        )
    
    def get_payment_status(self, payment_id: str) -> PaymentResponse:
        """Get internal payment status"""
        
        return PaymentResponse(
            payment_id=payment_id,
            order_id=0,
            status=PaymentStatus.COMPLETED,
            amount=0,
            currency="USD",
            provider=PaymentProvider.INTERNAL,
            timestamp=datetime.utcnow(),
            metadata={"test_mode": True}
        )


class PaymentFactory:
    """Factory for creating payment processors"""
    
    _processors = {
        PaymentProvider.STRIPE: StripeProcessor,
        PaymentProvider.PAYPAL: PayPalProcessor,
        PaymentProvider.INTERNAL: InternalProcessor,
    }
    
    @classmethod
    def create(
        cls,
        provider: str,
        **kwargs
    ) -> PaymentProcessor:
        """
        Create a payment processor.
        
        Args:
            provider: Payment provider name (stripe, paypal, internal)
            **kwargs: Provider-specific configuration
        
        Returns:
            PaymentProcessor instance
        
        Raises:
            ValueError: If provider not supported
        """
        
        provider_enum = PaymentProvider(provider.lower())
        processor_class = cls._processors.get(provider_enum)
        
        if not processor_class:
            raise ValueError(f"Unsupported payment provider: {provider}")
        
        return processor_class(**kwargs)


# Convenience function
def get_payment_processor(
    provider: str = "stripe",
    **kwargs
) -> PaymentProcessor:
    """Get a payment processor instance"""
    return PaymentFactory.create(provider, **kwargs)
