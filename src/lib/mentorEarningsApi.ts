/**
 * Mentor Earnings API Layer
 * Handles all API calls for mentor earnings, payouts, and payment methods
 */

import { apiGet, apiPost, apiPut, apiDelete } from './api'

/**
 * Payment Method Types
 */
export interface PaymentMethod {
  id: number
  payment_type: 'BANK_ACCOUNT' | 'PAYPAL' | 'STRIPE'
  account_holder_name: string
  bank_name: string
  account_last_four: string
  status: 'PENDING' | 'VERIFIED' | 'REJECTED' | 'INACTIVE'
  is_default: boolean
  verified_at: string | null
  created_at: string
}

export interface CreatePaymentMethodRequest {
  payment_type?: 'BANK_ACCOUNT' | 'PAYPAL' | 'STRIPE'
  account_holder_name: string
  bank_name: string
  account_number: string
  routing_number: string
  is_default?: boolean
}

export interface UpdatePaymentMethodRequest {
  account_holder_name?: string
  bank_name?: string
  is_default?: boolean
}

/**
 * Payout Request Types
 */
export interface PayoutRequest {
  id: number
  amount: number
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'PROCESSING' | 'COMPLETED'
  payment_method_id: number | null
  rejection_reason: string | null
  created_at: string
  updated_at: string
  approved_at: string | null
  completed_at: string | null
}

export interface CreatePayoutRequestPayload {
  amount: number
  payment_method_id?: number
  notes?: string
}

/**
 * Earnings Types
 */
export interface EarningsSummary {
  total_earnings: number
  available_balance: number
  pending_payouts: number
  completed_payouts: number
  total_sessions: number
  completed_sessions: number
  average_session_price: number
  platform_fee_percentage: number
}

export interface EarningDetail {
  id: number
  session_id: number
  student_name: string
  topic: string
  gross_amount: number
  platform_fee: number
  net_amount: number
  earned_at: string
  is_paid_out: boolean
  payout_id: number | null
}

/**
 * Payment Methods API
 */
export const mentorPaymentMethodsApi = {
  /**
   * Add a new payment method (bank account)
   */
  async create(data: CreatePaymentMethodRequest): Promise<PaymentMethod> {
    return apiPost('/api/v1x/mentors/payouts/payment-methods', data)
  },

  /**
   * Get all payment methods for current mentor
   */
  async list(): Promise<PaymentMethod[]> {
    return apiGet('/api/v1x/mentors/payouts/payment-methods')
  },

  /**
   * Update a payment method
   */
  async update(
    id: number,
    data: UpdatePaymentMethodRequest
  ): Promise<PaymentMethod> {
    return apiPut(`/api/v1x/mentors/payouts/payment-methods/${id}`, data)
  },

  /**
   * Delete a payment method
   */
  async delete(id: number): Promise<void> {
    return apiDelete(`/api/v1x/mentors/payouts/payment-methods/${id}`)
  },

  /**
   * Set a payment method as default
   */
  async setDefault(id: number): Promise<PaymentMethod> {
    return this.update(id, { is_default: true })
  },
}

/**
 * Payout Requests API
 */
export const mentorPayoutRequestsApi = {
  /**
   * Create a new payout request
   */
  async create(data: CreatePayoutRequestPayload): Promise<PayoutRequest> {
    return apiPost('/api/v1x/mentors/payouts/payout-request', data)
  },

  /**
   * Get payout request history
   */
  async history(skip: number = 0, limit: number = 50): Promise<PayoutRequest[]> {
    const params = new URLSearchParams()
    params.append('skip', skip.toString())
    params.append('limit', limit.toString())

    return apiGet(`/api/v1x/mentors/payouts/history?${params}`)
  },

  /**
   * Get a specific payout request
   */
  async get(id: number): Promise<PayoutRequest> {
    return apiGet(`/api/v1x/mentors/payouts/${id}`)
  },
}

/**
 * Earnings API
 */
export const mentorEarningsApi = {
  /**
   * Get earnings summary
   */
  async getSummary(): Promise<EarningsSummary> {
    return apiGet('/api/v1x/mentors/payouts/summary')
  },

  /**
   * Get detailed earnings history
   */
  async history(skip: number = 0, limit: number = 50): Promise<EarningDetail[]> {
    const params = new URLSearchParams()
    params.append('skip', skip.toString())
    params.append('limit', limit.toString())

    return apiGet(`/api/v1x/mentors/payouts/earnings?${params}`)
  },

  /**
   * Get completed sessions
   */
  async getCompletedSessions(skip: number = 0, limit: number = 50) {
    const params = new URLSearchParams()
    params.append('skip', skip.toString())
    params.append('limit', limit.toString())

    return apiGet(`/api/v1x/mentors/payouts/sessions/completed?${params}`)
  },
}

/**
 * Combined Mentor Earnings API (all methods)
 */
export const mentorEarningsPageApi = {
  paymentMethods: mentorPaymentMethodsApi,
  payoutRequests: mentorPayoutRequestsApi,
  earnings: mentorEarningsApi,

  /**
   * Load all data needed for payouts page
   */
  async loadAllData() {
    try {
      const [summary, paymentMethods, payoutRequests, earnings] =
        await Promise.all([
          mentorEarningsApi.getSummary(),
          mentorPaymentMethodsApi.list(),
          mentorPayoutRequestsApi.history(0, 10),
          mentorEarningsApi.history(0, 20),
        ])

      return {
        summary,
        paymentMethods,
        payoutRequests,
        earnings,
        success: true,
      }
    } catch (error) {
      console.error('Error loading earnings data:', error)
      throw error
    }
  },
}

export default mentorEarningsPageApi
