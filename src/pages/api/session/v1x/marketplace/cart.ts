import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const method = req.method || "GET";
    const target = `${API_BASE}/api/v1x/marketplace/cart`;

    console.log(`[cart-proxy] ${method} /api/session/v1x/marketplace/cart -> ${target}`);

    const headers: Record<string, string> = {};
    if (req.headers.cookie) headers.cookie = req.headers.cookie;
    if (req.headers["content-type"]) headers["content-type"] = req.headers["content-type"];

    let body: any = undefined;
    
    // Handle request body for POST requests
    if (method === "POST" && req.headers["content-length"]) {
      const chunks: Buffer[] = [];
      await new Promise<void>((resolve, reject) => {
        (req as any)
          .on("data", (chunk: Buffer) => chunks.push(chunk))
          .on("end", () => resolve())
          .on("error", reject);
      });
      if (chunks.length > 0) {
        body = Buffer.concat(chunks);
      }
    }

    const response = await fetch(target, {
      method,
      headers,
      body,
    } as any);

    const responseText = await response.text();
    
    const setCookie = response.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    res.status(response.status);
    res.setHeader("content-type", response.headers.get("content-type") || "application/json");
    res.end(responseText);
  } catch (e: any) {
    console.error("[cart-proxy] Error:", e);
    res.status(500).json({ detail: e?.message || "Proxy error" });
  }
}
