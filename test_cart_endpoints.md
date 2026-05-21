# Cart Functionality Troubleshooting Guide

## Endpoints Configuration

### ✓ Backend Endpoints (All Verified)
- **POST** `/api/v1x/marketplace/cart/add` - Add course to cart
- **GET** `/api/v1x/marketplace/cart` - Get current cart
- **DELETE** `/api/v1x/marketplace/cart/{item_id}` - Remove item from cart
- **POST** `/api/v1x/marketplace/checkout` - Process checkout

### ✓ Frontend Proxy Routes (All Verified)
- **POST** `/api/session/v1x/marketplace/cart/add` → Backend `/api/v1x/marketplace/cart/add`
- **GET** `/api/session/v1x/marketplace/cart` → Backend `/api/v1x/marketplace/cart`
- **DELETE** `/api/session/v1x/marketplace/cart/{item_id}` → Backend `/api/v1x/marketplace/cart/{item_id}`
- **POST** `/api/session/v1x/marketplace/checkout` → Backend `/api/v1x/marketplace/checkout`

## Testing Steps

### 1. Test Add to Cart
```bash
# Frontend URL
http://localhost:3000/marketplace

# Action
- Click "Add to Cart" on any paid course
- Check browser console for logs
- Should see success message

# Expected
- "✓ Course added to cart!" message appears
- Cart count increases in top-right
```

### 2. Test View Cart
```bash
# Frontend URL
http://localhost:3000/marketplace/cart

# Expected
- List of items in cart
- Each item shows: title, price, date added
- Trash icon to remove item
```

### 3. Test Remove Item
```bash
# Action
- Click trash icon on any cart item
- Check browser console for logs

# Expected
- "[Remove Item] Starting removal..." in console
- "[Remove Item] Successfully removed item {id}" in console
- Item removed from cart display
```

### 4. Test Checkout
```bash
# Action
- Click "Proceed to Checkout" button
- Select payment method (coins)
- Click "Complete Purchase"

# Expected
- "Order placed successfully!" message
- Redirected to /marketplace/orders
- Order visible in orders list
```

## Common Issues & Solutions

### Issue: "Failed to remove item: Not Found"
**Cause**: Cart item doesn't exist or doesn't belong to current user

**Check**:
1. Is the cart item ID correct?
   - Browser console should show "[Remove Item] Starting removal of cart item {id}"
   - Verify the ID matches the item in the cart display

2. Is the user still logged in?
   - Open DevTools → Application → Cookies
   - Look for authentication cookies
   - If missing, user is logged out

3. Was the item already deleted?
   - Refresh the page
   - Get cart again via GET `/api/session/v1x/marketplace/cart`

**Solution**: 
- Clear browser cache and cookies
- Log out and log in again
- Try adding a new item to cart

### Issue: "Failed to add to cart: Course already in cart"
**Cause**: The same course is already in the cart

**Solution**:
- Navigate to cart and remove the duplicate item
- Then try adding again

### Issue: "Failed to add to cart: Course already purchased"
**Cause**: The user has already purchased this course

**Solution**:
- This course cannot be purchased again
- Try adding a different course

## Debug Information

### Database Check
```sql
-- Check cart items for a user
SELECT id, course_id, price, added_at FROM cart_items WHERE user_id = 3;

-- Sample: ID=1, Course=4, Price=199.99
```

### API Testing with Curl

```bash
# Add to cart
curl -X POST http://localhost:8001/api/v1x/marketplace/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"course_id": 1}'

# Get cart
curl http://localhost:8001/api/v1x/marketplace/cart \
  -H "Authorization: Bearer {token}"

# Remove from cart (item ID 1)
curl -X DELETE http://localhost:8001/api/v1x/marketplace/cart/1 \
  -H "Authorization: Bearer {token}"

# Checkout
curl -X POST http://localhost:8001/api/v1x/marketplace/checkout \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"payment_method": "coins"}'
```

## Recent Fixes Applied

1. **Enhanced error messages** - Backend now differentiates between "item not found" and "item doesn't belong to you"
2. **Better console logging** - Frontend logs cart item ID and response details
3. **All endpoints using proxy pattern** - Ensures HttpOnly cookies are properly handled
4. **All marketplace pages fixed** - Create, edit, delete, analytics all use proxy pattern

## Testing Checklist

- [ ] Add paid course to cart
- [ ] View cart - see items listed
- [ ] Remove item from cart
- [ ] Add another item and checkout
- [ ] View order in /marketplace/orders
- [ ] Create product as seller
- [ ] Upload product image
- [ ] Edit product details
- [ ] View seller analytics
- [ ] Check seller orders
