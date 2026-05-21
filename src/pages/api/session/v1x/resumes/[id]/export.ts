import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { id } = req.query;
    const formatRaw = (req.query.format ?? 'pdf');
    const format = Array.isArray(formatRaw) ? formatRaw[0] : formatRaw;

    const target = `${API_BASE}/api/v1x/resumes/${id}/export?format=${encodeURIComponent(format || 'pdf')}`;

    const headers: Record<string, string> = {
      cookie: (req.headers.cookie as string) || "",
    };
    if (req.headers["authorization"]) headers["authorization"] = String(req.headers["authorization"]);

    const r = await fetch(target, {
      method: "GET",
      headers: headers as any,
    });

    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);

    const contentDisposition = r.headers.get("content-disposition");
    if (contentDisposition) res.setHeader("content-disposition", contentDisposition);

    if (process.env.NODE_ENV !== 'production') {
      res.setHeader('x-debug-target', target);
    }

    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/octet-stream";
    res.setHeader("content-type", contentType);
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "export proxy error" });
  }
}
