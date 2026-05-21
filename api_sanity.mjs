const BASE = "http://localhost:3000";
const EMAIL = "sync_tester@example.com";
const PASSWORD = "secret123";

const postJSON = async (url, body, cookie) => {
  const r = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(cookie ? { cookie } : {}),
    },
    body: JSON.stringify(body),
    redirect: "manual",
  });
  const setCookie = r.headers.get("set-cookie") || "";
  const text = await r.text();
  return { status: r.status, text, setCookie };
};

const getWithCookie = async (url, cookie) => {
  const r = await fetch(url, { headers: cookie ? { cookie } : {}, redirect: "manual" });
  const text = await r.text();
  return { status: r.status, text };
};

const main = async () => {
  // 1) Login to Next API
  const login = await postJSON(`${BASE}/api/session/login`, { email: EMAIL, password: PASSWORD });
  console.log("login:", login.status, login.text);
  if (login.status !== 200) process.exit(1);

  // 2) Capture token cookie
  const cookie = (login.setCookie || "").split(";")[0];
  if (!cookie || !cookie.startsWith("token=")) {
    console.log("✗ missing token cookie");
    process.exit(1);
  } else {
    console.log("✓ got cookie");
  }

  // 3) /api/session/me should show user
  const me = await getWithCookie(`${BASE}/api/session/me`, cookie);
  console.log("me:", me.status, me.text);

  // 4) Optional: progress proxy endpoint
  const prog = await fetch(`${BASE}/api/progress/get?path=python-ai`, { headers: { cookie } });
  console.log("progress get:", prog.status);
};
main();
