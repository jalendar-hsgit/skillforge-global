# 🧪 Quick Marketplace Testing Guide

## Step-by-Step Test Flow

### 1️⃣ Start: Browse Courses
```
URL: http://localhost:3000/marketplace
Expected: See 5-6 courses listed with cards
- Python Fundamentals ($49.99)
- Web Development Bootcamp ($99.99)
- Advanced React & Next.js ($149.99)
- Machine Learning Masterclass ($199.99)
- DevOps Essentials ($129.99)
```

### 2️⃣ Test Search & Filter
```
Action: Type in search box or select category
Expected: Courses list filters in real-time
```

### 3️⃣ Test Course Details (NEW!)
```
URL: Click "View Details" on any course
Expected: Redirect to /courses/[course-path]
Shows:
  - Course title & description
  - Price ($49.99 - $199.99)
  - Difficulty level
  - Video count
  - "What you'll learn" section
```

### 4️⃣ Test Add to Cart (From Details)
```
Action: Click "Add to Cart" button on details page
Expected: 
  - Button shows "Adding..." 
  - After 1-2 seconds, shows "✓ Added to cart successfully!"
  - Button changes to "View in Cart"
```

### 5️⃣ Test Digital Products
```
URL: http://localhost:3000/marketplace/digital-products
Expected: See 3-6 digital products
- Python Cheat Sheet ($9.99)
- Resume Template Pack ($19.99)
- Interview Prep Guide ($29.99)
```

### 6️⃣ Test Digital Product Details
```
Action: Click any product
Expected: Load /marketplace/digital-products/[id]
Shows: Product details, seller info, pricing
```

### 7️⃣ Test Add Product to Cart
```
Action: Click "Add to Cart" on product page
Expected: Same loading state + success message
```

### 8️⃣ View Cart
```
URL: http://localhost:3000/marketplace/cart
Expected: See ALL items added
- Course: Python Fundamentals ($49.99)
- Product: Python Cheat Sheet ($9.99)
- Subtotal: $58.98
- Tax: (calculated)
- Total: (displayed)
```

### 9️⃣ Remove Item from Cart
```
Action: Click "Remove" button on any item
Expected: 
  - Button shows loading state
  - Item disappears from cart
  - Total recalculates
```

### 🔟 Proceed to Checkout
```
Action: Click "Proceed to Checkout" button
Expected: 
  - Redirect to /marketplace/checkout
  - See order summary
  - See Stripe payment form
```

### 1️⃣1️⃣ Complete Payment
```
Action: Enter test card details
Card: 4242 4242 4242 4242
Expiry: 12/25
CVC: 123
Expected:
  - Payment processes
  - Order created
  - Redirect to /marketplace/orders
```

### 1️⃣2️⃣ View Order History
```
URL: http://localhost:3000/marketplace/orders
Expected: See completed order
- Order number: ORD-XXXX
- Status: COMPLETED
- Amount: $58.98 (or higher with tax)
- Payment status: COMPLETED
- Items: List of purchased courses/products
```

---

## ✅ Success Criteria

| Step | Expected Result | Status |
|------|-----------------|--------|
| Courses visible | See 5-6 courses | ✅/❌ |
| Course details | View full course info | ✅/❌ |
| Add to cart (course) | Loading state + success | ✅/❌ |
| Products visible | See 3-6 products | ✅/❌ |
| Product details | View product info | ✅/❌ |
| Add to cart (product) | Loading state + success | ✅/❌ |
| Cart display | See all items | ✅/❌ |
| Remove item | Item removed + total updates | ✅/❌ |
| Checkout page | Payment form loads | ✅/❌ |
| Order creation | Order saved | ✅/❌ |
| Order history | See completed order | ✅/❌ |

---

## 🔍 Troubleshooting

### Issue: "No courses found" on /marketplace
**Solution**: API data format was fixed
- ✅ Already resolved in this session
- Try refreshing the page

### Issue: "Page not found" when viewing course details
**Solution**: Course details page created
- ✅ New file: `src/pages/courses/[path].tsx`
- Already deployed
- Try clicking "View Details" again

### Issue: Add to cart button doesn't respond
**Solution**: Check browser console
1. Press F12 to open DevTools
2. Go to Console tab
3. Try adding to cart
4. Look for error messages
5. Check Network tab for API call

### Issue: Cart shows no items
**Solution**: Verify API is running
```powershell
curl http://localhost:8001/api/v1x/marketplace/cart
```
Should return cart data

### Issue: Stripe payment form not showing
**Solution**: Check if Stripe key is configured
- See `src/lib/stripe.ts`
- Verify `NEXT_PUBLIC_STRIPE_KEY` env var

---

## 📱 Quick Command Reference

```powershell
# Test Backend API
curl http://localhost:8001/api/v1x/marketplace/courses

# Test Frontend
curl http://localhost:3000/marketplace

# Check Error Logs
# Open browser DevTools: F12
# Console tab shows JavaScript errors
# Network tab shows API calls

# Test Specific Endpoints
curl http://localhost:8001/api/v1x/marketplace/cart
curl http://localhost:8001/api/v1x/marketplace/digital-products
curl http://localhost:8001/api/v1x/marketplace/orders
```

---

## 🎯 What Should Work Now

✅ Browse courses list
✅ Search and filter courses
✅ View course details
✅ Add courses to cart with loading state
✅ Browse digital products
✅ View product details
✅ Add products to cart with loading state
✅ View combined cart (courses + products)
✅ Remove items from cart
✅ Proceed to checkout
✅ Enter payment information
✅ Complete payment
✅ View order history
✅ See payment status

---

## 🆘 Still Having Issues?

If something doesn't work:

1. **Check Console** (F12 in browser)
   - Look for red error messages
   - Copy exact error text

2. **Check Network Tab** (F12)
   - Look for failed API calls (red)
   - Check response status codes

3. **Verify Backend Running**
   ```powershell
   curl http://localhost:8001/api/v1x/marketplace/courses
   ```
   Should return 5-6 courses

4. **Verify Frontend Running**
   ```powershell
   curl http://localhost:3000/marketplace
   ```
   Should return HTML page

5. **Check .env Variables**
   - `NEXT_PUBLIC_API_BASE` should be `http://localhost:8001`
   - `NEXT_PUBLIC_STRIPE_KEY` should be set for payment

Report issues with:
- Exact URL
- What you expected
- What actually happened
- Error messages from console
