import type { NextApiRequest, NextApiResponse } from "next";
import { API_BASE } from "@/lib/apiBase";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") return res.status(405).end();

  const r = await fetch(`${API_BASE}/api/v1/auth/signup`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req.body || {}),
    credentials: "include" as any
  });

  // Pass backend Set-Cookie(s) to the browser
  const anyHeaders = r.headers as any;
  const raw = typeof anyHeaders.raw === 'function' ? anyHeaders.raw() : undefined;
  const setCookies: string[] | undefined = raw?.["set-cookie"] || (r.headers.get("set-cookie") ? [r.headers.get("set-cookie") as string] : undefined);
  if (setCookies && setCookies.length) {
    res.setHeader("Set-Cookie", setCookies);
  }

  const text = await r.text();
  res.status(r.status).send(text || "{}");
}
