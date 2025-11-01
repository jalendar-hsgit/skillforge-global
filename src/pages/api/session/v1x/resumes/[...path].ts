import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const segments = (req.query.path as string[] | undefined) || [];
    const target = `${API_BASE}/api/v1x/resumes/${segments.join("/")}`;

    const headers: Record<string, string> = {
      cookie: req.headers.cookie || "",
    };
    if (req.headers["content-type"]) headers["content-type"] = String(req.headers["content-type"]);

    const method = req.method || "GET";
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
    let body: any = undefined;

    if (isWrite && ["POST", "PUT", "PATCH"].includes(method)) {
      body = JSON.stringify(req.body || {});
      if (!headers["content-type"]) headers["content-type"] = "application/json";
    }

    const r = await fetch(target, {
      method,
      headers: headers as any,
      body,
      credentials: "include" as any,
    });

    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/json";
    res.setHeader("content-type", contentType);
    const text = await r.text();
    res.send(text || (r.status === 204 ? "" : "{}"));
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "resumes proxy error" });
  }
}
