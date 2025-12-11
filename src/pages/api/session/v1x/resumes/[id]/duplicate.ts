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
    const idStr = Array.isArray(id) ? id[0] : id;
    const target = `${API_BASE}/api/v1x/resumes/${encodeURIComponent(String(idStr))}/duplicate`;

    console.log(`[v1x-resumes-duplicate] ${req.method} -> ${target}`);

    const headers: Record<string, string> = {
      cookie: (req.headers.cookie as string) || "",
    };
    if (req.headers["content-type"]) headers["content-type"] = String(req.headers["content-type"]);

    const method = req.method || "POST";
    let body: any = undefined;
    if (["POST", "PUT", "PATCH"].includes(method)) {
      const chunks: Buffer[] = [];
      await new Promise<void>((resolve, reject) => {
        (req as any)
          .on("data", (chunk: Buffer) => chunks.push(chunk))
          .on("end", () => resolve())
          .on("error", reject);
      });
      body = Buffer.concat(chunks);
    }

    const r = await fetch(target, {
      method,
      headers: headers as any,
      body: body && body.length > 0 ? body : undefined,
    } as any);

    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);

    if (process.env.NODE_ENV !== "production") res.setHeader("x-debug-target", target);

    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/json";
    res.setHeader("content-type", contentType);
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    console.error("v1x-resumes-duplicate error:", e?.message);
    res.status(502).json({ detail: e?.message || "proxy error" });
  }
}
