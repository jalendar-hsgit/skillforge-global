import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE =
  process.env.API_BASE ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://localhost:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { path } = req.query as { path?: string };
    if (!path) {
      return res.status(400).json({ detail: "Missing path" });
    }

    // Forward the browser cookies to the backend so the 'token' cookie is seen
    const r = await fetch(`${API_BASE}/api/v1/progress?path=${encodeURIComponent(path)}`, {
      headers: { cookie: req.headers.cookie || "" } as any,
    });

    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e: any) {
    res.status(500).send("Internal Error: " + (e?.message || "unknown"));
  }
}
