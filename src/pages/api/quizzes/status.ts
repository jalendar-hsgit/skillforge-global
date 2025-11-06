import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { path } = req.query;
    const r = await fetch(`${API_BASE}/api/v1/quizzes/status?path=${encodeURIComponent(String(path||''))}` , {
      headers: { cookie: req.headers.cookie || "" },
      credentials: "include" as any,
    });
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e:any) {
    res.status(500).json({ detail: e.message || "backend error" });
  }
}
