import type { NextApiRequest, NextApiResponse } from "next"

const API_BASE = process.env.API_BASE || "http://localhost:8001"

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    res.status(405).end()
    return
  }

  const r = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req.body || {}),
    // let FastAPI set the cookie
  } as any)

  // forward Set-Cookie from backend to browser
  const setCookie = r.headers.get("set-cookie")
  if (setCookie) res.setHeader("Set-Cookie", setCookie)

  const text = await r.text()
  res.status(r.status).send(text || "{}")
}
