import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { id, action } = req.query;

  if (!id) {
    return res.status(400).json({ error: 'Template ID is required' });
  }

  try {
    const url = `${API_BASE}/api/v1x/resume-templates/${id}/${action || ''}`;

    const response = await fetch(url, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.cookie ? { Cookie: req.headers.cookie } : {}),
      },
      ...(req.method !== 'GET' && req.body ? { body: JSON.stringify(req.body) } : {}),
    });

    const data = await response.json();

    const setCookie = response.headers.get('set-cookie');
    if (setCookie) {
      res.setHeader('Set-Cookie', setCookie);
    }

    res.status(response.status).json(data);
  } catch (error) {
    console.error('Template action proxy error:', error);
    res.status(500).json({ error: 'Failed to process request' });
  }
}
