import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import Layout from '@/components/Layout';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { useMe } from '@/hooks/useMe';

interface EarningsSummary {
  total_earnings: number;
  available_balance: number;
  pending_payouts: number;
  completed_payouts: number;
  total_sessions: number;
  completed_sessions: number;
  average_session_price: number;
  platform_fee_percentage: number;
}

interface EarningDetail {
  id: number;
  session_id: number;
  student_name: string;
  topic: string;
  gross_amount: number;
  platform_fee: number;
  net_amount: number;
  earned_at: string;
  is_paid_out: boolean;
  payout_id: number | null;
}

interface PayoutDetail {
  id: number;
  amount: number;
  platform_fee: number;
  net_amount: number;
  method: string;
  status: string;
  requested_at: string;
  processed_at: string | null;
  completed_at: string | null;
  failure_reason: string | null;
  earnings_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function MentorEarningsPage() {
  const router = useRouter();
  const { me: user, loading: userLoading } = useMe();
  const [summary, setSummary] = useState<EarningsSummary | null>(null);
  const [earnings, setEarnings] = useState<EarningDetail[]>([]);
  const [payouts, setPayouts] = useState<PayoutDetail[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'earnings' | 'payouts'>('overview');
  const [requestAmount, setRequestAmount] = useState('');
  const [showPayoutModal, setShowPayoutModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/login');
    }
  }, [user, userLoading, router]);

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      setLoading(true);
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      if (!token) {
        router.push('/login');
        return;
      }

      // Load summary
      const summaryRes = await fetch(`${API_BASE}/api/v1x/mentors/payouts/summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }

      // Load earnings
      const earningsRes = await fetch(`${API_BASE}/api/v1x/mentors/payouts/earnings?limit=100`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (earningsRes.ok) {
        const earningsData = await earningsRes.json();
        setEarnings(earningsData);
      }

      // Load payouts
      const payoutsRes = await fetch(`${API_BASE}/api/v1x/mentors/payouts/history?limit=100`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (payoutsRes.ok) {
        const payoutsData = await payoutsRes.json();
        setPayouts(payoutsData);
      }
    } catch (error) {
      console.error('Error loading earnings data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestPayout = async () => {
    if (!requestAmount || parseFloat(requestAmount) < 10) {
      alert('Minimum payout amount is $10');
      return;
    }

    try {
      setSubmitting(true);
      const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];

      const response = await fetch(`${API_BASE}/api/v1x/mentors/payouts/request`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          amount: parseFloat(requestAmount),
          method: 'stripe'
        })
      });

      if (response.ok) {
        alert('Payout request submitted successfully!');
        setShowPayoutModal(false);
        setRequestAmount('');
        loadData();
      } else {
        const error = await response.json();
        alert(error.detail || 'Failed to request payout');
      }
    } catch (error) {
      console.error('Error requesting payout:', error);
      alert('Failed to request payout');
    } finally {
      setSubmitting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || styles.pending}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (userLoading || loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading earnings data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!summary) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <p className="text-red-600">Failed to load earnings data. Please try again later.</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <Head>
        <title>Earnings Dashboard - SkillForge Global</title>
      </Head>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Earnings Dashboard</h1>
          <p className="text-gray-600">Track your mentoring earnings and request payouts</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <p className="text-sm text-gray-600 mb-1">Available Balance</p>
            <p className="text-3xl font-bold text-green-600">{formatCurrency(summary.available_balance)}</p>
            <p className="text-xs text-gray-500 mt-2">Ready to withdraw</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600 mb-1">Total Earnings</p>
            <p className="text-3xl font-bold text-gray-900">{formatCurrency(summary.total_earnings)}</p>
            <p className="text-xs text-gray-500 mt-2">All time</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600 mb-1">Completed Sessions</p>
            <p className="text-3xl font-bold text-blue-600">{summary.completed_sessions}</p>
            <p className="text-xs text-gray-500 mt-2">of {summary.total_sessions} total</p>
          </Card>

          <Card className="p-6">
            <p className="text-sm text-gray-600 mb-1">Avg. Session Price</p>
            <p className="text-3xl font-bold text-purple-600">{formatCurrency(summary.average_session_price)}</p>
            <p className="text-xs text-gray-500 mt-2">Per session</p>
          </Card>
        </div>

        {/* Request Payout Button */}
        {summary.available_balance >= 10 && (
          <div className="mb-6">
            <Button
              onClick={() => setShowPayoutModal(true)}
              variant="primary"
              className="w-full md:w-auto"
            >
              💰 Request Payout
            </Button>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('earnings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'earnings'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Earnings History ({earnings.length})
            </button>
            <button
              onClick={() => setActiveTab('payouts')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'payouts'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Payout Requests ({payouts.length})
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Earnings Breakdown</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Gross Earnings:</span>
                  <span className="font-semibold">{formatCurrency(summary.total_earnings / 0.8)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Platform Fee ({summary.platform_fee_percentage}%):</span>
                  <span className="font-semibold text-red-600">
                    -{formatCurrency((summary.total_earnings / 0.8) * (summary.platform_fee_percentage / 100))}
                  </span>
                </div>
                <div className="flex justify-between pt-3 border-t">
                  <span className="font-semibold">Net Earnings:</span>
                  <span className="font-bold text-green-600">{formatCurrency(summary.total_earnings)}</span>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Payout Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Available to Withdraw:</span>
                  <span className="font-semibold text-green-600">{formatCurrency(summary.available_balance)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pending Payouts:</span>
                  <span className="font-semibold text-yellow-600">{formatCurrency(summary.pending_payouts)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Completed Payouts:</span>
                  <span className="font-semibold">{formatCurrency(summary.completed_payouts)}</span>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'earnings' && (
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Student
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Topic
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Gross
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fee
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Net
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {earnings.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                        No earnings yet. Complete sessions to start earning!
                      </td>
                    </tr>
                  ) : (
                    earnings.map((earning) => (
                      <tr key={earning.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(earning.earned_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {earning.student_name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {earning.topic}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-900">
                          {formatCurrency(earning.gross_amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600">
                          -{formatCurrency(earning.platform_fee)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-green-600">
                          {formatCurrency(earning.net_amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                          {earning.is_paid_out ? (
                            <span className="text-green-600">✓ Paid</span>
                          ) : (
                            <span className="text-yellow-600">⏳ Pending</span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {activeTab === 'payouts' && (
          <Card className="overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Requested
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Method
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sessions
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Completed
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {payouts.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                        No payout requests yet.
                      </td>
                    </tr>
                  ) : (
                    payouts.map((payout) => (
                      <tr key={payout.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatDate(payout.requested_at)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-semibold text-gray-900">
                          {formatCurrency(payout.net_amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                          {payout.method.replace('_', ' ')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-900">
                          {payout.earnings_count}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center">
                          {getStatusBadge(payout.status)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {payout.completed_at ? formatDate(payout.completed_at) : '-'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}
      </div>

      {/* Payout Request Modal */}
      {showPayoutModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="max-w-md w-full p-6">
            <h2 className="text-2xl font-bold mb-4">Request Payout</h2>
            <p className="text-gray-600 mb-4">
              Available balance: <span className="font-semibold text-green-600">{formatCurrency(summary.available_balance)}</span>
            </p>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount (USD)
              </label>
              <input
                type="number"
                min="10"
                max={summary.available_balance}
                step="0.01"
                value={requestAmount}
                onChange={(e) => setRequestAmount(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Minimum $10"
              />
              <p className="text-xs text-gray-500 mt-1">Minimum payout: $10</p>
            </div>
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method
              </label>
              <select className="w-full px-4 py-2 border border-gray-300 rounded-lg">
                <option>Stripe (Direct Deposit)</option>
              </select>
            </div>
            <div className="flex gap-3">
              <Button
                onClick={handleRequestPayout}
                variant="primary"
                disabled={submitting || !requestAmount || parseFloat(requestAmount) < 10}
                className="flex-1"
              >
                {submitting ? 'Submitting...' : 'Request Payout'}
              </Button>
              <Button
                onClick={() => {
                  setShowPayoutModal(false);
                  setRequestAmount('');
                }}
                variant="secondary"
                disabled={submitting}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </Card>
        </div>
      )}
    </Layout>
  );
}
