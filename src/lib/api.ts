const RAW_BASE = process.env.NEXT_PUBLIC_API_BASE?.trim() || "http://127.0.0.1:8001";
export const API_BASE = RAW_BASE.replace(/\/+$/, "");

function buildUrl(path: string) {
  const clean = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${clean}`;
}

export async function apiGet(path: string) {
  const url = buildUrl(path);
  const res = await fetch(url, { credentials: "include" });
  if (!res.ok) {
    let errorMsg = `GET ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export async function apiPost(path: string, data: any) {
  const url = buildUrl(path);
  const res = await fetch(url, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data ?? {})
  });
  if (!res.ok) {
    let errorMsg = `POST ${url} failed (${res.status})`;
    try {
      const errorData = await res.json();
      if (errorData.detail) {
        errorMsg = errorData.detail;
      }
    } catch (e) {
      // If JSON parsing fails, use default error message
    }
    throw new Error(errorMsg);
  }
  return res.json();
}
