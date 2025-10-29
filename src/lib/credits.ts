const KEY = "forge_ai_credits";

export function getCredits(): number {
  if (typeof window === "undefined") return 0;
  const raw = localStorage.getItem(KEY);
  const n = raw ? parseInt(raw, 10) : 0;
  return Number.isFinite(n) ? n : 0;
}

export function addCredits(amount: number): number {
  if (typeof window === "undefined") return 0;
  const cur = getCredits();
  const next = cur + amount;
  localStorage.setItem(KEY, String(next));
  return next;
}
