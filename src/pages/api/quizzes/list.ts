import type { NextApiRequest, NextApiResponse } from "next";
const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const r = await fetch(`${API_BASE}/api/v1/quizzes?path=${req.query.slug}`, {
      headers: { cookie: req.headers.cookie || "" },
      credentials: "include" as any,
    });
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e:any) {
    res.status(500).json({ detail: e.message || "backend error" });
  }
}
