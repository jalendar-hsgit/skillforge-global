import { useEffect, useState } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import Layout from '@/components/Layout'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { loadStripe } from '@stripe/stripe-js'
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js'
import { useMe } from '@/hooks/useMe'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'
const STRIPE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''

function SubscribeForm() {
  const stripe = useStripe()
  const elements = useElements()
  const router = useRouter()
  const { me } = useMe()

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const plan = (router.query.plan as string) || 'pro'
  const cycle = (router.query.cycle as string) || 'monthly'

  useEffect(() => {
    if (!me) {
      // If not logged in, redirect to login
      router.replace(`/login?next=/subscribe?plan=${plan}&cycle=${cycle}`)
    }
  }, [me, plan, cycle, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!stripe || !elements) return

    try {
      setLoading(true)

      const card = elements.getElement(CardElement)
      if (!card) throw new Error('Payment element not ready')

      const pmResult = await stripe.createPaymentMethod({
        type: 'card',
        card
      })

      if (pmResult.error || !pmResult.paymentMethod) {
        throw new Error(pmResult.error?.message || 'Failed to create payment method')
      }

      const token = document.cookie
        .split('; ')
        .find(r => r.startsWith('token='))
        ?.split('=')[1]

      if (!token) throw new Error('Not authenticated')

      const res = await fetch(`${API_BASE}/api/v1x/subscriptions/subscribe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          plan: plan.toUpperCase(),
          billing_cycle: cycle,
          payment_method_id: pmResult.paymentMethod.id
        })
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data?.detail || 'Subscription failed')
      }

      // Success! Go to dashboard
      router.replace('/dashboard')
    } catch (err: any) {
      setError(err?.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="max-w-lg mx-auto p-8">
      <h1 className="text-2xl font-bold mb-2">Subscribe to {plan?.toUpperCase()}</h1>
      <p className="text-sm text-gray-600 mb-6">Billing: {cycle === 'annual' ? 'Annual (save 17%)' : 'Monthly'}</p>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Card details</label>
          <div className="border rounded-md p-3 bg-white">
            <CardElement options={{ hidePostalCode: true }} />
          </div>
        </div>

        {error && (
          <div className="text-red-600 text-sm mb-3">{error}</div>
        )}

        <Button type="submit" variant="primary" className="w-full" disabled={!stripe || loading}>
          {loading ? 'Processing...' : 'Start Subscription'}
        </Button>
      </form>
    </Card>
  )
}

export default function SubscribePage() {
  const stripePromise = loadStripe(STRIPE_PUBLISHABLE_KEY)

  return (
    <Layout>
      <Head><title>Subscribe – SkillForge Global</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <Elements stripe={stripePromise}>
          <SubscribeForm />
        </Elements>
      </section>
    </Layout>
  )
}
