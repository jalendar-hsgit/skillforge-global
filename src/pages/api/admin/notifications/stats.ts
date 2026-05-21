import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
  
  try {
    const response = await fetch(`${API_BASE}/api/v1x/admin/notifications/stats`, {
      method: 'GET',
      headers: {
        'Cookie': req.headers.cookie || '',
      },
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ detail: 'Internal server error' });
  }
}
