import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE as DEFAULT_API_BASE } from "@/lib/apiBase";

// Prefer explicit server-side API_BASE, fall back to shared lib default
const API_BASE = process.env.API_BASE || DEFAULT_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();
  try {
    const r = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { "content-type": "application/json", cookie: req.headers.cookie || "" },
      credentials: "include" as any,
      body: JSON.stringify(req.body || {}),
    });

    // Pass backend Set-Cookie to the browser
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("Set-Cookie", setCookie);

    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "login proxy error" });
  }
}
