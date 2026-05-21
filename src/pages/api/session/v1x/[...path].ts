import type { NextApiRequest, NextApiResponse } from "next";

export const config = {
  api: {
    bodyParser: false, // allow streaming/multipart bodies to pass through
  },
};

// Prefer env-provided base; default to localhost (not 127.0.0.1) to avoid cookie domain confusion
const API_BASE = process.env.API_BASE || process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const started = Date.now();
    const segments = (req.query.path as string[] | undefined) || [];
    let target = `${API_BASE}/api/v1x/${segments.join("/")}`;
    
    // ALWAYS log to debug routing issues
    console.log(`[v1x-proxy] ${req.method} /api/session/v1x/${segments.join("/")} -> ${target}`);
    
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
    
    console.log(`[v1x-proxy] Full target URL: ${target}`);

    // Build headers, preserving content-type and cookies, and add common proxy headers
    const headers: Record<string, string> = {
      cookie: (req.headers.cookie as string) || "",
    };
    if (req.headers["content-type"]) headers["content-type"] = String(req.headers["content-type"]);
    if (req.headers["authorization"]) headers["authorization"] = String(req.headers["authorization"]);
    if (req.headers["x-request-id"]) headers["x-request-id"] = String(req.headers["x-request-id"]);
    headers["x-forwarded-for"] = (req.headers["x-forwarded-for"] as string) || (req.socket as any)?.remoteAddress || "";
    headers["x-forwarded-host"] = req.headers.host || "";
    headers["x-forwarded-proto"] = (req.headers["x-forwarded-proto"] as string) || "http";

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

    // Dev-only trace to aid debugging route/404 issues
    if (process.env.NODE_ENV !== "production") {
      // eslint-disable-next-line no-console
      console.log(`[v1x-proxy] ${req.method} /api/session/v1x/${segments.join("/")} -> ${target}`);
    }

    // Support a hard timeout to avoid hanging requests
    const controller = new AbortController();
    const timeoutMs = Number(process.env.V1X_PROXY_TIMEOUT_MS || 15000);
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    const r = await fetch(target, {
      method,
      headers: headers as any,
      // @ts-ignore - Node fetch accepts Readable/Buffer for body
      body,
      // credentials not used server-to-server but keep for symmetry
      signal: controller.signal,
    } as any).finally(() => clearTimeout(timeout));

    // Stream response back to client preserving status and set-cookie
    const setCookie = r.headers.get("set-cookie");
    if (setCookie) res.setHeader("set-cookie", setCookie);
    
    // Forward Content-Disposition for file downloads
    const contentDisposition = r.headers.get("content-disposition");
    if (contentDisposition) res.setHeader("content-disposition", contentDisposition);
    
    // Add debug headers to help diagnose routing issues and latency
    const latency = Date.now() - started;
    res.setHeader("x-proxy-latency", `${latency}ms`);
    res.setHeader("x-proxy-timeout-ms", `${timeoutMs}`);
    if (process.env.NODE_ENV !== "production") res.setHeader("x-debug-target", target);
    
    res.status(r.status);
    const contentType = r.headers.get("content-type") || "application/json";
    res.setHeader("content-type", contentType);
    // For HEAD requests, do not send a body
    if (method === "HEAD") {
      res.end();
      return;
    }
    const buf = Buffer.from(await r.arrayBuffer());
    res.end(buf);
  } catch (e: any) {
    // Map common errors to clearer HTTP status codes
    const msg = e?.message || "v1x proxy error";
    const isAbort = msg.includes("The operation was aborted") || msg.includes("aborted");
    const status = isAbort ? 504 : 502;
    res.status(status).json({ detail: msg, code: status });
  }
}
