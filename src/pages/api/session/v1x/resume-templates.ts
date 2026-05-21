import type { NextApiRequest, NextApiResponse } from 'next';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { method, query } = req;

  try {
    // Build query string
    const queryParams = new URLSearchParams();
    if (query.category && query.category !== 'All') {
      queryParams.append('category', query.category as string);
    }
    if (query.ats_friendly) {
      queryParams.append('ats_friendly', query.ats_friendly as string);
    }
    if (query.free_only) {
      queryParams.append('free_only', query.free_only as string);
    }

    const queryString = queryParams.toString();
    const url = `${API_BASE}/api/v1x/resume-templates${queryString ? `?${queryString}` : ''}`;

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.cookie ? { Cookie: req.headers.cookie } : {}),
      },
    });

    const data = await response.json();

    // Forward any set-cookie headers
    const setCookie = response.headers.get('set-cookie');
    if (setCookie) {
      res.setHeader('Set-Cookie', setCookie);
    }

    res.status(response.status).json(data);
  } catch (error) {
    console.error('Resume templates proxy error:', error);
    res.status(500).json({ error: 'Failed to fetch templates' });
  }
}
