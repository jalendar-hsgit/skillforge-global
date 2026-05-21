import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";
import { Card } from "@/components/Card";
import Button from "@/components/Button";
import SectionHeading from "@/components/SectionHeading";
import { Check, X } from "lucide-react";

interface Tier {
  id: number;
  name: string;
  tier_type: string;
  monthly_price: number;
  yearly_price: number;
  quotas: {
    max_coding_submissions_per_day: number;
    max_code_snippets: number;
    max_learning_paths: number;
    max_ai_hints_per_day: number;
    max_storage_gb: number;
  };
  features: Record<string, boolean>;
}

export default function ComparePlans() {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/subscriptions/tiers`
      );
      const data = await response.json();
      setTiers(data.tiers || []);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch tiers:", error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
          <div className="text-center text-white">
            <p>Loading comparison...</p>
          </div>
        </div>
      </Layout>
    );
  }

  const featuresList = [
    { category: "Submissions", key: "max_coding_submissions_per_day", label: "Coding Submissions/Day" },
    { category: "Resources", key: "max_code_snippets", label: "Code Snippets" },
    { category: "Resources", key: "max_learning_paths", label: "Learning Paths" },
    { category: "Resources", key: "max_ai_hints_per_day", label: "AI Hints/Day" },
    { category: "Resources", key: "max_storage_gb", label: "Storage (GB)" },
    { category: "Features", key: "advanced_analytics", label: "Advanced Analytics" },
    { category: "Features", key: "ai_code_review", label: "AI Code Review" },
    { category: "Features", key: "video_tutorials", label: "Video Tutorials" },
    { category: "Features", key: "mentorship", label: "Mentorship Access" },
    { category: "Features", key: "certification", label: "Certification" },
    { category: "Features", key: "early_access", label: "Early Access Features" },
    { category: "Features", key: "priority_support", label: "Priority Support" },
    { category: "Features", key: "custom_learning_paths", label: "Custom Learning Paths" }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <div className="text-center mb-12">
            <SectionHeading className="text-white mb-4">Plan Comparison</SectionHeading>
            <p className="text-slate-300 text-lg max-w-2xl mx-auto">
              Compare all features and quotas across our subscription plans
            </p>
          </div>

          {/* Comparison Table */}
          <div className="overflow-x-auto">
            <table className="w-full min-w-max">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-4 px-4 text-white font-semibold">Feature</th>
                  {tiers.map(tier => (
                    <th key={tier.id} className="text-center py-4 px-4 text-white font-semibold">
                      {tier.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {featuresList.map((feature, index) => {
                  const category = feature.category as "Submissions" | "Resources" | "Features";
                  
                  return (
                    <tr
                      key={feature.key}
                      className={`border-b border-slate-700 ${
                        index % 2 === 0 ? "bg-slate-800/30" : ""
                      }`}
                    >
                      <td className="py-4 px-4 text-slate-300 font-medium text-sm">
                        {feature.label}
                      </td>
                      {tiers.map(tier => {
                        let value = null;
                        
                        if (category === "Submissions" || category === "Resources") {
                          const quotaValue = tier.quotas[feature.key as keyof typeof tier.quotas];
                          value = quotaValue !== undefined ? (
                            <span className="text-white font-semibold">{quotaValue}</span>
                          ) : (
                            "-"
                          );
                        } else if (category === "Features") {
                          const featureValue = tier.features[feature.key];
                          value = featureValue ? (
                            <Check className="w-5 h-5 text-green-400 mx-auto" />
                          ) : (
                            <X className="w-5 h-5 text-slate-600 mx-auto" />
                          );
                        }

                        return (
                          <td key={tier.id} className="text-center py-4 px-4">
                            {value}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* CTA Section */}
          <div className="mt-12 text-center">
            <Button className="text-lg px-8 py-4">
              View All Plans and Pricing
            </Button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
