import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { resumeId, id } = req.query;

    let target = "";
    if (id) {
      // DELETE or PUT /education/{id}
      target = `${API_BASE}/api/v1x/resumes/education/${id}`;
    } else {
      // POST /{resumeId}/education
      target = `${API_BASE}/api/v1x/resumes/${resumeId}/education`;
    }

    const method = req.method || "GET";
    const headers: Record<string, string> = {
      cookie: req.headers.cookie || "",
      "content-type": "application/json",
    };

    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
    const body = ["POST", "PUT", "PATCH"].includes(method) ? JSON.stringify(req.body || {}) : undefined;

    const r = await fetch(target, {
      method,
      headers,
      body,
      // @ts-ignore
      credentials: "include",
    });

    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    res.status(r.status);

    if (r.status === 204) {
      return res.end();
    }

    const text = await r.text();
    res.setHeader("content-type", r.headers.get("content-type") || "application/json");
    res.send(text || "{}");
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "education proxy error" });
  }
}
