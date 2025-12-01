import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE as DEFAULT_API_BASE } from "@/lib/apiBase";

// Prefer explicit server-side API_BASE, fall back to shared lib default
const API_BASE = process.env.API_BASE || DEFAULT_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();
  
  try {
    // SECURITY: Extract credentials from request body server-side only
    // This prevents credentials from being logged in browser DevTools
    const { email, password } = req.body || {};
    
    if (!email || !password) {
      return res.status(400).json({ detail: "Email and password required" });
    }
    
    const r = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: "POST",
      headers: { 
        "content-type": "application/json",
        cookie: req.headers.cookie || "" 
      },
      credentials: "include" as any,
      body: JSON.stringify({ email, password }),
    });

    // Pass backend Set-Cookie(s) to the browser (handle multiple cookies)
    // Node/undici may store cookies in raw()["set-cookie"] array
    const anyHeaders = r.headers as any;
    const raw = typeof anyHeaders.raw === 'function' ? anyHeaders.raw() : undefined;
    const setCookies: string[] | undefined = raw?.["set-cookie"] || (r.headers.get("set-cookie") ? [r.headers.get("set-cookie") as string] : undefined);
    if (setCookies && setCookies.length) {
      res.setHeader("Set-Cookie", setCookies);
    }

    const text = await r.text();
    
    // Don't log credentials in server logs either
    if (!r.ok) {
      console.error(`/api/session/login failed with status ${r.status}`);
    }
    
    res.status(r.status).send(text);
  } catch (e: any) {
    console.error("/api/session/login proxy error:", e?.message || e);
    res.status(500).json({ detail: e?.message || "login proxy error" });
  }
}
