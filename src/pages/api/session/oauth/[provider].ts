import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE } from "@/lib/apiBase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const provider = (req.query.provider as string) || "";
  if (req.method !== "POST") return res.status(405).end();

  try {
    const r = await fetch(`${API_BASE}/api/v1/auth/oauth/${provider}`, {
      method: "POST",
      headers: { "content-type": "application/json", cookie: req.headers.cookie || "" },
      body: JSON.stringify(req.body || {}),
    });

    // Forward Set-Cookie if backend set it
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("Set-Cookie", setCookie);

    const text = await r.text();
    res.status(r.status).send(text || "{}");
  } catch (e: any) {
    console.error("/api/session/oauth proxy error:", e?.message || e);
    res.status(500).json({ detail: e?.message || "oauth proxy error" });
  }
}
