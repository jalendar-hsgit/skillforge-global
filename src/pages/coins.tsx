import { useEffect, useState } from "react";
import { getBalance, addCoins, redeemCoins } from "@/lib/coins";

export default function CoinsPage() {
  const [coins, setCoins] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string>("");

  async function refresh() {
    setErr("");
    try {
      const j = await getBalance();
      setCoins(j.coins ?? 0);
    } catch (e:any) {
      setErr(e?.message || "Failed to load");
    }
  }

  useEffect(() => { refresh(); }, []);

  async function doAdd(a:number) {
    setLoading(true); setErr("");
    try { await addCoins(a); await refresh(); }
    catch(e:any){ setErr(e?.message || "Add failed"); }
    finally { setLoading(false); }
  }
  async function doRedeem(a:number) {
    setLoading(true); setErr("");
    try { await redeemCoins(a); await refresh(); }
    catch(e:any){ setErr(e?.message || "Redeem failed"); }
    finally { setLoading(false); }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-indigo-600 mb-4">Your Coins</h1>
      {err && <p className="text-red-500 mb-3">{err}</p>}
      <div className="bg-white rounded-xl shadow p-4">
        <p className="text-gray-700">Balance: <span className="font-semibold">{coins ?? "…"}</span></p>
        <div className="flex gap-3 mt-4">
          <button onClick={() => doAdd(100)} disabled={loading} className="px-4 py-2 rounded-xl bg-indigo-600 text-white hover:opacity-95">+100</button>
          <button onClick={() => doAdd(500)} disabled={loading} className="px-4 py-2 rounded-xl bg-indigo-600 text-white hover:opacity-95">+500</button>
          <button onClick={() => doRedeem(20)} disabled={loading} className="px-4 py-2 rounded-xl border border-gray-300 hover:bg-gray-50">Redeem 20</button>
        </div>
      </div>
    </div>
  );
}
