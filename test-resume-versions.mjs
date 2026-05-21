#!/usr/bin/env node
/**
 * Quick test script for resume-comparison endpoints via session proxy
 * Usage: node test-resume-versions.mjs
 * 
 * Prerequisites:
 * 1. Backend running on http://127.0.0.1:8001
 * 2. Frontend running on http://localhost:3001
 * 3. User logged in (cookie in cookies.txt or manual login first)
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:3001';

async function testVersionsEndpoints() {
  console.log('=== Resume Versions API Test ===\n');
  
  // Test 1: Health check
  console.log('1. Backend health check...');
  try {
    const healthRes = await fetch('http://127.0.0.1:8001/healthz');
    const health = await healthRes.json();
    console.log('   ✓ Backend healthy:', health);
  } catch (e) {
    console.error('   ✗ Backend not responding:', e.message);
    return;
  }

  // Test 2: Check if user is logged in (via session proxy)
  console.log('\n2. Checking session...');
  try {
    const meRes = await fetch(`${API_BASE}/api/session/me`, {
      headers: { 'Cookie': process.env.COOKIE || '' }
    });
    if (meRes.ok) {
      const user = await meRes.json();
      console.log('   ✓ Logged in as:', user.email || user.id);
    } else {
      console.log('   ✗ Not logged in (status:', meRes.status, ')');
      console.log('   → Please log in via the UI first, or set COOKIE env var');
      return;
    }
  } catch (e) {
    console.error('   ✗ Session check failed:', e.message);
    return;
  }

  // Test 3: List resumes to get a valid resume_id
  console.log('\n3. Fetching resumes...');
  try {
    const resumesRes = await fetch(`${API_BASE}/api/session/v1x/resumes`, {
      headers: { 'Cookie': process.env.COOKIE || '' }
    });
    
    if (!resumesRes.ok) {
      console.log('   ✗ Failed to fetch resumes (status:', resumesRes.status, ')');
      const error = await resumesRes.text();
      console.log('   Error:', error);
      return;
    }

    const resumes = await resumesRes.json();
    if (!resumes || resumes.length === 0) {
      console.log('   ⚠ No resumes found. Create one first via the UI.');
      return;
    }

    const testResume = resumes[0];
    console.log(`   ✓ Found ${resumes.length} resume(s). Using:`, testResume.id, testResume.title);

    // Test 4: Get versions for this resume
    console.log('\n4. Fetching versions for resume', testResume.id, '...');
    const versionsRes = await fetch(
      `${API_BASE}/api/session/v1x/resume-comparison/versions/${testResume.id}`,
      { headers: { 'Cookie': process.env.COOKIE || '' } }
    );

    console.log('   Status:', versionsRes.status, versionsRes.statusText);
    
    if (!versionsRes.ok) {
      const errorText = await versionsRes.text();
      try {
        const errorJson = JSON.parse(errorText);
        console.log('   ✗ Error:', errorJson.detail || errorJson.message || errorJson);
      } catch {
        console.log('   ✗ Error:', errorText);
      }
      console.log('\n   → This matches the 404 you saw in the UI.');
      console.log('   → Check backend logs for ownership verification.');
    } else {
      const versions = await versionsRes.json();
      console.log('   ✓ Versions:', versions.length);
      if (versions.length > 0) {
        console.log('   Sample:', versions[0]);
      }
    }

    // Test 5: Create a new version
    console.log('\n5. Creating a test version...');
    const createRes = await fetch(
      `${API_BASE}/api/session/v1x/resume-comparison/versions`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cookie': process.env.COOKIE || ''
        },
        body: JSON.stringify({
          resume_id: testResume.id,
          label: `Test Version ${new Date().toISOString()}`,
          snapshot_data: { test: true, created_by: 'test-script' }
        })
      }
    );

    console.log('   Status:', createRes.status, createRes.statusText);
    if (createRes.ok) {
      const newVersion = await createRes.json();
      console.log('   ✓ Created version:', newVersion.id);
    } else {
      const error = await createRes.text();
      console.log('   ✗ Error:', error);
    }

  } catch (e) {
    console.error('   ✗ Test failed:', e.message);
  }

  console.log('\n=== Test Complete ===');
}

testVersionsEndpoints();
