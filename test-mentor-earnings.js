#!/usr/bin/env node

/**
 * Interactive Test Script for Mentor Earnings System
 * Run: node test-mentor-earnings.js
 */

const http = require('http');

const API_BASE = 'http://localhost:8001';
const MENTOR_SESSION = process.env.MENTOR_SESSION || 'test-session';
const ADMIN_SESSION = process.env.ADMIN_SESSION || 'test-admin-session';

// Helper function to make HTTP requests
function makeRequest(path, method = 'GET', body = null, session = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, API_BASE);
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (session) {
      options.headers['Cookie'] = `session=${session}`;
    }

    const req = http.request(url, options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          resolve({
            status: res.statusCode,
            body: JSON.parse(data),
            headers: res.headers,
          });
        } catch {
          resolve({
            status: res.statusCode,
            body: data,
            headers: res.headers,
          });
        }
      });
    });

    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// Test functions
async function testGetSummary() {
  console.log('\n📊 Testing: Get Earnings Summary');
  try {
    const result = await makeRequest(
      '/api/v1x/mentors/payouts/summary',
      'GET',
      null,
      MENTOR_SESSION
    );
    console.log('Status:', result.status);
    console.log('Response:', JSON.stringify(result.body, null, 2));
    return result.status === 200;
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

async function testGetPaymentMethods() {
  console.log('\n💳 Testing: Get Payment Methods');
  try {
    const result = await makeRequest(
      '/api/v1x/mentors/payouts/payment-methods',
      'GET',
      null,
      MENTOR_SESSION
    );
    console.log('Status:', result.status);
    console.log('Response:', JSON.stringify(result.body, null, 2));
    return result.status === 200;
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

async function testCreatePaymentMethod() {
  console.log('\n➕ Testing: Create Payment Method');
  const data = {
    account_holder_name: 'Test Mentor',
    bank_name: 'Test Bank',
    account_number: '123456789012345',
    routing_number: '021000021',
    is_default: true,
  };
  try {
    const result = await makeRequest(
      '/api/v1x/mentors/payouts/payment-methods',
      'POST',
      data,
      MENTOR_SESSION
    );
    console.log('Status:', result.status);
    console.log('Response:', JSON.stringify(result.body, null, 2));
    return result.status === 201;
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

async function testGetPayoutHistory() {
  console.log('\n📜 Testing: Get Payout History');
  try {
    const result = await makeRequest(
      '/api/v1x/mentors/payouts/history',
      'GET',
      null,
      MENTOR_SESSION
    );
    console.log('Status:', result.status);
    console.log('Response:', JSON.stringify(result.body, null, 2));
    return result.status === 200;
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

async function testAdminGetPending() {
  console.log('\n⏳ Testing: Admin Get Pending Payouts');
  try {
    const result = await makeRequest(
      '/api/v1x/admin/payouts/pending',
      'GET',
      null,
      ADMIN_SESSION
    );
    console.log('Status:', result.status);
    console.log('Response:', JSON.stringify(result.body, null, 2));
    return result.status === 200;
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

async function testHealthCheck() {
  console.log('\n🏥 Testing: Backend Health Check');
  try {
    const result = await makeRequest('/health', 'GET');
    console.log('Status:', result.status);
    return result.status === 200 || result.status === 404; // 404 is ok if endpoint doesn't exist
  } catch (err) {
    console.error('Error:', err.message);
    return false;
  }
}

// Main test runner
async function runTests() {
  console.log('═══════════════════════════════════════════════════════════');
  console.log('🧪 MENTOR EARNINGS SYSTEM - API TEST SUITE');
  console.log('═══════════════════════════════════════════════════════════');

  const tests = [
    { name: 'Health Check', fn: testHealthCheck },
    { name: 'Get Earnings Summary', fn: testGetSummary },
    { name: 'Get Payment Methods', fn: testGetPaymentMethods },
    { name: 'Create Payment Method', fn: testCreatePaymentMethod },
    { name: 'Get Payout History', fn: testGetPayoutHistory },
    { name: 'Admin Get Pending Payouts', fn: testAdminGetPending },
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      const result = await test.fn();
      if (result) {
        console.log(`✅ PASSED: ${test.name}`);
        passed++;
      } else {
        console.log(`❌ FAILED: ${test.name}`);
        failed++;
      }
    } catch (err) {
      console.log(`❌ ERROR: ${test.name} - ${err.message}`);
      failed++;
    }
  }

  console.log('\n═══════════════════════════════════════════════════════════');
  console.log(`📊 RESULTS: ${passed} passed, ${failed} failed`);
  console.log('═══════════════════════════════════════════════════════════\n');

  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(console.error);
