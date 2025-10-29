import type { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') return res.status(405).end()
  const { email } = req.body || {}
  if (!email) return res.status(400).json({ ok:false, message:'Email required' })
  const r = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/subscribe`, {
    method: 'POST',
    headers: { 'Content-Type':'application/json' },
    body: JSON.stringify({ email }),
  })
  const t = await r.text()
  res.status(r.status).send(t || '{}')
}
