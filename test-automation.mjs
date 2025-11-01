#!/usr/bin/env node
import http from "http";
import https from "https";
import { readFileSync } from "fs";

const BASE = process.env.FRONTEND_BASE || "http://localhost:3000";
const EMAIL = "autotest@example.com";
const PASSWORD = "TestPass123!";

function request(urlString, { method = "GET", headers = {}, body, timeout = 20000 } = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlString);
    const protocol = url.protocol === "https:" ? https : http;
    const options = {
      method,
      hostname: url.hostname,
      port: url.port || (url.protocol === "https:" ? 443 : 80),
      path: url.pathname + url.search,
      headers,
      timeout,
    };
    const req = protocol.request(options, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          text: Buffer.concat(chunks).toString("utf8"),
        });
      });
    });
    req.on("error", reject);
    req.on("timeout", () => {
      req.destroy(new Error("Request timeout"));
    });
    if (body) req.write(body);
    req.end();
  });
}

function extractCookie(setCookieHeader) {
  if (!setCookieHeader) return "";
  const raw = Array.isArray(setCookieHeader) ? setCookieHeader[0] : setCookieHeader;
  return (raw.split(";")[0] || "").trim();
}

async function main() {
  console.log("\n=== SkillForge Resume E2E Automation Test ===\n");

  // 1. Signup
  console.log("1️⃣  Signup...");
  const signupBody = JSON.stringify({ email: EMAIL, password: PASSWORD });
  const signupRes = await request(`${BASE}/api/session/signup`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: signupBody,
  });
  console.log(`   Signup: ${signupRes.status} ${signupRes.text.substring(0, 80)}`);
  if (signupRes.status !== 200 && signupRes.status !== 400) {
    throw new Error(`Signup failed: ${signupRes.status}`);
  }

  // 2. Login
  console.log("\n2️⃣  Login...");
  const loginBody = JSON.stringify({ email: EMAIL, password: PASSWORD });
  const loginRes = await request(`${BASE}/api/session/login`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: loginBody,
  });
  console.log(`   Login: ${loginRes.status} ${loginRes.text.substring(0, 80)}`);
  if (loginRes.status !== 200) throw new Error(`Login failed: ${loginRes.status}`);
  const cookie = extractCookie(loginRes.headers["set-cookie"]);
  if (!cookie || !cookie.startsWith("token=")) {
    console.log(`   DEBUG: set-cookie header = ${JSON.stringify(loginRes.headers["set-cookie"])}`);
    throw new Error("Token cookie missing");
  }
  console.log(`   ✓ Cookie captured`);

  // 3. Get /me
  console.log("\n3️⃣  Get user profile (/api/session/me)...");
  const meRes = await request(`${BASE}/api/session/me`, { headers: { cookie } });
  console.log(`   Me: ${meRes.status} ${meRes.text.substring(0, 80)}`);
  if (meRes.status !== 200) throw new Error("GET /me failed");
  const user = JSON.parse(meRes.text);
  console.log(`   ✓ User ID: ${user.id}, Email: ${user.email}`);

  // 4. Create Resume
  console.log("\n4️⃣  Create Resume...");
  const createBody = JSON.stringify({
    full_name: "John Doe",
    email: "john@example.com",
    phone: "555-1234",
    professional_summary: "Experienced developer.",
  });
  const createRes = await request(`${BASE}/api/session/resumes`, {
    method: "POST",
    headers: { "content-type": "application/json", cookie },
    body: createBody,
  });
  console.log(`   Create: ${createRes.status}`);
  if (createRes.status !== 201) throw new Error(`Create resume failed: ${createRes.status}`);
  const createdResume = JSON.parse(createRes.text);
  const resumeId = createdResume.id;
  console.log(`   ✓ Created resume ID: ${resumeId}`);

  // 5. Get Resume
  console.log("\n5️⃣  Get Resume...");
  const getRes = await request(`${BASE}/api/session/resumes?id=${resumeId}`, { headers: { cookie } });
  console.log(`   Get: ${getRes.status}`);
  if (getRes.status !== 200) throw new Error(`Get resume failed: ${getRes.status}`);
  const fetchedResume = JSON.parse(getRes.text);
  console.log(`   ✓ Fetched: ${fetchedResume.full_name}`);

  // 6. PATCH Resume
  console.log("\n6️⃣  PATCH Resume...");
  const patchBody = JSON.stringify({ full_name: "John Smith", phone: "555-9999" });
  const patchRes = await request(`${BASE}/api/session/resumes?id=${resumeId}`, {
    method: "PATCH",
    headers: { "content-type": "application/json", cookie },
    body: patchBody,
  });
  console.log(`   Patch: ${patchRes.status}`);
  if (patchRes.status !== 200) throw new Error(`PATCH resume failed: ${patchRes.status}`);
  const patchedResume = JSON.parse(patchRes.text);
  console.log(`   ✓ Patched name: ${patchedResume.full_name}`);

  // 7. AI Professional Summary
  console.log("\n7️⃣  AI Professional Summary...");
  const aiBody = JSON.stringify({ title: "Software Engineer", years_of_experience: 5 });
  const aiRes = await request(`${BASE}/api/session/resume-ai/professional-summary`, {
    method: "POST",
    headers: { "content-type": "application/json", cookie },
    body: aiBody,
  });
  console.log(`   AI summary: ${aiRes.status}`);
  if (aiRes.status !== 200) throw new Error(`AI summary failed: ${aiRes.status}`);
  const aiData = JSON.parse(aiRes.text);
  console.log(`   ✓ AI summary: ${aiData.summary.substring(0, 60)}...`);

  // 8. AI Bullet Points
  console.log("\n8️⃣  AI Bullet Points...");
  const bulletBody = JSON.stringify({ role: "Backend Developer", description: "Built APIs" });
  const bulletRes = await request(`${BASE}/api/session/resume-ai/bullet-points`, {
    method: "POST",
    headers: { "content-type": "application/json", cookie },
    body: bulletBody,
  });
  console.log(`   AI bullets: ${bulletRes.status}`);
  if (bulletRes.status !== 200) throw new Error(`AI bullets failed: ${bulletRes.status}`);
  const bulletData = JSON.parse(bulletRes.text);
  console.log(`   ✓ Generated ${bulletData.bullet_points.length} bullet points`);

  // 9. Duplicate Resume
  console.log("\n9️⃣  Duplicate Resume...");
  const dupBody = JSON.stringify({ action: "duplicate" });
  const dupRes = await request(`${BASE}/api/session/resumes?id=${resumeId}`, {
    method: "POST",
    headers: { "content-type": "application/json", cookie },
    body: dupBody,
  });
  console.log(`   Duplicate: ${dupRes.status}`);
  if (dupRes.status !== 200 && dupRes.status !== 201) throw new Error(`Duplicate failed: ${dupRes.status}`);
  const dupResume = JSON.parse(dupRes.text);
  console.log(`   ✓ Duplicated resume ID: ${dupResume.id}`);

  // 10. List Resumes
  console.log("\n🔟 List Resumes...");
  const listRes = await request(`${BASE}/api/session/resumes`, { headers: { cookie } });
  console.log(`   List: ${listRes.status}`);
  if (listRes.status !== 200) throw new Error(`List resumes failed: ${listRes.status}`);
  const resumes = JSON.parse(listRes.text);
  console.log(`   ✓ Total resumes: ${resumes.length}`);

  // 11. Delete Original Resume
  console.log("\n1️⃣1️⃣ Delete Original Resume...");
  const delRes = await request(`${BASE}/api/session/resumes?id=${resumeId}`, {
    method: "DELETE",
    headers: { cookie },
  });
  console.log(`   Delete: ${delRes.status}`);
  if (delRes.status !== 200 && delRes.status !== 204) throw new Error(`Delete failed: ${delRes.status}`);
  console.log(`   ✓ Deleted resume ID: ${resumeId}`);

  // 12. Courses
  console.log("\n1️⃣2️⃣ Get Courses...");
  const coursesRes = await request(`${BASE}/api/courses`, { headers: { cookie } });
  console.log(`   Courses: ${coursesRes.status}`);
  if (coursesRes.status !== 200) throw new Error(`Courses failed: ${coursesRes.status}`);
  const courses = JSON.parse(coursesRes.text);
  console.log(`   ✓ Found ${courses.length} courses`);

  // 13. Progress
  console.log("\n1️⃣3️⃣ Get Progress...");
  const progressRes = await request(`${BASE}/api/progress/get?path=python-ai`, { headers: { cookie } });
  console.log(`   Progress: ${progressRes.status} ${progressRes.text.substring(0, 80)}`);
  // Progress might be 404 if no progress yet, that's OK

  console.log("\n✅ All E2E automation tests passed!\n");
}

main().catch((err) => {
  console.error("\n❌ Test failed:", err.message);
  process.exit(1);
});
