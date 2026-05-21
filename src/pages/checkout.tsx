import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Link from 'next/link';
import { apiGet } from '@/lib/api';
import { createOrder, createPaymentIntent } from '@/lib/orderApi';
import { getStripe } from '@/lib/stripe';
import styles from '@/styles/checkout.module.css';

interface Course {
  id: number;
  path?: string;
  title: string;
  description?: string;
  price: number;
  is_paid: boolean;
}

interface User {
  id: number;
  email: string;
  name?: string;
}

export default function CheckoutPage() {
  const router = useRouter();
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [step, setStep] = useState<'select' | 'payment' | 'confirmation'>('select');
  const [orderId, setOrderId] = useState<number | null>(null);
  const [paymentIntentId, setPaymentIntentId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [processing, setProcessing] = useState(false);

  // Load courses and user on mount
  useEffect(() => {
    loadCoursesAndUser();
  }, []);

  const loadCoursesAndUser = async () => {
    try {
      setLoading(true);
      const coursesResponse = await apiGet('/api/v1x/courses-db');
      const userResponse = await apiGet('/api/v1x/auth/me');

      const paidCourses = coursesResponse.data?.filter((c: Course) => c.is_paid) || [];
      setCourses(paidCourses);
      setUser(userResponse.data || userResponse);
      setError('');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to load courses';
      setError(errorMsg);
      // If user is not logged in, redirect to login
      if (errorMsg.includes('401') || errorMsg.includes('unauthorized')) {
        setTimeout(() => router.push('/auth/login'), 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCourse = async (course: Course) => {
    setSelectedCourse(course);
    setError('');

    try {
      setProcessing(true);

      // Create order
      const orderResponse = await createOrder(course.id, 'stripe');
      if (!orderResponse.success) {
        throw new Error(orderResponse.message || 'Failed to create order');
      }

      const newOrderId = orderResponse.data.id;
      setOrderId(newOrderId);

      // Create payment intent
      const piResponse = await createPaymentIntent(newOrderId);
      if (!piResponse.success) {
        throw new Error(piResponse.message || 'Failed to create payment intent');
      }

      setPaymentIntentId(piResponse.data.payment_intent_id);
      setClientSecret(piResponse.data.client_secret);
      setStep('payment');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  const handlePaymentSuccess = (result: any) => {
    setStep('confirmation');
    setError('');
  };

  const handlePaymentError = (error: string) => {
    setError(error);
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <Head>
          <title>Checkout - SkillForge Global</title>
        </Head>
        <div className={styles.loading}>Loading courses...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className={styles.container}>
        <Head>
          <title>Checkout - SkillForge Global</title>
        </Head>
        <div className={styles.error}>
          <p>Please log in to checkout.</p>
          <Link href="/auth/login">
            <button className={styles.button}>Go to Login</button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Head>
        <title>Checkout - SkillForge Global</title>
      </Head>

      <div className={styles.checkout}>
        <h1>Course Checkout</h1>

        {error && <div className={styles.errorMessage}>{error}</div>}

        {step === 'select' && (
          <div className={styles.courseSelection}>
            <h2>Select a Course</h2>
            <div className={styles.courseGrid}>
              {courses.map((course) => (
                <div key={course.id} className={styles.courseCard}>
                  <div className={styles.courseInfo}>
                    <h3>{course.title}</h3>
                    {course.description && <p>{course.description}</p>}
                    <div className={styles.price}>
                      ${course.price?.toFixed(2) || '0.00'}
                    </div>
                  </div>
                  <button
                    onClick={() => handleSelectCourse(course)}
                    disabled={processing}
                    className={styles.selectButton}
                  >
                    {processing ? 'Processing...' : 'Enroll Now'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 'payment' && selectedCourse && orderId && (
          <div className={styles.paymentSection}>
            <h2>Payment Details</h2>
            <div className={styles.orderSummary}>
              <h3>{selectedCourse.title}</h3>
              <p>Price: ${selectedCourse.price?.toFixed(2) || '0.00'}</p>
              <p>Order ID: {orderId}</p>
            </div>

            <div className={styles.paymentInfo}>
              <h3>Pay with Stripe</h3>
              <p>Test Card: 4242 4242 4242 4242</p>
              <p>Expiry: 12/25 | CVC: 123</p>
            </div>

            <StripePaymentForm
              orderId={orderId}
              amount={Math.round((selectedCourse.price || 0) * 100)}
              currency="usd"
              clientSecret={clientSecret}
              paymentIntentId={paymentIntentId}
              onSuccess={handlePaymentSuccess}
              onError={handlePaymentError}
            />

            <button
              onClick={() => setStep('select')}
              className={styles.backButton}
            >
              Back to Courses
            </button>
          </div>
        )}

        {step === 'confirmation' && selectedCourse && (
          <div className={styles.confirmation}>
            <div className={styles.successIcon}>✓</div>
            <h2>Payment Successful!</h2>
            <p>Thank you for your purchase of <strong>{selectedCourse.title}</strong></p>
            <p>Your access has been activated.</p>

            <div className={styles.confirmationActions}>
              <Link href={`/courses/${selectedCourse.path || selectedCourse.id}`}>
                <button className={styles.primaryButton}>Go to Course</button>
              </Link>
              <Link href="/dashboard">
                <button className={styles.secondaryButton}>Back to Dashboard</button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Inline Stripe Payment Form Component
interface StripePaymentFormProps {
  orderId: number;
  amount: number;
  currency: string;
  clientSecret: string;
  paymentIntentId: string;
  onSuccess: (result: any) => void;
  onError: (error: string) => void;
}

function StripePaymentForm({
  orderId,
  amount,
  currency,
  clientSecret,
  paymentIntentId,
  onSuccess,
  onError,
}: StripePaymentFormProps) {
  const [cardNumber, setCardNumber] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvc, setCvc] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\s/g, '');
    if (!/^\d*$/.test(value)) return;
    if (value.length > 16) return;
    value = value.replace(/(\d{4})/g, '$1 ').trim();
    setCardNumber(value);
  };

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '');
    if (value.length >= 2) {
      value = value.slice(0, 2) + '/' + value.slice(2, 4);
    }
    setExpiry(value);
  };

  const handleCvcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setCvc(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProcessing(true);
    setError('');

    try {
      // Simulate payment processing
      // In production, use Stripe.js for secure payment handling
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Call the confirmation endpoint
      const response = await fetch('/api/v1x/orders/confirm-payment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          order_id: orderId,
          payment_intent_id: paymentIntentId,
        }),
      });

      const result = await response.json();
      if (result.success) {
        onSuccess(result);
      } else {
        setError(result.message || 'Payment failed');
        onError(result.message || 'Payment failed');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Payment processing failed';
      setError(errorMsg);
      onError(errorMsg);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <div className={styles.formGroup}>
        <label>Card Number</label>
        <input
          type="text"
          value={cardNumber}
          onChange={handleCardNumberChange}
          placeholder="4242 4242 4242 4242"
          disabled={processing}
        />
      </div>

      <div className={styles.formRow}>
        <div className={styles.formGroup}>
          <label>Expiry Date</label>
          <input
            type="text"
            value={expiry}
            onChange={handleExpiryChange}
            placeholder="MM/YY"
            disabled={processing}
          />
        </div>
        <div className={styles.formGroup}>
          <label>CVC</label>
          <input
            type="text"
            value={cvc}
            onChange={handleCvcChange}
            placeholder="123"
            disabled={processing}
          />
        </div>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <button
        type="submit"
        disabled={processing}
        className={styles.submitButton}
      >
        {processing ? 'Processing...' : `Pay $${(amount / 100).toFixed(2)}`}
      </button>
    </form>
  );
}
