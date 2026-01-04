'use client'

import { useState } from 'react'
import { CreditCard, Lock, Check, AlertCircle } from 'lucide-react'
import { Button } from './Button'

interface PaymentFormProps {
  amount: number
  currency?: string
  description?: string
  bookingId?: number
  onSuccess?: () => void
  onError?: (error: string) => void
}

interface CardData {
  cardNumber: string
  cardHolder: string
  expiryDate: string
  cvc: string
}

export function PaymentForm({
  amount,
  currency = 'USD',
  description = 'SkillForge Global Payment',
  bookingId,
  onSuccess,
  onError
}: PaymentFormProps) {
  const [cardData, setCardData] = useState<CardData>({
    cardNumber: '',
    cardHolder: '',
    expiryDate: '',
    cvc: ''
  })
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [agreedToTerms, setAgreedToTerms] = useState(false)

  const handleCardNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\s/g, '')
    if (!/^\d*$/.test(value)) return
    if (value.length > 16) return
    value = value.replace(/(\d{4})/g, '$1 ').trim()
    setCardData({ ...cardData, cardNumber: value })
  }

  const handleExpiryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value.replace(/\D/g, '')
    if (value.length >= 2) {
      value = value.slice(0, 2) + '/' + value.slice(2, 4)
    }
    setCardData({ ...cardData, expiryDate: value })
  }

  const handleCVCChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4)
    setCardData({ ...cardData, cvc: value })
  }

  const validateForm = () => {
    if (!cardData.cardNumber.replace(/\s/g, '') || cardData.cardNumber.length < 19) {
      return 'Please enter a valid card number'
    }
    if (!cardData.cardHolder.trim()) {
      return 'Please enter the cardholder name'
    }
    if (!cardData.expiryDate || cardData.expiryDate.length < 5) {
      return 'Please enter a valid expiry date'
    }
    if (!cardData.cvc || cardData.cvc.length < 3) {
      return 'Please enter a valid CVV'
    }
    if (!agreedToTerms) {
      return 'Please agree to the terms'
    }
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      onError?.(validationError)
      return
    }

    setLoading(true)
    setError('')

    try {
      const endpoint = bookingId 
        ? `/api/v1x/payments/process-booking`
        : `/api/v1x/payments/process`

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8002'}${endpoint}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            amount,
            currency,
            bookingId,
            description,
            card: {
              number: cardData.cardNumber.replace(/\s/g, ''),
              holder: cardData.cardHolder,
              expiry: cardData.expiryDate,
              cvc: cardData.cvc
            }
          })
        }
      )

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Payment processing failed')
      }

      const result = await response.json()
      setSuccess(true)
      onSuccess?.()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Payment failed'
      setError(errorMessage)
      onError?.(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="bg-gradient-to-br from-[#0B0A13] to-[#1a1625] border border-green-500/20 rounded-lg p-8 text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center">
            <Check size={32} className="text-green-400" />
          </div>
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Payment Successful!</h2>
        <p className="text-white/60 mb-2">
          Your payment of {currency} {amount.toFixed(2)} has been processed
        </p>
        <p className="text-white/40 text-sm">
          A confirmation has been sent to your email. Your booking is now confirmed.
        </p>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Payment Summary */}
      <div className="bg-white/5 border border-white/10 rounded-lg p-4">
        <p className="text-white/60 text-sm mb-1">Amount to pay</p>
        <p className="text-3xl font-bold text-white">
          {currency} {amount.toFixed(2)}
        </p>
        <p className="text-white/40 text-xs mt-2">{description}</p>
      </div>

      {/* Card Details */}
      <div className="space-y-4">
        <h3 className="text-white font-semibold flex items-center gap-2">
          <CreditCard size={20} />
          Card Details
        </h3>

        {/* Card Number */}
        <div>
          <label className="block text-white text-sm font-medium mb-2">
            Card Number
          </label>
          <input
            type="text"
            placeholder="1234 5678 9012 3456"
            value={cardData.cardNumber}
            onChange={handleCardNumberChange}
            maxLength={19}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
          <p className="text-white/40 text-xs mt-1">No spaces - just 16 digits</p>
        </div>

        {/* Cardholder Name */}
        <div>
          <label className="block text-white text-sm font-medium mb-2">
            Cardholder Name
          </label>
          <input
            type="text"
            placeholder="John Doe"
            value={cardData.cardHolder}
            onChange={(e) => setCardData({ ...cardData, cardHolder: e.target.value })}
            className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Expiry and CVV */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              Expiry Date
            </label>
            <input
              type="text"
              placeholder="MM/YY"
              value={cardData.expiryDate}
              onChange={handleExpiryChange}
              maxLength={5}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-white text-sm font-medium mb-2">
              CVV
            </label>
            <input
              type="text"
              placeholder="123"
              value={cardData.cvc}
              onChange={handleCVCChange}
              maxLength={4}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Security Notice */}
      <div className="flex items-start gap-3 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
        <Lock size={16} className="text-blue-400 flex-shrink-0 mt-0.5" />
        <p className="text-blue-300 text-xs">
          Your payment information is encrypted and secure. We never store your full card details.
        </p>
      </div>

      {/* Terms Agreement */}
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          id="terms"
          checked={agreedToTerms}
          onChange={(e) => setAgreedToTerms(e.target.checked)}
          className="mt-1 rounded border-white/20"
        />
        <label htmlFor="terms" className="text-white/70 text-sm">
          I agree to the payment terms and confirm this booking. I understand that this charge is non-refundable.
        </label>
      </div>

      {/* Error Message */}
      {error && (
        <div className="flex items-start gap-3 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <AlertCircle size={16} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-400 font-medium text-sm">Payment Error</p>
            <p className="text-red-300 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={loading || !agreedToTerms}
        size="lg"
        className="w-full"
      >
        {loading ? (
          <>
            <span className="inline-block animate-spin mr-2">⏳</span>
            Processing Payment...
          </>
        ) : (
          <>
            <Lock size={16} className="mr-2" />
            Pay {currency} {amount.toFixed(2)}
          </>
        )}
      </Button>

      {/* Additional Info */}
      <p className="text-white/40 text-xs text-center">
        For testing: Use card 4242 4242 4242 4242 with any future date
      </p>
    </form>
  )
}
