/**
 * Test export flow through Next.js proxy
 * This simulates what the UI does
 */

const BASE_FRONTEND = "http://localhost:3001";
const BASE_BACKEND = "http://127.0.0.1:8001";

async function main() {
  console.log("=".repeat(80));
  console.log("Export UI Flow Test");
  console.log("=".repeat(80));

  // Step 1: Login through Next.js proxy to get session cookie
  console.log("\n1. Login via Next.js proxy...");
  const loginRes = await fetch(`${BASE_FRONTEND}/api/session/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "test_lfupg_1762328544240@example.com",
      password: "P@ssw0rd!123"
    }),
    credentials: "include"
  });
  
  const cookies = loginRes.headers.get("set-cookie") || "";
  console.log(`   Status: ${loginRes.status}`);
  console.log(`   Cookies: ${cookies.split(";")[0]}`);
  
  if (!loginRes.ok) {
    console.log(`   Failed: ${await loginRes.text()}`);
    return;
  }

  // Step 2: Create a resume via Next.js proxy
  console.log("\n2. Create resume via Next.js proxy...");
  const createRes = await fetch(`${BASE_FRONTEND}/api/session/resumes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Cookie": cookies
    },
    body: JSON.stringify({
      title: "UI Test Resume",
      template_id: "modern",
      full_name: "Test User",
      email: "test@example.com"
    }),
    credentials: "include"
  });

  console.log(`   Status: ${createRes.status}`);
  if (!createRes.ok) {
    console.log(`   Failed: ${await createRes.text()}`);
    return;
  }

  const resume = await createRes.json();
  const resumeId = resume.id;
  console.log(`   Resume ID: ${resumeId}`);

  // Step 3: Export PDF via Next.js proxy (the exact path the UI uses)
  console.log("\n3. Export PDF via Next.js proxy...");
  const exportUrl = `${BASE_FRONTEND}/api/session/v1x/resumes/${resumeId}/export?format=pdf`;
  console.log(`   URL: ${exportUrl}`);
  
  const exportRes = await fetch(exportUrl, {
    method: "GET",
    headers: {
      "Cookie": cookies
    },
    credentials: "include"
  });

  console.log(`   Status: ${exportRes.status}`);
  console.log(`   Content-Type: ${exportRes.headers.get("content-type")}`);
  console.log(`   Content-Disposition: ${exportRes.headers.get("content-disposition")}`);
  console.log(`   X-Debug-Target: ${exportRes.headers.get("x-debug-target")}`);
  
  if (exportRes.ok) {
    const blob = await exportRes.blob();
    console.log(`   Size: ${blob.size} bytes`);
    console.log("   ✅ PDF export SUCCESS");
  } else {
    const text = await exportRes.text();
    console.log(`   ❌ PDF export FAILED: ${text.substring(0, 200)}`);
  }

  // Step 4: Export DOCX
  console.log("\n4. Export DOCX via Next.js proxy...");
  const docxUrl = `${BASE_FRONTEND}/api/session/v1x/resumes/${resumeId}/export?format=docx`;
  const docxRes = await fetch(docxUrl, {
    method: "GET",
    headers: {
      "Cookie": cookies
    },
    credentials: "include"
  });

  console.log(`   Status: ${docxRes.status}`);
  console.log(`   X-Debug-Target: ${docxRes.headers.get("x-debug-target")}`);
  
  if (docxRes.ok) {
    const blob = await docxRes.blob();
    console.log(`   Size: ${blob.size} bytes`);
    console.log("   ✅ DOCX export SUCCESS");
  } else {
    const text = await docxRes.text();
    console.log(`   ❌ DOCX export FAILED: ${text.substring(0, 200)}`);
  }

  // Step 5: Cleanup
  console.log("\n5. Cleanup...");
  await fetch(`${BASE_FRONTEND}/api/session/resumes?id=${resumeId}`, {
    method: "DELETE",
    headers: { "Cookie": cookies },
    credentials: "include"
  });
  console.log("   Resume deleted");

  console.log("\n" + "=".repeat(80));
  console.log("Test complete!");
  console.log("=".repeat(80));
}

main().catch(console.error);
