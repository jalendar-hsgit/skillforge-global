import http from "http";
const BASE = "http://127.0.0.1:3000";
const EMAIL = "sync_tester@example.com";
const PASSWORD = "secret123";

function request(u, { method="GET", headers={}, body, timeout=15000 } = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(u);
    const req = http.request(
      { method, hostname: url.hostname, port: url.port || 80, path: url.pathname + url.search, headers, timeout },
      res => {
        const chunks = [];
        res.on("data", c => chunks.push(c));
        res.on("end", () => resolve({ status: res.statusCode, headers: res.headers, text: Buffer.concat(chunks).toString("utf8") }));
      }
    );
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(new Error("timeout")); });
    if (body) req.write(body);
    req.end();
  });
}

(async () => {
  const loginBody = JSON.stringify({ email: EMAIL, password: PASSWORD });
  const login = await request(`${BASE}/api/session/login`, {
    method: "POST",
    headers: { "content-type": "application/json", "content-length": Buffer.byteLength(loginBody) },
    body: loginBody,
  });
  console.log("login:", login.status, login.text);
  if (login.status !== 200) process.exit(1);

  const setCookie = login.headers["set-cookie"]?.[0] || login.headers["set-cookie"] || "";
  const tokenCookie = (setCookie.split(";")[0] || "").trim();
  if (!tokenCookie.startsWith("token=")) { console.log("✗ token cookie missing"); process.exit(1); }
  console.log("✓ cookie captured");

  const me = await request(`${BASE}/api/session/me`, { headers: { cookie: tokenCookie } });
  console.log("me:", me.status, me.text);

  const progress = await request(`${BASE}/api/progress/get?path=python-ai`, { headers: { cookie: tokenCookie } });
  console.log("progress get:", progress.status);
})();
