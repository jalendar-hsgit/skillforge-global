import type { NextApiRequest, NextApiResponse } from "next";

export const config = {
  api: {
    bodyParser: false, // allow streaming/multipart bodies to pass through
  },
};

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const segments = (req.query.path as string[] | undefined) || [];
    let target = `${API_BASE}/api/v1x/${segments.join("/")}`;
    
    // Forward query parameters
    const { path, ...queryParams } = req.query;
    const queryString = new URLSearchParams(
      Object.entries(queryParams).flatMap(([key, value]) =>
        Array.isArray(value) ? value.map(v => [key, v]) : [[key, String(value)]]
      )
    ).toString();
    if (queryString) {
      target += `?${queryString}`;
    }

    // Build headers, preserving content-type and cookies
    const headers: Record<string, string> = {
      cookie: (req.headers.cookie as string) || "",
    };
    if (req.headers["content-type"]) headers["content-type"] = String(req.headers["content-type"]);
    if (req.headers["authorization"]) headers["authorization"] = String(req.headers["authorization"]);

    // Determine request body strategy
    const method = req.method || "GET";
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
    let body: any = undefined;

    // If multipart/form-data or octet-stream, forward the raw stream
    const ct = (req.headers["content-type"] || "").toString();
    const isMultipart = ct.startsWith("multipart/form-data") || ct.startsWith("application/octet-stream");
    if (isWrite) {
      if (isMultipart) {
        body = req as any; // pass through stream
      } else if (["POST", "PUT", "PATCH"].includes(method)) {
        // For JSON-like bodies, buffer and forward as-is
        // Next has bodyParser disabled, so we read the raw stream
        const chunks: Buffer[] = [];
        await new Promise<void>((resolve, reject) => {
          (req as any)
            .on("data", (chunk: Buffer) => chunks.push(chunk))
            .on("end", () => resolve())
            .on("error", reject);
        });
        body = Buffer.concat(chunks);
        // If no explicit content-type was provided, default to JSON
        if (!headers["content-type"]) headers["content-type"] = "application/json";
      }
    }

    const r = await fetch(target, {
      method,
      headers: headers as any,
      // @ts-ignore - Node fetch accepts Readable/Buffer for body
      body,
      // credentials not used server-to-server but keep for symmetry
    } as any);

    // Stream response back to client preserving status and set-cookie
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/json";
    res.setHeader("content-type", contentType);
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    res.status(500).json({ detail: e?.message || "v1x proxy error" });
  }
}
