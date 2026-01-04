import React, { useState, useEffect, useCallback } from 'react';
import { X, TrendingUp, TrendingDown, RefreshCw, Clock, Coins, Gift, Award } from 'lucide-react';

interface Transaction {
  id: number;
  amount: number;
  type: 'earn' | 'spend';
  reason: string;
  timestamp: string | null;
  balance_impact: number;
}

interface TransactionSummary {
  total_transactions: number;
  total_earns: number;
  total_spends: number;
  total_earned: number;
  total_spent: number;
  current_balance: number;
}

interface CoinHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentBalance?: number;
}

// Icon mapping for transaction reasons
const getTransactionIcon = (reason: string, type: 'earn' | 'spend') => {
  const lowerReason = reason.toLowerCase();
  
  if (lowerReason.includes('quiz')) return '🧠';
  if (lowerReason.includes('course') || lowerReason.includes('complete')) return '📚';
  if (lowerReason.includes('streak') || lowerReason.includes('daily')) return '🔥';
  if (lowerReason.includes('referral') || lowerReason.includes('refer')) return '🤝';
  if (lowerReason.includes('achievement') || lowerReason.includes('badge')) return '🏆';
  if (lowerReason.includes('mentor')) return '👨‍🏫';
  if (lowerReason.includes('purchase') || lowerReason.includes('shop')) return '🛒';
  if (lowerReason.includes('premium')) return '⭐';
  if (lowerReason.includes('bonus') || lowerReason.includes('reward')) return '🎁';
  if (lowerReason.includes('signup') || lowerReason.includes('welcome')) return '👋';
  
  return type === 'earn' ? '➕' : '➖';
};

// Format reason for display
const formatReason = (reason: string): string => {
  // Capitalize first letter and clean up
  return reason.charAt(0).toUpperCase() + reason.slice(1).replace(/_/g, ' ');
};

// Format timestamp
const formatDate = (timestamp: string | null): string => {
  if (!timestamp) return 'Unknown';
  
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  });
};

export const CoinHistoryModal: React.FC<CoinHistoryModalProps> = ({
  isOpen,
  onClose,
  currentBalance = 0
}) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState<TransactionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'earned' | 'spent'>('all');

  const fetchData = useCallback(async () => {
    if (!isOpen) return;
    
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');
      
      // Fetch transactions and summary in parallel
      const [transactionsRes, summaryRes] = await Promise.all([
        fetch(`${apiBase}/api/v1x/coins_db/transactions?limit=50`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${apiBase}/api/v1x/coins_db/transactions/summary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);
      
      if (transactionsRes.ok) {
        const data = await transactionsRes.json();
        setTransactions(data || []);
      }
      
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }
    } catch (err) {
      setError('Failed to load transaction history');
      console.error('Coin history fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [isOpen]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Filter transactions based on active tab
  const filteredTransactions = transactions.filter(t => {
    if (activeTab === 'earned') return t.type === 'earn';
    if (activeTab === 'spent') return t.type === 'spend';
    return true;
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-lg mx-4 bg-gradient-to-br from-gray-900 to-gray-800 border border-white/10 rounded-2xl shadow-2xl overflow-hidden max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="relative px-6 py-4 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center">
                <Coins className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Coin History</h2>
                <p className="text-sm text-white/60">Track your earnings & spending</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={fetchData}
                className="p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Balance Display */}
          <div className="mt-4 flex items-center gap-4">
            <div className="flex-1 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-xl p-4">
              <p className="text-sm text-white/60">Current Balance</p>
              <p className="text-3xl font-bold text-white flex items-center gap-2">
                💰 {(summary?.current_balance ?? currentBalance).toLocaleString()}
              </p>
            </div>
          </div>
          
          {/* Stats Row */}
          {summary && (
            <div className="mt-4 grid grid-cols-3 gap-3">
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-green-400 mb-1">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs font-medium">Earned</span>
                </div>
                <p className="text-lg font-bold text-white">{summary.total_earned.toLocaleString()}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-red-400 mb-1">
                  <TrendingDown className="w-4 h-4" />
                  <span className="text-xs font-medium">Spent</span>
                </div>
                <p className="text-lg font-bold text-white">{summary.total_spent.toLocaleString()}</p>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center">
                <div className="flex items-center justify-center gap-1 text-blue-400 mb-1">
                  <Clock className="w-4 h-4" />
                  <span className="text-xs font-medium">Transactions</span>
                </div>
                <p className="text-lg font-bold text-white">{summary.total_transactions}</p>
              </div>
            </div>
          )}
        </div>
        
        {/* Filter Tabs */}
        <div className="px-6 py-3 border-b border-white/10 bg-white/5">
          <div className="flex gap-2">
            {(['all', 'earned', 'spent'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                  activeTab === tab
                    ? 'bg-gradient-to-r from-forgePurple to-neuralBlue text-white'
                    : 'text-white/60 hover:text-white hover:bg-white/10'
                }`}
              >
                {tab === 'all' ? 'All' : tab === 'earned' ? '↑ Earned' : '↓ Spent'}
              </button>
            ))}
          </div>
        </div>
        
        {/* Transaction List */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="animate-spin text-4xl mb-4">⏳</div>
              <p className="text-white/60">Loading transactions...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-4xl mb-4">😕</div>
              <p className="text-red-400 font-medium">{error}</p>
              <button
                onClick={fetchData}
                className="mt-4 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>
          ) : filteredTransactions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="text-5xl mb-4">📭</div>
              <p className="text-white/60 font-medium">
                {activeTab === 'all' 
                  ? 'No transactions yet' 
                  : `No ${activeTab} coins yet`}
              </p>
              <p className="text-white/40 text-sm mt-2">
                Complete quizzes and courses to earn coins!
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredTransactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className={`flex items-center gap-4 p-3 rounded-xl transition-colors ${
                    transaction.type === 'earn'
                      ? 'bg-green-500/10 hover:bg-green-500/20'
                      : 'bg-red-500/10 hover:bg-red-500/20'
                  }`}
                >
                  {/* Icon */}
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${
                    transaction.type === 'earn'
                      ? 'bg-green-500/20'
                      : 'bg-red-500/20'
                  }`}>
                    {getTransactionIcon(transaction.reason, transaction.type)}
                  </div>
                  
                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-white truncate">
                      {formatReason(transaction.reason)}
                    </p>
                    <p className="text-xs text-white/50">
                      {formatDate(transaction.timestamp)}
                    </p>
                  </div>
                  
                  {/* Amount */}
                  <div className={`text-right ${
                    transaction.type === 'earn' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    <p className="font-bold text-lg">
                      {transaction.type === 'earn' ? '+' : '-'}{transaction.amount.toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="px-6 py-4 border-t border-white/10 bg-white/5">
          <div className="flex items-center justify-between">
            <a
              href="/coins"
              className="text-sm text-forgePurple hover:text-neuralBlue transition-colors"
            >
              Visit Coin Shop →
            </a>
            <p className="text-xs text-white/40">
              Showing last {filteredTransactions.length} transactions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoinHistoryModal;
