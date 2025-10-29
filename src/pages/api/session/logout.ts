import type { NextApiRequest, NextApiResponse } from "next"
const API_BASE = process.env.API_BASE || "http://localhost:8001"
export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  const r = await fetch(`${API_BASE}/api/v1/auth/logout`, { method: "POST" } as any)
  const setCookie = r.headers.get("set-cookie")
  if (setCookie) res.setHeader("Set-Cookie", setCookie)
  const text = await r.text()
  res.status(r.status).send(text)
}
