import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export const config = {
  api: {
    bodyParser: false, // Required for binary file downloads
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { format = 'pdf' } = req.query;
    const resumeId = req.query.resumeId || req.query.id;
    
    if (!resumeId) {
      return res.status(400).json({ detail: "Resume ID required" });
    }

    const target = `${API_BASE}/api/v1x/resumes/${resumeId}/export?format=${format}`;
    console.log(`[export-proxy] ${req.method} -> ${target}`);

    const r = await fetch(target, {
      method: "GET",
      headers: {
        cookie: req.headers.cookie || "",
      },
      credentials: "include" as any,
    });

    console.log(`[export-proxy] <- ${r.status} ${target}`);

    // Forward all relevant headers
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    const contentDisposition = r.headers.get("content-disposition");
    if (contentDisposition) res.setHeader("content-disposition", contentDisposition);
    
    res.setHeader("x-debug-target", target);
    res.status(r.status);
    
    const contentType = r.headers.get("content-type") || "application/octet-stream";
    res.setHeader("content-type", contentType);
    
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    console.error("[export-proxy] Error:", e);
    res.status(500).json({ detail: e?.message || "export proxy error" });
  }
}
