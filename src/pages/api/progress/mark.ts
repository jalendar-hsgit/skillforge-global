import type { NextApiRequest, NextApiResponse } from 'next'
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { path, module_id } = req.body || {}
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/progress?path=${encodeURIComponent(path)}&module_id=${encodeURIComponent(module_id)}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${req.cookies['sfg_token'] || ''}`
    }
  })
  const t = await r.text()
  res.status(r.status).send(t || '{}')
}
