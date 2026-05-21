import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import Button from '../components/Button';
import Card from '../components/Card';
import { API_BASE } from '../lib/apiBase';

export default function ReferralProgram() {
  const [referralCode, setReferralCode] = useState(null);
  const [referrals, setReferrals] = useState([]);
  const [stats, setStats] = useState(null);
  const [recentRewards, setRecentRewards] = useState([]);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1x/referral/dashboard`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setReferralCode(data.referral_code);
        setStats(data.statistics);
        setReferrals(data.recent_referrals);
        setRecentRewards(data.pending_rewards);
      }
    } catch (error) {
      console.error('Failed to fetch referral dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_BASE}/api/v1x/referral/refer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ referred_email: inviteEmail }),
      });
      if (response.ok) {
        setInviteEmail('');
        setShowInviteForm(false);
        fetchDashboard();
      }
    } catch (error) {
      console.error('Failed to send invitation:', error);
    }
  };

  const copyCode = () => {
    if (referralCode) {
      navigator.clipboard.writeText(referralCode.code);
      alert('Referral code copied!');
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      bronze: 'text-amber-600',
      silver: 'text-gray-400',
      gold: 'text-yellow-500',
      platinum: 'text-purple-600',
    };
    return colors[tier] || 'text-gray-600';
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Referral Program</h1>
          <p className="text-xl text-gray-600">Earn rewards by inviting friends to join SkillForge Global</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-200">
          {['overview', 'referrals', 'rewards', 'leaderboard'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize transition ${
                activeTab === tab
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Referral Code Card */}
            <Card>
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Referral Code</h2>
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
                  <div className="text-center">
                    <p className="text-gray-600 text-sm mb-2">Share this code with your friends</p>
                    <div className="flex items-center justify-center gap-3">
                      <code className="text-3xl font-bold text-blue-600">{referralCode?.code}</code>
                      <button
                        onClick={copyCode}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition"
                      >
                        Copy
                      </button>
                    </div>
                    {referralCode?.custom_url && (
                      <p className="text-sm text-gray-600 mt-3">
                        Share link: {`https://skillforge.io/signup?ref=${referralCode.custom_url}`}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-600 text-sm mb-1">Times Used</p>
                    <p className="text-3xl font-bold text-gray-900">{referralCode?.used_count || 0}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-600 text-sm mb-1">Successful Referrals</p>
                    <p className="text-3xl font-bold text-gray-900">{referralCode?.successful_referrals || 0}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-600 text-sm mb-1">Bonus per Referral</p>
                    <p className="text-3xl font-bold text-blue-600">{referralCode?.bonus_per_referral || 100} coins</p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Statistics Card */}
            {stats && (
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Your Statistics</h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <p className="text-gray-600 text-sm mb-2">Total Referrals</p>
                      <p className="text-3xl font-bold text-blue-600">{stats.total_referrals}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                      <p className="text-gray-600 text-sm mb-2">Confirmed</p>
                      <p className="text-3xl font-bold text-green-600">{stats.confirmed_referrals}</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                      <p className="text-gray-600 text-sm mb-2">Rewards Earned</p>
                      <p className="text-3xl font-bold text-purple-600">{stats.total_rewards_earned}</p>
                    </div>
                    <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                      <p className="text-gray-600 text-sm mb-2">Your Tier</p>
                      <p className={`text-2xl font-bold capitalize ${getTierColor(stats.referrer_tier)}`}>
                        {stats.referrer_tier}
                      </p>
                    </div>
                  </div>

                  {/* Tier Progress */}
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-2">Conversion Rate: {(stats.conversion_rate * 100).toFixed(1)}%</p>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${Math.min(stats.conversion_rate * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Active Campaigns */}
            {dashboardData?.active_campaigns && dashboardData.active_campaigns.length > 0 && (
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Active Campaigns</h2>
                  <div className="space-y-3">
                    {dashboardData.active_campaigns.map((campaign) => (
                      <div key={campaign.id} className="p-4 border border-gray-200 rounded-lg">
                        <h3 className="font-semibold text-gray-900 mb-1">{campaign.name}</h3>
                        <p className="text-sm text-gray-600 mb-2">{campaign.description}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium text-blue-600">
                            +{campaign.referrer_bonus} coins per referral
                          </span>
                          <span className="text-xs text-gray-500">
                            Until {new Date(campaign.end_date).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            )}

            {/* Invite Button */}
            <Button
              onClick={() => setShowInviteForm(true)}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white text-lg py-3 rounded-lg transition"
            >
              + Invite a Friend
            </Button>
          </div>
        )}

        {/* Referrals Tab */}
        {activeTab === 'referrals' && (
          <div className="space-y-4">
            {referrals.length > 0 ? (
              referrals.map((ref) => (
                <Card key={ref.id}>
                  <div className="p-4 flex justify-between items-center">
                    <div>
                      <p className="font-semibold text-gray-900">{ref.referred_email}</p>
                      <p className={`text-sm font-medium ${
                        ref.status === 'confirmed' ? 'text-green-600' : 'text-yellow-600'
                      }`}>
                        {ref.status.charAt(0).toUpperCase() + ref.status.slice(1)}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{ref.bonus_amount} {ref.bonus_type}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(ref.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </Card>
              ))
            ) : (
              <Card>
                <div className="p-12 text-center">
                  <p className="text-gray-600 text-lg mb-4">No referrals yet</p>
                  <Button
                    onClick={() => setShowInviteForm(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition"
                  >
                    Invite Your First Friend
                  </Button>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Rewards Tab */}
        {activeTab === 'rewards' && (
          <div className="space-y-4">
            <Card>
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Pending Rewards</h2>
                <p className="text-3xl font-bold text-green-600 mb-6">{dashboardData?.pending_rewards || 0} coins</p>
                <Button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition">
                  Claim All Rewards
                </Button>
              </div>
            </Card>

            <Card>
              <div className="p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">How Rewards Work</h2>
                <div className="space-y-3 text-gray-700">
                  <p>✓ Earn 100 coins for each successful referral</p>
                  <p>✓ Bonus multipliers unlock at higher tiers</p>
                  <p>✓ Bronze tier (0-5): 1.0x multiplier</p>
                  <p>✓ Silver tier (6-20): 1.5x multiplier</p>
                  <p>✓ Gold tier (20+): 2.0x multiplier</p>
                  <p>✓ Platinum tier (30+): 3.0x multiplier</p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Leaderboard Tab */}
        {activeTab === 'leaderboard' && (
          <Card>
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Top Referrers</h2>
              <div className="space-y-3">
                {[
                  { rank: 1, name: 'Sarah Chen', referrals: 42, rewards: 4200 },
                  { rank: 2, name: 'Alex Kumar', referrals: 38, rewards: 3800 },
                  { rank: 3, name: 'Jordan Lee', referrals: 35, rewards: 3500 },
                  { rank: 4, name: 'Emma Watson', referrals: 30, rewards: 3000 },
                  { rank: 5, name: 'Chris Brown', referrals: 28, rewards: 2800 },
                ].map((entry) => (
                  <div key={entry.rank} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-gray-400 w-8">#{entry.rank}</span>
                      <div>
                        <p className="font-semibold text-gray-900">{entry.name}</p>
                        <p className="text-sm text-gray-600">{entry.referrals} referrals</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-600">{entry.rewards} coins</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        )}

        {/* Invite Modal */}
        {showInviteForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <Card className="max-w-md w-full">
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Invite a Friend</h2>
                <form onSubmit={handleInvite} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Friend's Email
                    </label>
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="friend@example.com"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                      required
                    />
                  </div>
                  <div className="flex gap-3">
                    <Button
                      type="submit"
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition"
                    >
                      Send Invite
                    </Button>
                    <Button
                      type="button"
                      onClick={() => setShowInviteForm(false)}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 py-2 rounded-lg transition"
                    >
                      Cancel
                    </Button>
                  </div>
                </form>
              </div>
            </Card>
          </div>
        )}
      </div>
    </Layout>
  );
}
