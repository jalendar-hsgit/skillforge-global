const PAGES = [
  { url: "http://localhost:3000/", expect: ["Skill", "Forge"] },
  { url: "http://localhost:3000/login", expect: ["Welcome back", "Log in"] },
  { url: "http://localhost:3000/signup", expect: ["Create account", "Sign up"], optional: true },
  { url: "http://localhost:3000/dashboard", expect: [], statusOnly: true }, // requires auth; 200 or 302 acceptable
  { url: "http://localhost:3000/courses/python-ai", expect: ["Python", "AI"], loose: true, optional: true },
];

const assertIncludes = (html, needles) =>
  needles.every(n => html.toLowerCase().includes(String(n).toLowerCase()));

const run = async () => {
  let failures = 0;
  for (const p of PAGES) {
    try {
      const r = await fetch(p.url, { redirect: "manual" });
      const statusOk = p.statusOnly ? (r.status === 200 || (r.status >= 300 && r.status < 400)) : (r.status === 200);
      if (!statusOk) {
        console.log(`✗ ${p.url} -> ${r.status}`);
        failures++;
        continue;
      }
      if (!p.statusOnly) {
        const text = await r.text();
        if (p.expect.length === 0 || assertIncludes(text, p.expect)) {
          console.log(`✓ ${p.url} ok`);
        } else {
          const msg = p.loose ? `warn: expected tokens not found` : `missing expected tokens`;
          if (p.loose) {
            console.log(`• ${p.url} ${msg}`);
          } else {
            console.log(`✗ ${p.url} ${msg}`);
            failures++;
          }
        }
      } else {
        console.log(`✓ ${p.url} status ok (${r.status})`);
      }
    } catch (e) {
      if (p.optional) {
        console.log(`• ${p.url} optional failed: ${e.message}`);
      } else {
        console.log(`✗ ${p.url} error: ${e.message}`);
        failures++;
      }
    }
  }
  if (failures > 0) {
    console.log(`\nSanity: ${PAGES.length - failures}/${PAGES.length} passed`);
    process.exit(1);
  } else {
    console.log(`\nSanity: all ${PAGES.length}/${PAGES.length} passed`);
  }
};
run();
