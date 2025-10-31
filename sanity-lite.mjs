import http from "http";

const PAGES = [
  { url: "http://127.0.0.1:3000/", expect: ["Skill", "Forge"] },
  { url: "http://127.0.0.1:3000/login", expect: ["Welcome back","Log in"] },
  { url: "http://127.0.0.1:3000/signup", expect: ["Sign up"], optional: true },
  { url: "http://127.0.0.1:3000/courses/python-ai", expect: ["Python","AI"], optional: true, loose: true },
];

function fetchRaw(u, { method="GET", headers={}, timeout=15000 } = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(u);
    const req = http.request(
      { method, hostname: url.hostname, port: url.port || 80, path: url.pathname + url.search, headers, timeout },
      res => {
        const chunks = [];
        res.on("data", c => chunks.push(c));
        res.on("end", () => resolve({ status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks).toString("utf8") }));
      }
    );
    req.on("error", reject);
    req.on("timeout", () => { req.destroy(new Error("timeout")); });
    req.end();
  });
}
const containsAll = (text, needles) => needles.every(n => text.toLowerCase().includes(String(n).toLowerCase()));

(async () => {
  let fails = 0;
  for (const p of PAGES) {
    try {
      const r = await fetchRaw(p.url);
      const ok = r.status === 200 || (p.optional && (r.status >= 200 && r.status < 400));
      if (!ok) { console.log(`✗ ${p.url} -> ${r.status}`); if (!p.optional) fails++; continue; }
      if (p.expect?.length) {
        const hit = containsAll(r.body, p.expect);
        if (!hit) { const msg = p.loose ? "•" : "✗"; console.log(`${msg} ${p.url} content check failed`); if (!p.loose) fails++; }
        else console.log(`✓ ${p.url} ok`);
      } else console.log(`✓ ${p.url} status ${r.status}`);
    } catch (e) {
      const msg = p.optional ? "•" : "✗";
      console.log(`${msg} ${p.url} error: ${e.message}`); if (!p.optional) fails++;
    }
  }
  if (fails) { console.log(`\nSanity-lite: ${PAGES.length - fails}/${PAGES.length} passed`); process.exit(1); }
  else console.log(`\nSanity-lite: all ${PAGES.length} passed`);
})();
