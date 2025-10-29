import type { NextApiRequest, NextApiResponse } from "next"
const API_BASE = process.env.API_BASE || "http://localhost:8001"

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const r = await fetch(`${API_BASE}/api/v1/auth/me`, {
    // forward the cookie the browser sent to Next
    headers: { cookie: req.headers.cookie || "" },
  } as any)
  const text = await r.text()
  res.status(r.status).send(text)
}
