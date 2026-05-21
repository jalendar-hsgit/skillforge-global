'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import styles from '../styles/mentor-booking.module.css';
import {
  getMentors,
  searchMentors,
  getAvailableSlots,
  bookSession,
  getMyBookings,
  MentorProfile,
  AvailabilitySlot,
  SessionBookingRequest,
  MentorSession,
} from '../lib/mentorBookingApi';
import { createOrder, createPaymentIntent, confirmPayment } from '../lib/orderApi';
import { apiGet } from '../lib/api';

type Step = 'mentors' | 'slots' | 'payment' | 'confirmation';

interface BookingState {
  selectedMentor: MentorProfile | null;
  selectedDate: string;
  selectedTime: string;
  duration: number;
  topic: string;
  description: string;
}

export default function MentorBookingPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('mentors');
  const [mentors, setMentors] = useState<MentorProfile[]>([]);
  const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [searchExpertise, setSearchExpertise] = useState('');

  // Booking details state
  const [booking, setBooking] = useState<BookingState>({
    selectedMentor: null,
    selectedDate: '',
    selectedTime: '',
    duration: 60,
    topic: '',
    description: '',
  });

  // Payment state
  const [orderId, setOrderId] = useState<number | null>(null);
  const [paymentIntentId, setPaymentIntentId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [processing, setProcessing] = useState(false);
  const [bookingResult, setBookingResult] = useState<MentorSession | null>(null);

  // Card form state
  const [cardNumber, setCardNumber] = useState('');
  const [expiry, setExpiry] = useState('');
  const [cvc, setCvc] = useState('');
  const [cardName, setCardName] = useState('');

  // Load mentors on mount
  useEffect(() => {
    loadMentorsAndUser();
  }, []);

  const loadMentorsAndUser = async () => {
    try {
      setLoading(true);
      const user = (await apiGet('/api/v1x/auth/me')).data;
      setCurrentUser(user);

      const mentorsList = await getMentors(50);
      setMentors(mentorsList);
    } catch (err) {
      setError('Failed to load mentors');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchMentors = async (expertise: string) => {
    setSearchExpertise(expertise);
    try {
      setLoading(true);
      if (expertise.trim()) {
        const results = await searchMentors(expertise);
        setMentors(results);
      } else {
        const results = await getMentors(50);
        setMentors(results);
      }
    } catch (err) {
      setError('Search failed');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectMentor = async (mentor: MentorProfile) => {
    try {
      setLoading(true);
      setBooking({ ...booking, selectedMentor: mentor });

      // Load available slots for this mentor
      const slots = await getAvailableSlots(mentor.id);
      setAvailableSlots(slots);
      setStep('slots');
    } catch (err) {
      setError('Failed to load availability');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSlot = (slot: AvailabilitySlot) => {
    setBooking({
      ...booking,
      selectedDate: slot.date || new Date().toISOString().split('T')[0],
      selectedTime: slot.start_time,
    });
  };

  const handleContinueToPayment = async () => {
    if (!booking.selectedMentor || !booking.selectedDate || !booking.selectedTime || !booking.topic) {
      setError('Please complete all booking details');
      return;
    }

    try {
      setProcessing(true);
      setError('');

      // Create order for mentor session
      const order = await createOrder(booking.selectedMentor.id, 'mentor_session');
      setOrderId(order.data.id);

      // Create payment intent
      const piData = await createPaymentIntent(order.data.id);
      setPaymentIntentId(piData.data.payment_intent_id);
      setClientSecret(piData.data.client_secret);

      setStep('payment');
    } catch (err) {
      setError('Failed to prepare payment');
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  const formatCardNumber = (value: string) => {
    return value.replace(/\s/g, '').replace(/(\d{4})/g, '$1 ').trim().slice(0, 19);
  };

  const formatExpiry = (value: string) => {
    const cleaned = value.replace(/\D/g, '').slice(0, 4);
    if (cleaned.length >= 2) {
      return `${cleaned.slice(0, 2)}/${cleaned.slice(2)}`;
    }
    return cleaned;
  };

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCardNumber(formatCardNumber(e.target.value));
  };

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setExpiry(formatExpiry(e.target.value));
  };

  const handleCvcChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setCvc(value);
  };

  const handlePaymentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!cardNumber || !expiry || !cvc || !cardName) {
      setError('Please fill in all card details');
      return;
    }

    if (cardNumber.replace(/\s/g, '').length !== 16) {
      setError('Card number must be 16 digits');
      return;
    }

    const [month, year] = expiry.split('/');
    if (!month || !year) {
      setError('Please enter a valid expiry date');
      return;
    }

    if (cvc.length < 3) {
      setError('CVC must be 3-4 digits');
      return;
    }

    try {
      setProcessing(true);
      setError('');

      // Confirm payment
      const result = await confirmPayment(orderId!, paymentIntentId, cardNumber.slice(-4));

      if (result.success) {
        // Book the mentor session
        const scheduledAt = new Date(`${booking.selectedDate}T${booking.selectedTime}`).toISOString();

        const sessionRequest: SessionBookingRequest = {
          mentor_id: booking.selectedMentor!.id,
          topic: booking.topic,
          description: booking.description,
          scheduled_at: scheduledAt,
          duration_minutes: booking.duration,
        };

        const session = await bookSession(sessionRequest);
        setBookingResult(session);
        setStep('confirmation');
      } else {
        setError('Payment failed: ' + result.message);
      }
    } catch (err) {
      setError('Payment processing failed');
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  const handleViewBookings = () => {
    router.push('/mentor-bookings');
  };

  const handleBackToMentors = () => {
    setStep('mentors');
    setBooking({
      selectedMentor: null,
      selectedDate: '',
      selectedTime: '',
      duration: 60,
      topic: '',
      description: '',
    });
    setError('');
  };

  if (loading && step === 'mentors') {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading mentors...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.bookingPage}>
        {/* Step 1: Select Mentor */}
        {step === 'mentors' && (
          <div className={styles.step}>
            <h1 className={styles.title}>Find Your Mentor</h1>
            <p className={styles.subtitle}>
              Choose from our network of expert mentors and schedule a session
            </p>

            <div className={styles.searchBox}>
              <input
                type="text"
                placeholder="Search by expertise (e.g., python-ai, web-dev)"
                value={searchExpertise}
                onChange={(e) => handleSearchMentors(e.target.value)}
                className={styles.searchInput}
              />
            </div>

            {error && <div className={styles.error}>{error}</div>}

            <div className={styles.mentorGrid}>
              {mentors.length > 0 ? (
                mentors.map((mentor) => (
                  <div key={mentor.id} className={styles.mentorCard}>
                    <div className={styles.mentorHeader}>
                      <h3>{mentor.user.full_name}</h3>
                      <span className={styles.rating}>⭐ {mentor.average_rating || 'N/A'}</span>
                    </div>
                    <p className={styles.bio}>{mentor.bio}</p>
                    <div className={styles.expertise}>
                      <strong>Expertise:</strong> {mentor.expertise}
                    </div>
                    <div className={styles.mentorFooter}>
                      <span className={styles.rate}>${mentor.hourly_rate}/hr</span>
                      <button
                        onClick={() => handleSelectMentor(mentor)}
                        className={styles.selectButton}
                      >
                        Select
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className={styles.noResults}>No mentors found</p>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Select Time Slot */}
        {step === 'slots' && booking.selectedMentor && (
          <div className={styles.step}>
            <h1 className={styles.title}>Schedule Your Session</h1>
            <p className={styles.subtitle}>With {booking.selectedMentor.user.full_name}</p>

            <div className={styles.bookingForm}>
              <div className={styles.formGroup}>
                <label>Session Topic *</label>
                <input
                  type="text"
                  placeholder="e.g., Python fundamentals, Web development setup"
                  value={booking.topic}
                  onChange={(e) => setBooking({ ...booking, topic: e.target.value })}
                  className={styles.formInput}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Description</label>
                <textarea
                  placeholder="Additional details about your needs..."
                  value={booking.description}
                  onChange={(e) => setBooking({ ...booking, description: e.target.value })}
                  className={styles.formTextarea}
                  rows={3}
                />
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Date *</label>
                  <input
                    type="date"
                    value={booking.selectedDate}
                    onChange={(e) => setBooking({ ...booking, selectedDate: e.target.value })}
                    className={styles.formInput}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>Time *</label>
                  <input
                    type="time"
                    value={booking.selectedTime}
                    onChange={(e) => setBooking({ ...booking, selectedTime: e.target.value })}
                    className={styles.formInput}
                  />
                </div>
              </div>

              <div className={styles.formGroup}>
                <label>Duration (minutes) *</label>
                <select
                  value={booking.duration}
                  onChange={(e) => setBooking({ ...booking, duration: parseInt(e.target.value) })}
                  className={styles.formSelect}
                >
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={90}>1.5 hours</option>
                  <option value={120}>2 hours</option>
                </select>
              </div>

              <div className={styles.priceEstimate}>
                <p>
                  Estimated Cost:{' '}
                  <strong>${((booking.selectedMentor.hourly_rate * booking.duration) / 60).toFixed(2)}</strong>
                </p>
              </div>

              {error && <div className={styles.error}>{error}</div>}

              <div className={styles.buttonGroup}>
                <button onClick={handleBackToMentors} className={styles.backButton}>
                  Back
                </button>
                <button
                  onClick={handleContinueToPayment}
                  disabled={processing}
                  className={styles.submitButton}
                >
                  {processing ? 'Processing...' : 'Continue to Payment'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Payment */}
        {step === 'payment' && booking.selectedMentor && (
          <div className={styles.step}>
            <h1 className={styles.title}>Complete Payment</h1>
            <p className={styles.subtitle}>
              Secure payment for your session with {booking.selectedMentor.user.full_name}
            </p>

            <form onSubmit={handlePaymentSubmit} className={styles.paymentForm}>
              <div className={styles.formGroup}>
                <label>Full Name *</label>
                <input
                  type="text"
                  placeholder="John Doe"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  className={styles.formInput}
                />
              </div>

              <div className={styles.formGroup}>
                <label>Card Number *</label>
                <input
                  type="text"
                  placeholder="4242 4242 4242 4242"
                  value={cardNumber}
                  onChange={handleCardNumberChange}
                  className={styles.formInput}
                  maxLength={19}
                />
              </div>

              <div className={styles.formRow}>
                <div className={styles.formGroup}>
                  <label>Expiry Date *</label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    value={expiry}
                    onChange={handleExpiryChange}
                    className={styles.formInput}
                    maxLength={5}
                  />
                </div>

                <div className={styles.formGroup}>
                  <label>CVC *</label>
                  <input
                    type="text"
                    placeholder="123"
                    value={cvc}
                    onChange={handleCvcChange}
                    className={styles.formInput}
                    maxLength={4}
                  />
                </div>
              </div>

              <div className={styles.orderSummary}>
                <h3>Order Summary</h3>
                <div className={styles.summaryRow}>
                  <span>Mentor:</span>
                  <strong>{booking.selectedMentor.user.full_name}</strong>
                </div>
                <div className={styles.summaryRow}>
                  <span>Session Date:</span>
                  <strong>{booking.selectedDate} at {booking.selectedTime}</strong>
                </div>
                <div className={styles.summaryRow}>
                  <span>Duration:</span>
                  <strong>{booking.duration} minutes</strong>
                </div>
                <div className={styles.summaryRow}>
                  <span>Rate:</span>
                  <strong>${booking.selectedMentor.hourly_rate}/hr</strong>
                </div>
                <div className={styles.totalRow}>
                  <span>Total:</span>
                  <strong>${((booking.selectedMentor.hourly_rate * booking.duration) / 60).toFixed(2)}</strong>
                </div>
              </div>

              {error && <div className={styles.error}>{error}</div>}

              <div className={styles.buttonGroup}>
                <button
                  type="button"
                  onClick={() => setStep('slots')}
                  className={styles.backButton}
                  disabled={processing}
                >
                  Back
                </button>
                <button type="submit" disabled={processing} className={styles.submitButton}>
                  {processing ? 'Processing Payment...' : `Pay $${((booking.selectedMentor.hourly_rate * booking.duration) / 60).toFixed(2)}`}
                </button>
              </div>
            </form>

            <div className={styles.paymentInfo}>
              <p>
                <strong>Test Card:</strong> 4242 4242 4242 4242 | Any date | Any CVC
              </p>
            </div>
          </div>
        )}

        {/* Step 4: Confirmation */}
        {step === 'confirmation' && bookingResult && (
          <div className={styles.confirmation}>
            <div className={styles.checkmark}>✓</div>
            <h1 className={styles.title}>Booking Confirmed!</h1>
            <p className={styles.subtitle}>Your mentor session has been scheduled</p>

            <div className={styles.confirmationDetails}>
              <div className={styles.detailRow}>
                <span>Session ID:</span>
                <strong>#{bookingResult.id}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Mentor:</span>
                <strong>{booking.selectedMentor?.user.full_name}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Topic:</span>
                <strong>{bookingResult.topic}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Scheduled For:</span>
                <strong>{new Date(bookingResult.scheduled_at).toLocaleString()}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Duration:</span>
                <strong>{bookingResult.duration_minutes} minutes</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Status:</span>
                <strong className={styles.statusPending}>{bookingResult.status}</strong>
              </div>
              <div className={styles.detailRow}>
                <span>Amount Paid:</span>
                <strong>${bookingResult.price.toFixed(2)}</strong>
              </div>
            </div>

            <div className={styles.nextSteps}>
              <h3>What's Next?</h3>
              <ul>
                <li>You'll receive a confirmation email shortly</li>
                <li>The mentor will confirm or suggest alternative times</li>
                <li>A meeting link will be sent closer to the session time</li>
                <li>Check your dashboard for all booking details</li>
              </ul>
            </div>

            <div className={styles.buttonGroup}>
              <button onClick={handleViewBookings} className={styles.submitButton}>
                View My Bookings
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
