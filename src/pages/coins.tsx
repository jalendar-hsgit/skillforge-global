import { useEffect, useState } from "react";
import Head from "next/head";
import { getBalance, redeemCoins } from "@/lib/coins";
import Layout from "@/components/Layout";

interface ShopItem {
  id: string;
  name: string;
  description: string;
  cost: number;
  icon: string;
  category: 'quiz' | 'mentor' | 'feature';
}

const SHOP_ITEMS: ShopItem[] = [
  {
    id: 'ai_quiz_5',
    name: '5 AI Quiz Credits',
    description: 'Generate 5 custom AI quizzes on any topic',
    cost: 50,
    icon: '🧠',
    category: 'quiz'
  },
  {
    id: 'ai_quiz_20',
    name: '20 AI Quiz Credits',
    description: 'Generate 20 custom AI quizzes (20% discount!)',
    cost: 160,
    icon: '🎯',
    category: 'quiz'
  },
  {
    id: 'mentor_30min',
    name: '30min Mentor Session Credit',
    description: 'Book a 30-minute session with any mentor',
    cost: 200,
    icon: '👨‍🏫',
    category: 'mentor'
  },
  {
    id: 'mentor_60min',
    name: '60min Mentor Session Credit',
    description: 'Book a full hour with any mentor (10% discount!)',
    cost: 360,
    icon: '⏱️',
    category: 'mentor'
  },
  {
    id: 'resume_review',
    name: 'AI Resume Review',
    description: 'Get AI-powered feedback on your resume with ATS scoring',
    cost: 100,
    icon: '📄',
    category: 'feature'
  },
  {
    id: 'premium_week',
    name: '7-Day Premium Access',
    description: 'Unlock all premium courses and features for one week',
    cost: 500,
    icon: '⭐',
    category: 'feature'
  }
];

export default function CoinsPage() {
  const [coins, setCoins] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  async function refresh() {
    setErr("");
    try {
      const j = await getBalance();
      setCoins(j.coins ?? 0);
    } catch (e: any) {
      setErr(e?.message || "Failed to load balance");
    }
  }

  useEffect(() => { refresh(); }, []);

  async function handlePurchase(item: ShopItem) {
    if (!coins || coins < item.cost) {
      setErr("Insufficient coins!");
      return;
    }

    setLoading(true);
    setErr("");
    setSuccess("");

    try {
      await redeemCoins(item.cost);
      await refresh();
      setSuccess(`Successfully purchased: ${item.name}!`);
      
      // Auto-clear success message after 3 seconds
      setTimeout(() => setSuccess(""), 3000);
    } catch (e: any) {
      setErr(e?.message || "Purchase failed");
    } finally {
      setLoading(false);
    }
  }

  const filteredItems = selectedCategory === 'all' 
    ? SHOP_ITEMS 
    : SHOP_ITEMS.filter(item => item.category === selectedCategory);

  return (
    <Layout maxWidth="7xl">
      <Head>
        <title>Coin Shop – SkillForge Global</title>
      </Head>

      <div className="py-12">
        {/* Header with Balance */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Forge Coin Shop 🪙
          </h1>
          <p className="text-lg text-gray-600">
            Use your coins to unlock premium features and services
          </p>
        </div>

        {/* Balance Card */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl shadow-lg p-6 mb-8 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm opacity-90">Your Balance</p>
              <p className="text-5xl font-bold mt-1">
                {coins !== null ? coins.toLocaleString() : "..."}
              </p>
              <p className="text-sm opacity-75 mt-2">Forge Coins</p>
            </div>
            <div className="text-7xl opacity-20">🪙</div>
          </div>
        </div>

        {/* Notifications */}
        {err && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700 font-medium">{err}</p>
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-700 font-medium">✅ {success}</p>
          </div>
        )}

        {/* Category Filter */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {['all', 'quiz', 'mentor', 'feature'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {cat === 'all' ? 'All Items' : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>

        {/* Shop Items Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => {
            const canAfford = coins !== null && coins >= item.cost;
            
            return (
              <div
                key={item.id}
                className={`bg-white rounded-xl shadow-md p-6 border-2 transition-all ${
                  canAfford 
                    ? 'border-gray-200 hover:border-blue-400 hover:shadow-lg' 
                    : 'border-gray-100 opacity-60'
                }`}
              >
                <div className="text-5xl mb-4">{item.icon}</div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {item.name}
                </h3>
                
                <p className="text-gray-600 text-sm mb-4">
                  {item.description}
                </p>

                <div className="flex items-center justify-between mt-auto pt-4 border-t">
                  <div>
                    <p className="text-2xl font-bold text-blue-600">
                      {item.cost.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">coins</p>
                  </div>

                  <button
                    onClick={() => handlePurchase(item)}
                    disabled={loading || !canAfford}
                    className={`px-6 py-2 rounded-lg font-medium transition-all ${
                      canAfford && !loading
                        ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {loading ? 'Processing...' : canAfford ? 'Purchase' : 'Not Enough'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* How to Earn More Coins */}
        <div className="mt-12 bg-gray-50 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            💡 How to Earn More Coins
          </h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start gap-3">
              <span className="text-xl">🎯</span>
              <div>
                <strong>Complete Quizzes:</strong> Earn 10 coins for each quiz you complete with 80%+ score
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">📚</span>
              <div>
                <strong>Finish Courses:</strong> Get 50 coins when you complete an entire learning path
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">🔥</span>
              <div>
                <strong>Daily Streak:</strong> Log in daily and earn 5 coins per day (up to 35/week)
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xl">🤝</span>
              <div>
                <strong>Refer Friends:</strong> Get 100 coins for each friend who joins using your referral link
              </div>
            </li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
