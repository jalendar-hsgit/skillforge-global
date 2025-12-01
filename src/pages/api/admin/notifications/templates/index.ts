import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
  
  try {
    const response = await fetch(`${API_BASE}/api/v1x/admin/notifications/templates`, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        'Cookie': req.headers.cookie || '',
      },
      body: req.method === 'POST' ? JSON.stringify(req.body) : undefined,
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
}
