export async function getBalance() {
  const r = await fetch("/api/coins/balance", { credentials: "include" });
  if (!r.ok) throw new Error("balance failed");
  return r.json();
}

export async function addCoins(amount: number) {
  const r = await fetch("/api/coins/add", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ amount }),
    credentials: "include",
  });
  if (!r.ok) throw new Error("add failed");
  return r.json();
}

export async function redeemCoins(amount: number) {
  const r = await fetch("/api/coins/redeem", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ amount }),
    credentials: "include",
  });
  if (!r.ok) throw new Error("redeem failed");
  return r.json();
}
