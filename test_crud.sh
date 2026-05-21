#!/bin/bash

echo "=========================================="
echo "DATABASE & CRUD OPERATIONS TEST"
echo "=========================================="
echo ""

echo "1. CHECK DATABASE TABLES"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -c "\dt public.users;" 2>&1 || echo "Failed to list users table"
echo ""

echo "2. COUNT USERS IN DATABASE"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -t -c "SELECT COUNT(*) FROM users;" 2>&1 || echo "Failed to count users"
echo ""

echo "3. LIST SAMPLE USERS (First 3)"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT id, email, role FROM users LIMIT 3;" 2>&1 || echo "Failed to list users"
echo ""

echo "4. CHECK LOGIN_HISTORY TABLE"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -c "\dt public.login_history;" 2>&1 || echo "Failed to check login_history table"
echo ""

echo "5. COUNT LOGIN RECORDS"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -t -c "SELECT COUNT(*) FROM login_history;" 2>&1 || echo "Failed to count login_history"
echo ""

echo "6. TEST API - GET COURSES (READ)"
echo "--------------------------------"
curl -s http://localhost:8001/api/v1/courses | head -c 200
echo ""
echo ""

echo "7. TEST API - LIST USERS (READ)"
echo "--------------------------------"
curl -s http://localhost:8001/api/v1/users | head -c 200
echo ""
echo ""

echo "8. TEST LOGIN ENDPOINT (CREATE + READ)"
echo "--------------------------------"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john.doe@example.com","password":"Password123!"}')

if echo "$RESPONSE" | grep -q "access_token"; then
  echo "✓ LOGIN SUCCESSFUL - Token generated"
  echo "$RESPONSE" | head -c 300
else
  echo "✗ LOGIN FAILED or returned unexpected response"
  echo "$RESPONSE" | head -c 300
fi
echo ""
echo ""

echo "9. CHECK LOGIN_HISTORY RECORDS (after login attempt)"
echo "--------------------------------"
docker exec skillforge-postgres psql -U admin -d skillforge -c "SELECT id, user_id, success, login_time FROM login_history ORDER BY login_time DESC LIMIT 3;" 2>&1 || echo "Failed to list login_history"
echo ""

echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
