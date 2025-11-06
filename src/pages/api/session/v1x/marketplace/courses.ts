import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Build query string from request
    const queryParams = new URLSearchParams();
    if (req.query.category) queryParams.set('category', String(req.query.category));
    if (req.query.search) queryParams.set('search', String(req.query.search));
    if (req.query.free_only) queryParams.set('free_only', String(req.query.free_only));
    
    const queryString = queryParams.toString();
    const target = `${API_BASE}/api/v1x/marketplace/courses${queryString ? '?' + queryString : ''}`;

    const r = await fetch(target, {
      method: req.method || "GET",
      headers: {
        cookie: req.headers.cookie || "",
      },
      credentials: "include" as any,
    });

    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    const data = await r.json();
    res.status(r.status).json(data);
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "marketplace courses proxy error" });
  }
}
