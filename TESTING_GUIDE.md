# 🧪 Coding Practice Arena - Testing Guide

## Quick Start

### 1. Start Backend
```powershell
cd "d:\python code\sfg\skillforge-global\backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Wait for: `Mounted v1x router: ['Coding Practice & Simulator']`

### 2. Start Frontend (if not running)
```powershell
cd "d:\python code\sfg\skillforge-global"
npm run dev
```

Wait for: `Ready on http://localhost:3000`

---

## Test Scenarios

### ✅ Test 1: Browse Challenges
1. Open: `http://localhost:3000/practice`
2. **Expected**: See 15 challenge cards
3. **Verify**:
   - Each card shows title, difficulty, category, points
   - Success rate percentage displays (e.g., "85% success")
   - "Start Challenge" button on each card

### ✅ Test 2: Filter Challenges
1. On practice page, click **Category** dropdown
2. Select "Algorithms"
3. **Expected**: Only algorithm challenges show (5 challenges)
4. Click **Difficulty** dropdown
5. Select "Easy"
6. **Expected**: Only easy algorithm challenges (2 challenges)

### ✅ Test 3: Challenge Detail Page
1. Click on "Two Sum Problem" card
2. **Expected**: Navigate to `/practice/two-sum`
3. **Verify**:
   - Left panel shows problem description
   - Right panel shows code editor
   - Language selector shows 8 options
   - Run Code and Submit buttons visible
   - Stats show: 10 points, 85% success rate

### ✅ Test 4: Real Code Execution - Python
1. On challenge page, ensure **Python** is selected
2. Write simple code:
   ```python
   print("Hello from SkillForge!")
   print(f"2 + 2 = {2 + 2}")
   ```
3. Click **Run Code**
4. **Expected**:
   - Button shows "Running..." with spinner
   - After ~1-2 seconds, output appears:
     ```
     ✅ Success!
     
     Output:
     Hello from SkillForge!
     2 + 2 = 4
     
     Execution time: 45.67ms
     ```

### ✅ Test 5: Error Handling
1. Write code with syntax error:
   ```python
   print("Missing quote)
   ```
2. Click **Run Code**
3. **Expected**:
   - Error message shows:
     ```
     ❌ Error:
     SyntaxError: unterminated string literal
     
     Execution time: 15.23ms
     ```

### ✅ Test 6: Multiple Languages
1. **JavaScript Test**:
   - Select "JavaScript" from dropdown
   - Code: `console.log("Hello from JS")`
   - Click Run Code
   - **Expected**: Output shows "Hello from JS"

2. **Java Test** (takes longer due to compilation):
   - Select "Java"
   - Code:
     ```java
     public class Solution {
         public static void main(String[] args) {
             System.out.println("Hello from Java");
         }
     }
     ```
   - Click Run Code
   - **Expected**: Output after ~500ms

### ✅ Test 7: Code Simulators
1. On practice page, scroll to **Code Simulators** section
2. Click **"Launch"** on "Code Editor" card
3. **Expected**: Navigate to `/practice/simulator/code-editor`
4. **Verify**:
   - Sidebar shows 8 simulator types
   - Code editor with Python template
   - Run, Copy, Reset buttons
   - Output panel below

### ✅ Test 8: API Direct Test
```powershell
# Test challenge list
curl http://localhost:8001/api/v1x/coding-practice/challenges?limit=3

# Test single challenge
curl http://localhost:8001/api/v1x/coding-practice/challenges/two-sum

# Test code execution
$body = '{"language":"python","code":"print(\"Hello\")"}' 
Invoke-RestMethod -Uri "http://localhost:8001/api/v1x/coding-practice/run" `
  -Method POST -Body $body -ContentType "application/json"
```

---

## Expected Results Summary

| Test | Feature | Status | Time |
|------|---------|--------|------|
| 1 | Browse challenges | ✅ | <1s |
| 2 | Filter challenges | ✅ | <1s |
| 3 | Challenge detail | ✅ | <1s |
| 4 | Python execution | ✅ | ~1-2s |
| 5 | Error handling | ✅ | ~1s |
| 6 | Multi-language | ✅ | 1-3s |
| 7 | Simulators | ✅ | <1s |
| 8 | API direct | ✅ | <1s |

---

## Troubleshooting

### Backend won't start
```powershell
# Check if port is in use
netstat -ano | findstr :8001

# Kill process if needed
taskkill /PID <PID> /F

# Check Python environment
python --version  # Should be 3.11+
```

### Frontend shows "No challenges found"
1. Check backend is running: `curl http://localhost:8001/healthz`
2. Check database has data: `python backend/check_challenges.py`
3. Check browser console for errors (F12)

### Code execution fails
1. Check backend logs for errors
2. Verify Python/Node is installed:
   ```powershell
   python --version
   node --version
   ```
3. Check code_executor is loaded: Backend logs should show no import errors

### API returns 404
1. Verify endpoint URL is correct
2. Check router is mounted: Backend logs should show "Mounted v1x router: ['Coding Practice & Simulator']"
3. Try with full URL: `http://localhost:8001/api/v1x/coding-practice/challenges`

---

## Performance Benchmarks

### Expected Execution Times
- **Python**: 50-200ms
- **JavaScript/Node**: 30-150ms
- **Java** (with compilation): 500-1000ms
- **C++** (with compilation): 400-800ms
- **Go**: 300-600ms
- **Rust** (with compilation): 800-1500ms

### API Response Times
- List challenges: <100ms
- Get challenge detail: <50ms
- Run code (Python): 50-200ms
- Submit solution: 200-3000ms (with test cases)

---

## Known Issues

### Current Limitations
1. ⚠️ **Local execution mode** - Code runs directly on server (dev only)
2. ⚠️ **No stdin support** - Cannot pass interactive input
3. ⚠️ **No real-time output** - Output shows only after completion
4. ⚠️ **Limited error details** - Compiler errors could be clearer

### Security Notes
- **DO NOT** use in production without Docker sandboxing
- Enable Docker mode: Change `use_docker=False` to `True` in `coding_practice.py`
- Consider using Judge0 or Sphere Engine for production

---

## Next Features to Test (Not Yet Implemented)

- [ ] Monaco Editor integration
- [ ] Test case validation UI
- [ ] Code submission with scoring
- [ ] Progressive hints unlock
- [ ] Leaderboard display
- [ ] Achievement badges
- [ ] Syntax highlighting improvements
- [ ] Autocomplete suggestions
- [ ] Debugging breakpoints

---

## Success Criteria

### ✅ Minimum Viable Product (MVP)
- [x] 15 challenges browsable
- [x] Filters work correctly
- [x] Challenge pages load with data
- [x] Code editor functional
- [x] Real Python execution
- [x] Real JavaScript execution
- [x] Error messages display
- [x] Execution time shown

### 🎯 Full Feature Complete
- [ ] All 8 languages tested
- [ ] Test cases validate automatically
- [ ] Submissions save to database
- [ ] Coins awarded for completion
- [ ] Leaderboard shows rankings
- [ ] Hints unlock with coins
- [ ] Monaco Editor integrated
- [ ] Debugging tools available

---

## Contact & Support

### If Tests Fail
1. Check both terminals for error messages
2. Review browser console (F12 → Console tab)
3. Verify all dependencies installed
4. Check documentation: `CODING_PRACTICE_COMPLETE_STATUS.md`

### Resources
- Backend API docs: `http://localhost:8001/docs`
- Frontend dev: `http://localhost:3000`
- Database check: `python backend/check_challenges.py`
- Full status: `CODING_PRACTICE_COMPLETE_STATUS.md`

---

**Last Updated**: December 12, 2025  
**Tested By**: Development Team  
**Status**: ✅ Core Features Working
