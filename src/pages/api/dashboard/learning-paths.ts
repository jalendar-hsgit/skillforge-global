// Next.js API proxy for learning paths
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiBase =
    process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

  const cookie = req.headers.cookie || '';

  try {
    const response = await fetch(`${apiBase}/api/v1/dashboard/learning-paths`, {
      method: 'GET',
      headers: {
        Cookie: cookie,
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({
        error: errorText || 'Failed to fetch learning paths',
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error: any) {
    console.error('Learning paths error:', error);
    return res.status(500).json({
      error: error.message || 'Internal server error',
    });
  }
}
