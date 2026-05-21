import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { useAuth } from '@/hooks/useAuth';
import CoinWidget from '@/components/CoinWidget';

interface CoinTransaction {
  id: number;
  userId: number;
  amount: number;
  type: 'earned' | 'spent' | 'bonus' | 'refunded';
  reason: string;
  createdAt: string;
  relatedEntity?: string;
}

interface CoinBalance {
  balance: number;
  totalEarned: number;
  totalSpent: number;
  lastUpdated: string;
}

export default function CoinsBalancePage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [balance, setBalance] = useState<CoinBalance | null>(null);
  const [transactions, setTransactions] = useState<CoinTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'earned' | 'spent' | 'bonus' | 'refunded'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    if (isAuthenticated && user?.id) {
      fetchCoinData();
    }
  }, [isAuthenticated, user?.id]);

  const fetchCoinData = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      // Fetch balance
      const balanceRes = await fetch(`${apiBase}/api/v1x/coins/balance`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!balanceRes.ok) throw new Error('Failed to fetch balance');
      const balanceData = await balanceRes.json();
      setBalance(balanceData);

      // Fetch transactions
      const transRes = await fetch(
        `${apiBase}/api/v1x/coins/history?type=${filterType === 'all' ? '' : filterType}&limit=100`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!transRes.ok) throw new Error('Failed to fetch transactions');
      const transData = await transRes.json();
      setTransactions(transData.transactions || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading coin data');
      console.error('Coin fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (type: typeof filterType) => {
    setFilterType(type);
    setCurrentPage(1);
  };

  const filteredTransactions = filterType === 'all'
    ? transactions
    : transactions.filter(t => t.type === filterType);

  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
  const paginatedTransactions = filteredTransactions.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'earned': return 'text-green-600 dark:text-green-400';
      case 'spent': return 'text-red-600 dark:text-red-400';
      case 'bonus': return 'text-yellow-600 dark:text-yellow-400';
      case 'refunded': return 'text-blue-600 dark:text-blue-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'earned': return '📈';
      case 'spent': return '💸';
      case 'bonus': return '🎁';
      case 'refunded': return '↩️';
      default: return '💰';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading your coins...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Coin Wallet - SkillForge</title>
        <meta name="description" content="View and manage your SkillForge coins" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              💰 Coin Wallet
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Track your coins and rewards
            </p>
          </div>

          {/* Balance Card */}
          {balance && (
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-700 dark:to-blue-800 rounded-lg shadow-lg p-8 mb-8 text-white">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <p className="text-blue-100 text-sm font-semibold mb-1">Current Balance</p>
                  <p className="text-4xl font-bold">{balance.balance.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-blue-100 text-sm font-semibold mb-1">Total Earned</p>
                  <p className="text-2xl font-bold text-green-300">
                    +{balance.totalEarned.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-blue-100 text-sm font-semibold mb-1">Total Spent</p>
                  <p className="text-2xl font-bold text-red-300">
                    -{balance.totalSpent.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Filter Tabs */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
            <div className="flex flex-wrap gap-2">
              {(['all', 'earned', 'spent', 'bonus', 'refunded'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => handleFilterChange(type)}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all capitalize ${
                    filterType === type
                      ? 'bg-blue-500 text-white shadow-md'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          {/* Transactions Table */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            {paginatedTransactions.length === 0 ? (
              <div className="p-8 text-center text-gray-600 dark:text-gray-400">
                <div className="text-4xl mb-3">📭</div>
                <p>No transactions found for this filter</p>
              </div>
            ) : (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-100 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600">
                      <tr>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Type
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Description
                        </th>
                        <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 dark:text-gray-300">
                          Date
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {paginatedTransactions.map((transaction) => (
                        <tr
                          key={transaction.id}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <td className="px-6 py-4">
                            <span className="text-xl">
                              {getTypeIcon(transaction.type)}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <p className="font-semibold text-gray-900 dark:text-white text-sm">
                              {transaction.reason}
                            </p>
                            {transaction.relatedEntity && (
                              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                                {transaction.relatedEntity}
                              </p>
                            )}
                          </td>
                          <td className="px-6 py-4 text-right">
                            <span className={`font-bold text-lg ${getTypeColor(transaction.type)}`}>
                              {transaction.type === 'spent' || transaction.type === 'refunded'
                                ? '-' : '+'}
                              {Math.abs(transaction.amount).toLocaleString()}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                            {new Date(transaction.createdAt).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="border-t border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Page {currentPage} of {totalPages}
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        ← Previous
                      </button>
                      <button
                        onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        Next →
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Info Card */}
          <div className="bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mt-6">
            <h3 className="font-semibold text-blue-900 dark:text-blue-200 mb-2">💡 How to Earn Coins</h3>
            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>✓ Complete coding challenges</li>
              <li>✓ Finish courses and modules</li>
              <li>✓ Earn achievements</li>
              <li>✓ Participate in community (helpful solutions, snippets)</li>
              <li>✓ Referral bonuses</li>
            </ul>
          </div>
        </div>
      </div>
    </>
  );
}
