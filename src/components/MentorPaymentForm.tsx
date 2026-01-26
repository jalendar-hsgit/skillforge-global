/**
 * MentorPaymentForm - Payment form for mentor session bookings
 * Uses Stripe Elements for secure payment collection
 */

import React, { useEffect, useState } from 'react';
import {
  CardElement,
  useStripe,
  useElements,
  Elements,
} from '@stripe/react-stripe-js';
import { useMe } from '@/hooks/useMe';
import axios from 'axios';

interface MentorPaymentFormProps {
  sessionId: number;
  amount: number;
  mentorName: string;
  onPaymentSuccess: (paymentIntentId: string) => void;
  onPaymentError: (error: string) => void;
}

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#9e2146',
    },
  },
};

export const MentorPaymentFormContent: React.FC<MentorPaymentFormProps> = ({
  sessionId,
  amount,
  mentorName,
  onPaymentSuccess,
  onPaymentError,
}) => {
  const stripe = useStripe();
  const elements = useElements();
  const { user } = useMe();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [clientSecret, setClientSecret] = useState('');

  // Create payment intent on component mount
  useEffect(() => {
    const createPaymentIntent = async () => {
      try {
        const response = await axios.post(
          '/api/v1x/payments/create-payment-intent',
          { session_id: sessionId }
        );
        setClientSecret(response.data.client_secret);
      } catch (error: any) {
        setErrorMessage(
          error.response?.data?.detail || 'Failed to initialize payment'
        );
        onPaymentError('Failed to initialize payment');
      }
    };

    if (sessionId) {
      createPaymentIntent();
    }
  }, [sessionId, onPaymentError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      setErrorMessage('Stripe is not loaded');
      return;
    }

    const cardElement = elements.getElement(CardElement);

    if (!cardElement) {
      setErrorMessage('Card element not found');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');

    try {
      // Confirm payment with Stripe
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: cardElement,
          billing_details: {
            name: user?.name || 'Guest',
            email: user?.email,
          },
        },
      });

      if (result.error) {
        // Show error to user
        setErrorMessage(result.error.message || 'Payment failed');
        onPaymentError(result.error.message || 'Payment failed');
      } else if (result.paymentIntent?.status === 'succeeded') {
        // Payment successful
        onPaymentSuccess(result.paymentIntent.id);
      } else if (result.paymentIntent?.status === 'requires_action') {
        // Additional authentication required
        setErrorMessage(
          'Additional authentication required. Please complete the verification.'
        );
      }
    } catch (error: any) {
      setErrorMessage(error.message || 'An error occurred');
      onPaymentError(error.message || 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-4">Book Mentor Session</h2>

      <div className="mb-6 p-4 bg-gray-50 rounded">
        <p className="text-sm text-gray-600">Mentor</p>
        <p className="text-lg font-semibold text-gray-900">{mentorName}</p>
        <p className="text-sm text-gray-600 mt-2">Amount</p>
        <p className="text-2xl font-bold text-blue-600">${amount.toFixed(2)}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="p-4 border border-gray-300 rounded">
          <CardElement options={CARD_ELEMENT_OPTIONS} />
        </div>

        {errorMessage && (
          <div className="p-4 bg-red-50 border border-red-200 rounded">
            <p className="text-red-700 text-sm">{errorMessage}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={!stripe || isLoading || !clientSecret}
          className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {isLoading ? 'Processing...' : `Pay $${amount.toFixed(2)}`}
        </button>
      </form>

      <p className="text-xs text-gray-500 mt-4 text-center">
        Your payment information is secure and encrypted
      </p>
    </div>
  );
};

export const MentorPaymentForm: React.FC<MentorPaymentFormProps> = (props) => {
  const { stripePromise } = require('@/lib/stripe');

  return (
    <Elements stripe={stripePromise}>
      <MentorPaymentFormContent {...props} />
    </Elements>
  );
};

export default MentorPaymentForm;
