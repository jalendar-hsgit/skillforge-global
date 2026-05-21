import { useState, useEffect } from 'react'
import Head from "next/head"
import { useRouter } from 'next/router'
import Layout from "@/components/Layout"
import { Card } from "@/components/Card"
import { Button } from "@/components/Button"
import { PageHeader, PageSection } from "@/components/PageLayout"
import { useMe } from '@/hooks/useMe'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001'

type Tier = {
  plan: string
  name: string
  monthlyPrice: number
  annualPrice: number
  blurb: string
  cta: string
  highlight?: boolean
  features: string[]
}

const tiers: Tier[] = [
  {
    plan: "free",
    name: "Free",
    monthlyPrice: 0,
    annualPrice: 0,
    blurb: "Perfect for getting started with learning",
    cta: "Get Started",
    features: [
      "Access to all learning paths",
      "Basic quizzes & progress tracking",
      "AI assistant access",
      "2 mentor sessions per month (30 min)",
      "Community support"
    ]
  },
  {
    plan: "pro",
    name: "Pro",
    monthlyPrice: 29,
    annualPrice: 290,
    blurb: "For serious learners who want unlimited access",
    cta: "Upgrade to Pro",
    highlight: true,
    features: [
      "Everything in Free",
      "Unlimited mentor sessions (2 hours max)",
      "File sharing in chat",
      "Session recording & replay",
      "Priority booking",
      "Email support"
    ]
  },
  {
    plan: "enterprise",
    name: "Enterprise",
    monthlyPrice: 99,
    annualPrice: 990,
    blurb: "For teams and organizations",
    cta: "Contact Sales",
    features: [
      "Everything in Pro",
      "Extended sessions (4 hours max)",
      "Team dashboard & analytics",
      "Custom learning paths",
      "Dedicated account manager",
      "Priority 24/7 support"
    ]
  }
]

export default function PricingPage() {
  const router = useRouter()
  const { me } = useMe()
  const [currentPlan, setCurrentPlan] = useState<string | null>(null)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly')

  const loadCurrentSubscription = async () => {
    try {
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1]

      if (!token) return

      const response = await fetch(`${API_BASE}/api/v1x/subscriptions/current`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentPlan(data.plan)
      }
    } catch (error) {
      console.error('Error loading subscription:', error)
    }
  }

  useEffect(() => {
    if (me) {
      loadCurrentSubscription()
    }
  }, [me])

  const handleSelectPlan = (plan: string) => {
    if (!me) {
      router.push('/login')
      return
    }

    if (plan === 'free') {
      return
    }

    if (plan === 'enterprise') {
      window.location.href = 'mailto:sales@skillforge.global'
      return
    }

    router.push(`/subscribe?plan=${plan}&cycle=${billingCycle}`)
  }

  const formatPrice = (tier: Tier) => {
    const price = billingCycle === 'annual' ? tier.annualPrice / 12 : tier.monthlyPrice
    return `$${Math.round(price)}`
  }

  return (
    <Layout>
      <Head><title>Pricing – SkillForge Global</title></Head>
      <section className="mx-auto max-w-7xl px-6 pt-36 pb-20">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, transparent pricing</h1>
          <p className="text-xl text-gray-600 mb-8">Start free. Upgrade anytime. Cancel anytime.</p>

          <div className="inline-flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                billingCycle === 'annual'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Annual
              <span className="ml-2 text-xs text-green-600 font-bold">Save 17%</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map(tier => (
            <Card
              key={tier.plan}
              className={`p-8 ${
                tier.highlight
                  ? 'ring-2 ring-blue-600 relative'
                  : 'ring-1 ring-gray-200'
              }`}
            >
              {tier.highlight && (
                <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                  <span className="bg-blue-600 text-white text-sm font-bold px-4 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
                <p className="text-gray-600 text-sm">{tier.blurb}</p>
              </div>

              <div className="mb-6">
                <div className="flex items-baseline">
                  <span className="text-5xl font-bold text-gray-900">
                    {formatPrice(tier)}
                  </span>
                  {tier.monthlyPrice > 0 && (
                    <span className="text-gray-600 ml-2">/month</span>
                  )}
                </div>
                {billingCycle === 'annual' && tier.annualPrice > 0 && (
                  <p className="text-sm text-gray-500 mt-1">
                    ${tier.annualPrice} billed annually
                  </p>
                )}
              </div>

              <Button
                onClick={() => handleSelectPlan(tier.plan)}
                variant={tier.highlight ? 'primary' : 'secondary'}
                className="w-full mb-6"
                disabled={currentPlan === tier.plan}
              >
                {currentPlan === tier.plan ? 'Current Plan' : tier.cta}
              </Button>

              <ul className="space-y-3">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <svg
                      className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-gray-700 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </Card>
          ))}
        </div>

        <div className="mt-20">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-10">
            Frequently Asked Questions
          </h2>
          <div className="max-w-3xl mx-auto space-y-6">
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Can I switch plans anytime?
              </h3>
              <p className="text-gray-600">
                Yes! You can upgrade, downgrade, or cancel your subscription at any time. 
                Changes take effect immediately or at the end of your billing period.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-600">
                We accept all major credit cards (Visa, Mastercard, American Express) via Stripe.
                All payments are secure and encrypted.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Is there a refund policy?
              </h3>
              <p className="text-gray-600">
                Yes, we offer a 14-day money-back guarantee. If you're not satisfied with your 
                subscription, contact us within 14 days for a full refund.
              </p>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Do mentor sessions cost extra?
              </h3>
              <p className="text-gray-600">
                Mentor sessions are charged separately based on the mentor's hourly rate. 
                Your subscription determines session duration limits and monthly quotas.
              </p>
            </Card>
          </div>
        </div>

        <div className="mt-20 text-center">
          <Card className="p-12 bg-gradient-to-r from-blue-50 to-purple-50">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to start learning?
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of learners accelerating their tech careers
            </p>
            <Button
              onClick={() => router.push('/signup')}
              variant="primary"
              className="text-lg px-8 py-3"
            >
              Start Free Trial
            </Button>
          </Card>
        </div>
      </section>
    </Layout>
  )
}
