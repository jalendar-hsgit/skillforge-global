import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const target = `${API_BASE}/api/v1x/marketplace/cart`;

    const headers: Record<string, string> = {};
    if (req.headers.cookie) headers.cookie = req.headers.cookie;

    const response = await fetch(target, {
      method: 'GET',
      headers,
    });

    const data = await response.json();
    
    const setCookie = response.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    res.status(response.status).json(data);
  } catch (e: any) {
    console.error('Cart proxy error:', e);
    res.status(500).json({ detail: e?.message || "Proxy error" });
  }
}
