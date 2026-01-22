# Cart Remove DELETE 404 Debug Guide

## Problem
User reports: `DELETE /api/session/v1x/marketplace/cart/1` returns `404 Not Found`

## Root Cause Investigation
The backend logs show the request reaching with `/api/session/` in the path:
```
DELETE /api/session/v1x/marketplace/cart/1 -> 404
```

This indicates the Next.js proxy is NOT stripping the `/session/` prefix before forwarding to the backend.

## Files to Check
1. `src/pages/api/session/v1x/[...path].ts` - Main v1x catch-all proxy
2. `src/pages/api/session/v1x/marketplace/cart/[id].ts` - Specific cart item handler (created recently)
3. `src/pages/api/session/v1x/marketplace/cart.ts` - Cart base handler
4. `src/pages/marketplace/cart.tsx` - Frontend cart page

## Next.js Routing Issue
The `[...path].ts` at `/api/session/v1x/` level may be intercepting requests before the specific `/api/session/v1x/marketplace/cart/[id].ts` route can handle them.

In Next.js, when you have nested dynamic routes, the catch-all may take precedence depending on routing order.

## Required Actions
1. **RESTART the frontend** (npm run dev) to apply any recent changes
2. **Run diagnostic test** to see actual behavior:
   ```bash
   python test_flow_debug.py
   ```
3. Check browser console for any proxy errors
4. Verify Next.js is properly routing to the specific handler

## Expected Behavior After Fix
- Frontend calls: `DELETE /api/session/v1x/marketplace/cart/1`
- Next.js proxy intercepts and forwards: `DELETE /api/v1x/marketplace/cart/1`
- Backend receives at `/api/v1x/marketplace/cart/1` (NOT `/api/session/...`)
- Backend returns 200 OK with item deleted

## If Still Failing After Restart
1. Check if `[id].ts` file actually exists and is properly formatted
2. Verify `[...path].ts` is correctly parsing and forwarding requests
3. Add console.log statements to trace the request flow
4. Check Next.js build logs for any errors

## Test Commands
```bash
# Test backend directly
python test_cart_delete_diagnostic.py

# Test complete flow
python test_cart_complete.py

# Test via frontend proxy
python test_cart_frontend.py

# Check actual request/response
python test_flow_debug.py
```
