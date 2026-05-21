import type { NextApiRequest, NextApiResponse } from "next";
const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const baseUrl = `${API_BASE}/api/v1x/resumes`;
    const id = (req.query.id as string) || "";
    const action = (req.query.action as string) || "";

    // Handle special actions
    if (action && id) {
      if (action === "duplicate") {
        const r = await fetch(`${baseUrl}/${id}/duplicate`, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            cookie: req.headers.cookie || "",
          },
          credentials: "include" as any,
          body: JSON.stringify(req.body || {}),
        });
        const text = await r.text();
        res.status(r.status).send(text || "{}");
        return;
      }
      
      if (action === "apply-template") {
        const templateId = (req.query.template as string) || "";
        if (!templateId) {
          return res.status(400).json({ detail: "template parameter required" });
        }
        const r = await fetch(`${baseUrl}/${id}/apply-template/${templateId}`, {
          method: "POST",
          headers: {
            "content-type": "application/json",
            cookie: req.headers.cookie || "",
          },
          credentials: "include" as any,
          body: JSON.stringify(req.body || {}),
        });
        const text = await r.text();
        res.status(r.status).send(text || "{}");
        return;
      }
    }

    // Handle GET (list or by id) and POST (create)
    if (req.method === "GET" || req.method === "POST") {
      const target = req.method === "GET" && id ? `${baseUrl}/${id}` : baseUrl;
      const r = await fetch(target, {
        method: req.method,
        headers: {
          "content-type": "application/json",
          // forward cookies to backend so it can read JWT token
          cookie: req.headers.cookie || "",
        },
        credentials: "include" as any,
        body: req.method === "POST" ? JSON.stringify(req.body || {}) : undefined,
      });

      // pass through response body and status
      const text = await r.text();
      res.status(r.status);
      // forward set-cookie if backend updates token (rare here but safe)
      const setCookie = r.headers.get("set-cookie");
      if (setCookie) res.setHeader("set-cookie", setCookie);
      res.send(text || "{}");
      return;
    }

    // Proxy GET by id, PATCH, DELETE: /api/session/resumes?id=123
    if (["PATCH", "DELETE"].includes(req.method || "")) {
      if (!id) return res.status(400).json({ detail: "id is required" });
      const r = await fetch(`${baseUrl}/${id}`, {
        method: req.method,
        headers: {
          "content-type": "application/json",
          cookie: req.headers.cookie || "",
        },
        credentials: "include" as any,
        body: req.method === "PATCH" ? JSON.stringify(req.body || {}) : undefined,
      });
      const text = await r.text();
      // For 204 No Content, don't send a body
      if (r.status === 204) {
        res.status(204).end();
      } else {
        res.status(r.status).send(text || "{}");
      }
      return;
    }

    res.setHeader("allow", ["GET", "POST", "PATCH", "DELETE"]);
    return res.status(405).end();
  } catch (e: any) {
    return res.status(500).json({ detail: e?.message || "resumes proxy error" });
  }
}
