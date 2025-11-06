import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.status(405).json({ detail: 'Method not allowed' });
    return;
  }

  try {
    const qs = new URLSearchParams();
    if (req.query.quiz_id) qs.set('quiz_id', String(req.query.quiz_id));
    if (req.query.path) qs.set('path', String(req.query.path));

    const r = await fetch(`${API_BASE}/api/v1/quizzes/session/start?${qs.toString()}`, {
      method: 'POST',
      headers: {
        cookie: req.headers.cookie || '',
      },
      // @ts-ignore Next runtime
      credentials: 'include',
    });
    const setCookie = r.headers.get('set-cookie');
    if (setCookie) res.setHeader('set-cookie', setCookie);
    const text = await r.text();
    res.status(r.status).send(text);
  } catch (e: any) {
    res.status(500).json({ detail: e.message || 'backend error' });
  }
}
