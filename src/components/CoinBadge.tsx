import React, { useEffect, useState } from 'react'
import { Award } from 'lucide-react'
import { apiGet } from '@/lib/api'

export default function CoinBadge() {
  const [coins, setCoins] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  async function refresh() {
    setLoading(true)
    try {
      // Prefer backend API via API_BASE
      const j: any = await apiGet('/api/v1x/coins_db/balance')
      // support both `{ coins }` and `{ balance }`
      setCoins((j && (j.coins ?? j.balance)) ?? 10) // Default 10 credits
    } catch (e) {
      // Default to 10 credits if API fails
      setCoins(10)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])

  // Expose refresh function for other components
  useEffect(() => {
    (window as any).refreshCoins = refresh
  }, [])

  if (coins === null && !loading) return null

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-forgePurple/20 to-neuralBlue/20 border border-forgePurple/30">
      <Award className="w-4 h-4 text-yellow-400" />
      <span className="text-sm font-semibold">
        {loading ? '…' : coins}
      </span>
      <span className="text-xs text-techGray">credits</span>
    </div>
  )
}
