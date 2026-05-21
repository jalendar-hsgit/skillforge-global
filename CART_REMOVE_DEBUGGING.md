# Cart Remove - Debugging & Diagnostics Guide

## Changes Made to Help Debug Issues

### Frontend Improvements (`src/pages/marketplace/cart.tsx`)
1. **Enhanced logging**: Now logs cart state before attempting deletion
2. **Better error messages**: Specific messages for 404 (item not found), 403 (permission), and other errors
3. **Auto-refresh on 404**: If item was already deleted, refreshes cart automatically
4. **Detailed error reporting**: Shows both status code and error details
5. **Network error details**: Shows exact error message if network fails

### Backend Improvements (`backend/app/api/v1x/marketplace.py`)
1. **Console logging**: Every step of the delete process is logged to backend console
2. **User verification**: Logs which user is attempting what action
3. **Item status checks**: Logs item existence and ownership checks
4. **Commit confirmation**: Logs successful deletion

## How to Diagnose Issues

### Step 1: Check Browser Console
1. Open browser DevTools (F12)
2. Click on "Console" tab
3. Try to delete an item
4. Look for `[Remove Item]` logs

**Expected output**:
```
[Remove Item] Starting removal of cart item 1
[Remove Item] Calling DELETE /api/session/v1x/marketplace/cart/1
[Remove Item] Current cart before deletion: (5) [{…}, {…}, {…}, {…}, {…}]
[Remove Item] Response status: 200, statusText: OK
[Remove Item] Successfully removed item 1
[Remove Item] Cart refreshed after deletion
```

**If you see an error**:
```
[Remove Item] Starting removal of cart item 1
[Remove Item] Response status: 401, statusText: Unauthorized
Error removing item: {status: 401, statusText: 'Unauthorized', itemId: 1, error: {…}}
```

### Step 2: Check Backend Logs
1. Look at backend terminal where you ran `uvicorn`
2. Try to delete an item from the cart
3. Look for `[DELETE /cart/X]` logs

**Expected output**:
```
[DELETE /cart/1] User 3 (admin@skillforge.com) attempting to remove item 1
[DELETE /cart/1] Item 1 found: course_id=4, user_id=3
[DELETE /cart/1] Deleting item 1...
[DELETE /cart/1] Successfully deleted item 1
```

**If authentication fails**:
```
[DELETE /cart/1] User 3 (admin@skillforge.com) attempting to remove item 1
[DELETE /cart/1] Item 1 found: course_id=4, user_id=3
[DELETE /cart/1] Permission denied: item belongs to user 3, not 0
```

### Step 3: Check Network Tab
1. Open DevTools (F12)
2. Go to "Network" tab
3. Delete an item
4. Look for DELETE request to `/api/session/v1x/marketplace/cart/1`

**Expected**:
- Status: **200**
- Response: `{"message": "Item removed from cart", "item_id": 1}`

**If 401 (Unauthorized)**:
- Means authentication failed
- Check if you're logged in
- Check if cookies are being sent

**If 404 (Not Found)**:
- Item doesn't exist
- Already been deleted
- Wrong item ID

**If 403 (Forbidden)**:
- Item belongs to different user
- Shouldn't happen in normal use

### Step 4: Check Application Storage
1. Open DevTools (F12)
2. Go to "Application" tab
3. Click "Cookies" → "localhost:3000"
4. Look for `token` cookie

**Expected**:
- Cookie named `token` exists
- Has a long encoded value
- Shows as `HttpOnly`

**If missing**:
- You're not logged in
- Session expired
- Need to login again

## Common Error Scenarios & Solutions

### Error: "Item not found (ID: X)"
```
[Remove Item] Response status: 404
Error: "Cart item 1 not found"
```

**Why**: Item doesn't exist (maybe already deleted)
**Solution**: 
1. Refresh cart page (F5)
2. Check that item is still showing
3. Try deleting a different item

### Error: Status 401 - Unauthorized
```
[Remove Item] Response status: 401
Error: "Invalid token"
```

**Why**: Session expired or not logged in
**Solution**:
1. Clear cookies: DevTools → Application → Cookies → Delete all
2. Log out: Go to account settings
3. Log back in: Visit /login
4. Try again

### Error: Status 403 - Forbidden
```
[Remove Item] Response status: 403
Error: "This cart item does not belong to you"
```

**Why**: Logged in as wrong user
**Solution**:
1. Check top-right corner - who are you logged in as?
2. Log out and log in with correct email
3. Try again

### Error: Network error
```
[Remove Item] Exception: TypeError: Failed to fetch
```

**Why**: Backend not running or network issue
**Solution**:
1. Check backend terminal - is it running?
2. Restart backend: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` (from backend/ dir)
3. Hard refresh frontend: Ctrl+Shift+R
4. Try again

### Item deleted but UI not updated
```
[Remove Item] Response status: 200
[Remove Item] Successfully removed item 1
[Remove Item] Cart refreshed after deletion
```
But item is still showing in the list

**Why**: JavaScript error after deletion
**Solution**:
1. Check console for JavaScript errors
2. Manually refresh: F5
3. Check backend logs for any issues

## Testing Steps

### Quick Test
1. Open http://localhost:3000/marketplace/cart
2. Open DevTools (F12)
3. Go to Console tab
4. Try to delete one item
5. Check logs show success
6. Verify item disappeared from list
7. Refresh page (F5)
8. Verify item is still gone

### Comprehensive Test
1. Log out and log back in
2. Go to cart page
3. Note how many items are in cart
4. Delete item 1 → check console logs
5. Verify item removed from UI
6. Delete item 2 → check console logs
7. Verify new item removed from UI
8. Refresh page → verify deletions persisted
9. Delete all remaining items
10. Verify cart shows "empty"

## Reporting Issues

If deletion still doesn't work, please provide:

1. **Error message** from the alert box
2. **Console logs** - copy the `[Remove Item]` logs
3. **Network response** - status code and response body
4. **Backend logs** - the `[DELETE /cart/X]` lines
5. **Browser info** - Chrome/Firefox/Safari version
6. **Cart state** - how many items in cart?
7. **User** - which account are you logged in as?

## Expected Behavior After Fix

### Successful Deletion
1. Click delete button → spinner appears
2. Console logs show deletion starting
3. Item disappears from UI
4. Cart total updates immediately
5. No error message
6. Refresh page → item is still gone

### Clear Feedback on Errors
1. Click delete button
2. If error occurs → specific error message shown
3. Console logs explain exactly what went wrong
4. Cart UI refreshed with current state
5. User knows what to do next

## Verification Checklist

- [ ] Console logging shows deletion attempt
- [ ] Backend logs show deletion request
- [ ] Network tab shows 200 status
- [ ] Item disappears from UI
- [ ] Cart total updates
- [ ] Deletion persists after refresh
- [ ] Multiple deletions work
- [ ] Error handling shows specific errors
- [ ] No JavaScript errors in console
- [ ] Backend endpoint returns correct response

## If Everything Fails

Try the backend direct test:

```bash
# 1. Login
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@skillforge.com","password":"admin123"}' \
  -c cookies.txt

# 2. Get cart
curl http://localhost:8001/api/v1x/marketplace/cart -b cookies.txt

# 3. Delete item (replace 1 with actual ID from cart)
curl -X DELETE http://localhost:8001/api/v1x/marketplace/cart/1 \
  -b cookies.txt

# 4. Verify deletion
curl http://localhost:8001/api/v1x/marketplace/cart -b cookies.txt
```

If this works, the issue is in the frontend/proxy.
If this fails, the issue is in the backend.

## Getting Help

1. **Check this guide** - follow diagnostic steps above
2. **Provide error details** - exact error message matters
3. **Check logs** - both browser console and backend logs
4. **Try clearing cache** - sometimes old code causes issues
5. **Restart servers** - fresh start can resolve temporary issues

---

**Status**: Enhanced logging in place to help diagnose any remaining issues
**Next Step**: Run diagnostic tests above and report any errors found

