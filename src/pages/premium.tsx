import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";
import { Check } from "lucide-react";

interface Tier {
  id: number;
  name: string;
  tier_type: string;
  description: string;
  monthly_price: number;
  yearly_price: number;
  lifetime_price: number | null;
  display_order: number;
  color: string;
  icon: string;
  is_popular: boolean;
  quotas: {
    max_coding_submissions_per_day: number;
    max_code_snippets: number;
    max_learning_paths: number;
    max_ai_hints_per_day: number;
    max_storage_gb: number;
  };
  features: {
    advanced_analytics: boolean;
    ai_code_review: boolean;
    video_tutorials: boolean;
    mentorship: boolean;
    certification: boolean;
    early_access: boolean;
    priority_support: boolean;
    custom_learning_paths: boolean;
  };
  benefits: Array<{
    id: number;
    feature_name: string;
    feature_description: string;
    icon: string;
    order: number;
  }>;
}

interface UserSubscription {
  subscription: any;
  tier: Tier;
  is_active: boolean;
  days_until_renewal: number | null;
}

export default function PricingPage() {
  const router = useRouter();
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [currentSub, setCurrentSub] = useState<UserSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "yearly">("monthly");

  useEffect(() => {
    fetchTiers();
    fetchCurrentSubscription();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/subscriptions/tiers`
      );
      const data = await response.json();
      setTiers(data.tiers || []);
    } catch (error) {
      console.error("Failed to fetch tiers:", error);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/subscriptions/me`,
        { credentials: "include" }
      );
      if (response.ok) {
        const data = await response.json();
        setCurrentSub(data);
      }
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch subscription:", error);
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/subscriptions/upgrade`,
        {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tier_id: tierId,
            billing_period: billingPeriod
          })
        }
      );
      if (response.ok) {
        await fetchCurrentSubscription();
        // TODO: Redirect to payment or show success message
      }
    } catch (error) {
      console.error("Failed to upgrade:", error);
    }
  };

  const getTierBadgeColor = (color: string) => {
    const colors: Record<string, string> = {
      green: "bg-green-500",
      blue: "bg-blue-500",
      purple: "bg-purple-500",
      gold: "bg-yellow-500"
    };
    return colors[color] || "bg-gray-500";
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading pricing plans...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const currentTierId = currentSub?.tier?.id;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="text-center mb-12">
            <SectionHeading className="text-white mb-4">Choose Your Plan</SectionHeading>
            <p className="text-slate-300 text-lg max-w-2xl mx-auto mb-8">
              Start free and upgrade whenever you need advanced features. All plans include access to our community and core platform features.
            </p>

            {/* Billing Toggle */}
            <div className="flex justify-center gap-4 mb-12">
              <button
                onClick={() => setBillingPeriod("monthly")}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  billingPeriod === "monthly"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
              >
                Monthly
              </button>
              <button
                onClick={() => setBillingPeriod("yearly")}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  billingPeriod === "yearly"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
              >
                Yearly
                <span className="ml-2 text-xs bg-green-600 px-2 py-1 rounded">Save 20%</span>
              </button>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {tiers.map(tier => {
              const price = billingPeriod === "yearly" ? tier.yearly_price : tier.monthly_price;
              const isCurrent = currentTierId === tier.id;

              return (
                <Card
                  key={tier.id}
                  className={`relative flex flex-col h-full transition ${
                    isCurrent
                      ? "bg-gradient-to-b from-blue-900/50 to-slate-800 border-2 border-blue-500 shadow-lg shadow-blue-500/20"
                      : "bg-slate-800 border-slate-700 hover:border-blue-500/50"
                  } ${tier.is_popular ? "lg:scale-105" : ""}`}
                >
                  {/* Popular Badge */}
                  {tier.is_popular && (
                    <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-1/2">
                      <span className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-1 rounded-full text-xs font-bold">
                        Most Popular
                      </span>
                    </div>
                  )}

                  {/* Current Badge */}
                  {isCurrent && (
                    <div className="absolute top-4 left-4">
                      <span className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        ✓ Current Plan
                      </span>
                    </div>
                  )}

                  <div className="pt-6">
                    {/* Icon & Name */}
                    <div className="text-4xl mb-3">{tier.icon}</div>
                    <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
                    <p className="text-slate-400 text-sm mb-4 min-h-10">{tier.description}</p>

                    {/* Pricing */}
                    <div className="mb-6 py-6 border-t border-b border-slate-700">
                      <div className="flex items-baseline gap-2">
                        <span className="text-4xl font-bold text-white">${price}</span>
                        <span className="text-slate-400">
                          {billingPeriod === "monthly" ? "/mo" : "/year"}
                        </span>
                      </div>
                      {billingPeriod === "yearly" && (
                        <p className="text-xs text-green-400 mt-2">
                          Save ${((tier.monthly_price * 12) - tier.yearly_price).toFixed(2)}/year
                        </p>
                      )}
                    </div>

                    {/* CTA Button */}
                    <div className="mb-6">
                      {isCurrent ? (
                        <button className="w-full px-4 py-2 bg-slate-700 text-white rounded-lg font-medium cursor-default">
                          Your Current Plan
                        </button>
                      ) : (
                        <Button
                          className="w-full"
                          onClick={() => handleUpgrade(tier.id)}
                        >
                          {currentTierId && tier.display_order > (tiers.find(t => t.id === currentTierId)?.display_order || 0)
                            ? "Upgrade"
                            : currentTierId
                            ? "Downgrade"
                            : "Get Started"}
                        </Button>
                      )}
                    </div>

                    {/* Quotas */}
                    <div className="space-y-2 mb-6 pb-6 border-b border-slate-700">
                      <h4 className="text-sm font-semibold text-slate-300">Quotas</h4>
                      <div className="text-xs text-slate-400 space-y-1">
                        <div>📝 {tier.quotas.max_coding_submissions_per_day} submissions/day</div>
                        <div>📚 {tier.quotas.max_code_snippets} code snippets</div>
                        <div>🎯 {tier.quotas.max_learning_paths} learning paths</div>
                        <div>💡 {tier.quotas.max_ai_hints_per_day} AI hints/day</div>
                        <div>💾 {tier.quotas.max_storage_gb}GB storage</div>
                      </div>
                    </div>

                    {/* Features */}
                    <div className="space-y-3">
                      {tier.benefits.map(benefit => (
                        <div key={benefit.id} className="flex items-start gap-3">
                          <Check className="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1">
                            <div className="text-sm font-medium text-white">
                              {benefit.feature_name}
                            </div>
                            {benefit.feature_description && (
                              <div className="text-xs text-slate-400">
                                {benefit.feature_description}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* FAQ Section */}
          <div className="mt-16 max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-white mb-8 text-center">Frequently Asked Questions</h2>
            <div className="space-y-4">
              {[
                {
                  q: "Can I change my plan anytime?",
                  a: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
                },
                {
                  q: "Do you offer a free trial?",
                  a: "Yes, start with our Free tier to explore all core features before upgrading to a paid plan."
                },
                {
                  q: "What payment methods do you accept?",
                  a: "We accept all major credit cards through Stripe. Additional payment methods coming soon."
                },
                {
                  q: "Is there a yearly discount?",
                  a: "Yes, yearly billing saves you 20% compared to monthly billing."
                }
              ].map((faq, index) => (
                <Card key={index} className="bg-slate-800 border-slate-700">
                  <h3 className="font-semibold text-white mb-2">{faq.q}</h3>
                  <p className="text-slate-400">{faq.a}</p>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
