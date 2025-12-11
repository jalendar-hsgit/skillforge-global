import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE } from "@/lib/apiBase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();

  try {
    const r = await fetch(`${API_BASE}/api/v1/auth/reset`, {
      method: "POST",
      headers: { "content-type": "application/json", cookie: req.headers.cookie || "" },
      body: JSON.stringify(req.body || {}),
    });
    const text = await r.text();
    res.status(r.status).send(text || "{}");
  } catch (e: any) {
    console.error("/api/session/reset proxy error:", e?.message || e);
    res.status(500).json({ detail: e?.message || "reset proxy error" });
  }
}
