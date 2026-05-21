import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const qs = new URLSearchParams();
    if (req.query.topic) qs.set('topic', String(req.query.topic));
    if (req.query.difficulty) qs.set('difficulty', String(req.query.difficulty));
    if (req.query.limit) qs.set('limit', String(req.query.limit));

    const r = await fetch(`${API_BASE}/api/v1/quizzes/saved?${qs.toString()}`, {
      headers: { cookie: req.headers.cookie || "" },
      credentials: 'include' as any,
    });
    const setCookie = r.headers.get('set-cookie');
    if (setCookie) res.setHeader('set-cookie', setCookie);
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e:any) {
    res.status(500).json({ detail: e.message || 'backend error' });
  }
}
