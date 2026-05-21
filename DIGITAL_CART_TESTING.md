# Digital Products Cart - Testing Guide

## What's Been Implemented

✅ **Digital Products Cart Integration**
- Digital products now add to cart (not direct purchase)
- Proper checkout with mixed items (courses + digital products)
- OrderItem model tracks individual items in orders
- Full multi-item order support

## Quick Testing

### 1. Start Services

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Frontend:**
```bash
npm run dev
# Runs on http://localhost:3001
```

### 2. Test Cart Flow

**Add Digital Product to Cart:**
1. Navigate to http://localhost:3001/marketplace/digital-products
2. Click "Add to Cart" on any product
3. ✓ Should see "Added to cart!" notification
4. ✓ Cart icon count should increment

**Add Course to Cart:**
1. Navigate to http://localhost:3001/marketplace
2. Click "Add to Cart" on any course
3. ✓ Should see "Added to cart!" notification
4. ✓ Cart icon count should increment

**View Mixed Cart:**
1. Click cart icon or go to /marketplace/cart
2. ✓ Should show both digital product and course
3. ✓ Prices should be correct
4. ✓ Subtotal should be sum of both items

**Checkout:**
1. Click "Proceed to Checkout"
2. ✓ Order should show all items (product + course)
3. ✓ Total should be correct

**Payment:**
1. Use test card: 4242 4242 4242 4242
2. Any future date, any CVC
3. ✓ Should see "Processing..." then success

**Confirmation:**
1. ✓ Should show order confirmation page
2. ✓ Order number should be displayed
3. ✓ All items should be listed

## Implementation Summary

### Backend Changes
- **New Model:** OrderItem (tracks items in an order)
- **Updated Model:** CartItem (now supports digital products)
- **Updated Endpoint:** POST /checkout (creates OrderItems)
- **New Endpoint:** POST /cart/add-digital-product

### Frontend Changes
- Digital products page uses `/cart/add-digital-product` instead of `/purchase`
- Cart flow displays both courses and products
- Checkout shows all items

### Database
- CartItem.product_id: NEW field for digital products
- OrderItem table: NEW for order item tracking

## Known Working
✅ Add courses to cart
✅ Checkout courses
✅ Payment processing (Stripe + Coins)
✅ Order confirmation

## Just Fixed
✅ Add digital products to cart
✅ Mixed cart display
✅ Checkout with multiple items
✅ Order item tracking

## Ready to Test
⏳ Complete end-to-end test (digital product → cart → checkout → payment)

## Troubleshooting

**Issue:** Digital product not adding to cart
- Check: Browser console for errors
- Check: Backend is running on 8001
- Check: Request goes to `/cart/add-digital-product`

**Issue:** Checkout shows empty cart
- Verify: Item count in cart icon
- Refresh: The cart page
- Check: No JavaScript errors

**Issue:** Payment fails
- Use test card: 4242 4242 4242 4242
- Check: Sufficient coin balance (if using coins)
- Check: Network errors in browser

**Issue:** Order doesn't save
- Check: Backend response status
- Check: Database connection
- Check: Order creation logs
