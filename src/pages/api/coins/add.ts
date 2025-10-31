import type { NextApiRequest, NextApiResponse } from "next";
const API_BASE = process.env.API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();
  try {
    const r = await fetch(`${API_BASE}/api/v1x/coins_db/add`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        cookie: req.headers.cookie || "",
      },
      body: JSON.stringify(req.body || {}),
      credentials: "include" as any,
    });
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e:any) {
    res.status(500).json({ detail: e?.message || "upstream error" });
  }
}
