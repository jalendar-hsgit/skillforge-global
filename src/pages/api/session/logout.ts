import type { NextApiRequest, NextApiResponse } from "next";
const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const r = await fetch(`${API_BASE}/api/v1/auth/logout`, { method: "POST", headers: { cookie: req.headers.cookie || "" }, credentials: "include" as any } as any);
    // best effort: expire token on frontend domain too (in case)
    res.setHeader("set-cookie", "token=deleted; Max-Age=0; Path=/; SameSite=Lax; HttpOnly");
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e: any) {
    // still expire cookie
    res.setHeader("set-cookie", "token=deleted; Max-Age=0; Path=/; SameSite=Lax; HttpOnly");
    res.status(200).json({ loggedOut: true });
  }
}
