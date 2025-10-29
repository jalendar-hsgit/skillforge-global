export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8001";

async function request(path: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

// session goes through Next proxies to forward cookies
async function session(path: string, opts: RequestInit = {}) {
  const res = await fetch(`/api/session${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    credentials: "include",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}

export const API = {
  signup: (email: string, password: string) =>
    session("/signup", { method: "POST", body: JSON.stringify({ email, password }) }),
  login: (email: string, password: string) =>
    session("/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => session("/me"),
  logout: () => session("/logout", { method: "POST" }),

  // public/backend data (not cookie-dependent)
  courses: (path: string) => request(`/api/v1/courses?path=${encodeURIComponent(path)}`),
  quizzes: (path: string) => request(`/api/v1/quizzes?path=${encodeURIComponent(path)}`),
};
