import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const r = await fetch(`${API_BASE}/api/v1x/resume-ai/keywords`, {
      method: req.method,
      headers: {
        "content-type": "application/json",
        cookie: req.headers.cookie || "",
      },
      credentials: "include" as any,
      body: req.method === "POST" ? JSON.stringify(req.body || {}) : undefined,
    });

    const text = await r.text();
    res.status(r.status);
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    res.send(text || "{}");
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "resume-ai keywords proxy error" });
  }
}
