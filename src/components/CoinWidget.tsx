import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';

interface CoinWidgetProps {
  compact?: boolean;
}

export const CoinWidget: React.FC<CoinWidgetProps> = ({ compact = false }) => {
  const { user } = useAuth();
  const [balance, setBalance] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.id) {
      fetchCoinBalance();
    }
  }, [user?.id]);

  const fetchCoinBalance = async () => {
    try {
      setLoading(true);
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const response = await fetch(`${apiBase}/api/v1x/coins/balance`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBalance(data.balance || 0);
      }
    } catch (error) {
      console.error('Failed to fetch coin balance:', error);
      setBalance(0);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  if (compact) {
    return (
      <Link href="/coins/balance">
        <div className="flex items-center gap-1 px-2 py-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors">
          <span className="text-lg">💰</span>
          <span className="text-sm font-semibold">
            {loading ? '...' : balance.toLocaleString()}
          </span>
        </div>
      </Link>
    );
  }

  return (
    <Link href="/coins/balance">
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-all">
        <div className="text-2xl">💰</div>
        <div className="flex flex-col">
          <span className="text-xs text-gray-600 dark:text-gray-400">Coins</span>
          <span className="text-lg font-bold">
            {loading ? 'Loading...' : balance.toLocaleString()}
          </span>
        </div>
      </div>
    </Link>
  );
};

export default CoinWidget;
