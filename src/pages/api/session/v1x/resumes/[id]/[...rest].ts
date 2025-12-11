import type { NextApiRequest, NextApiResponse } from "next";

const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export const config = {
  api: {
    bodyParser: false, // allow streaming/multipart bodies to pass through
  },
};

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const { id, rest } = req.query;
    const idStr = Array.isArray(id) ? id[0] : id;
    const restSegments = Array.isArray(rest) ? rest : [rest];
    const pathSegments = [idStr, ...restSegments].join("/");
    
      // Debug logging
      console.log(`[v1x-resumes-catch-all] id=${id}, rest=${rest}`);
      console.log(`[v1x-resumes-catch-all] pathSegments=${pathSegments}`);
    
    const target = `${API_BASE}/api/v1x/resumes/${pathSegments}`;

    // ALWAYS log to debug routing issues
    console.log(`[v1x-resumes-proxy] ${req.method} /api/session/v1x/resumes/${pathSegments} -> ${target}`);

    // Build headers, preserving content-type and cookies
    const headers: Record<string, string> = {
      cookie: (req.headers.cookie as string) || "",
    };
    if (req.headers["content-type"]) headers["content-type"] = String(req.headers["content-type"]);
    if (req.headers["authorization"]) headers["authorization"] = String(req.headers["authorization"]);
    headers["x-forwarded-for"] = (req.headers["x-forwarded-for"] as string) || (req.socket as any)?.remoteAddress || "";
    headers["x-forwarded-host"] = req.headers.host || "";
    headers["x-forwarded-proto"] = (req.headers["x-forwarded-proto"] as string) || "http";

    // Determine request body strategy
    const method = req.method || "GET";
    const isWrite = ["POST", "PUT", "PATCH", "DELETE"].includes(method);
    let body: any = undefined;

    if (isWrite) {
      const ct = (req.headers["content-type"] || "").toString();
      const isMultipart = ct.startsWith("multipart/form-data") || ct.startsWith("application/octet-stream");
      if (isMultipart) {
        body = req as any; // pass through stream
      } else if (["POST", "PUT", "PATCH"].includes(method)) {
        // For JSON-like bodies, buffer and forward as-is
        const chunks: Buffer[] = [];
        await new Promise<void>((resolve, reject) => {
          (req as any)
            .on("data", (chunk: Buffer) => chunks.push(chunk))
            .on("end", () => resolve())
            .on("error", reject);
        });
        body = Buffer.concat(chunks);
        if (!headers["content-type"]) headers["content-type"] = "application/json";
      }
    }

    const controller = new AbortController();
    const timeoutMs = Number(process.env.V1X_PROXY_TIMEOUT_MS || 15000);
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    const r = await fetch(target, {
      method,
      headers: headers as any,
      body,
      signal: controller.signal,
    } as any).finally(() => clearTimeout(timeout));

    // Stream response back to client preserving status and set-cookie
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    const contentDisposition = r.headers.get("content-disposition");
    if (contentDisposition) res.setHeader("content-disposition", contentDisposition);
    
    if (process.env.NODE_ENV !== "production") res.setHeader("x-debug-target", target);
    
    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/json";
    res.setHeader("content-type", contentType);
    if (method === "HEAD") {
      res.end();
      return;
    }
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    const msg = e?.message || "v1x resumes proxy error";
    const isAbort = msg.includes("The operation was aborted") || msg.includes("aborted");
    const status = isAbort ? 504 : 502;
    res.status(status).json({ detail: msg, code: status });
  }
}
  const { rest } = req.query;
      if (!rest) {
        // If no [...rest] path provided, this handler shouldn't be called
        // But handle gracefully by delegating to parent handler
        return res.status(404).json({ detail: "Not found" });
      }
      const idStr = Array.isArray(id) ? id[0] : id;
      const restSegments = Array.isArray(rest) ? rest : rest ? [rest] : [];
@@
