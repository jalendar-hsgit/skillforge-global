import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id } = req.query;
  if (!id) return res.status(400).json({ detail: 'id required' });

  try {
    const url = `${API_BASE}/api/v1/quizzes/saved/${id}`;
    if (req.method === 'GET') {
      const r = await fetch(url, { headers: { cookie: req.headers.cookie || '' }, credentials: 'include' as any });
      const setCookie = r.headers.get('set-cookie');
      if (setCookie) res.setHeader('set-cookie', setCookie);
      const text = await r.text();
      res.status(r.status).send(text);
      return;
    }
    if (req.method === 'DELETE') {
      const r = await fetch(url, { method: 'DELETE', headers: { cookie: req.headers.cookie || '' }, credentials: 'include' as any });
      const setCookie = r.headers.get('set-cookie');
      if (setCookie) res.setHeader('set-cookie', setCookie);
      res.status(r.status).end();
      return;
    }
    res.status(405).json({ detail: 'Method not allowed' });
  } catch (e:any) {
    res.status(500).json({ detail: e.message || 'backend error' });
  }
}
