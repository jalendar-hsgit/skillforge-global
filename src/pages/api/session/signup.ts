import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE } from "@/lib/apiBase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();

  const r = await fetch(`${API_BASE}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req.body || {}),
  });

  const text = await r.text();
  res.status(r.status).send(text || "{}");
}
