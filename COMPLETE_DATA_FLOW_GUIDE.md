# 🔄 SKILLFORGE COMPLETE DATA FLOW & SYSTEM ARCHITECTURE

**Comprehensive guide showing how data flows through all systems**

---

## 📊 USER JOURNEY FLOWS

### FLOW 1: NEW USER SIGNUP & ONBOARDING

```
┌─────────────────────────────────────────────────────────┐
│ 1. LANDING PAGE (/index.tsx)                            │
├─────────────────────────────────────────────────────────┤
│ User clicks "Get Started"                               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. SIGNUP PAGE (/signup.tsx)                            │
├─────────────────────────────────────────────────────────┤
│ Form: email, password, name                             │
│ Client validation                                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (POST /api/v1/auth/register)
┌─────────────────────────────────────────────────────────┐
│ 3. AUTH API ENDPOINT                                    │
├─────────────────────────────────────────────────────────┤
│ backend/app/api/v1/auth.py → register()                │
│ ├─ Hash password                                        │
│ ├─ Create User in database                             │
│ ├─ Create UserProfile                                  │
│ ├─ Send verification email (async)                     │
│ └─ Return JWT token                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (Database Write)
┌─────────────────────────────────────────────────────────┐
│ 4. DATABASE TABLES CREATED                              │
├─────────────────────────────────────────────────────────┤
│ users                                                   │
│ ├─ id, email, password_hash, role                      │
│ ├─ created_at, updated_at                              │
│ └─ is_active: true                                     │
│                                                         │
│ user_profiles                                          │
│ ├─ user_id (FK)                                        │
│ ├─ bio, avatar_url, location                           │
│ └─ created_at                                          │
│                                                         │
│ coin_ledger                                            │
│ ├─ user_id (FK)                                        │
│ ├─ delta: 100 (welcome bonus)                          │
│ └─ reason: "Welcome bonus"                             │
│                                                         │
│ user_preferences                                       │
│ ├─ user_id (FK)                                        │
│ ├─ theme: "light"                                      │
│ ├─ notifications_enabled: true                         │
│ └─ language: "en"                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼ (Response with Token)
┌─────────────────────────────────────────────────────────┐
│ 5. FRONTEND STORES TOKEN                                │
├─────────────────────────────────────────────────────────┤
│ localStorage.setItem('token', jwt_token)               │
│ Set Authorization header for future requests           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. REDIRECT TO DASHBOARD                                │
├─────────────────────────────────────────────────────────┤
│ /dashboard                                              │
│ ├─ Load user profile                                   │
│ ├─ Show welcome message                                │
│ ├─ Display achievement: "First Steps"                  │
│ ├─ Show recommended courses                            │
│ └─ Display coin balance: 100                           │
└──────────────────────────────────────────────────────────┘
```

### FLOW 2: COURSE ENROLLMENT & LEARNING

```
┌──────────────────────────────────┐
│ USER AT DASHBOARD                │
└────────────┬─────────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Click "Browse Courses"  │
    └────────────┬────────────┘
                 │
                 ▼ (GET /api/v1/courses)
         ┌───────────────────────────┐
         │ Backend fetches all       │
         │ PUBLIC courses from DB    │
         └────────────┬──────────────┘
                      │
                      ▼ (Return 5 courses)
         ┌──────────────────────────────────┐
         │ /watch page displays courses     │
         │ ├─ Title, description, price     │
         │ ├─ Rating, enrollment count      │
         │ ├─ "Enroll" button               │
         │ └─ "Add to Cart" button          │
         └────────────┬─────────────────────┘
                      │
            ┌─────────┴──────────┐
            │                    │
            ▼                    ▼
       (Free)              (Paid $99.99)
       │                   │
       ├─ Click Enroll     ├─ Click Add to Cart
       │ (Instant)         │
       │                   ▼ (POST /api/v1x/marketplace/cart)
       │                   │
       │                   ├─ Add item to session cart
       │                   │
       │                   ▼ (POST /api/v1x/marketplace/checkout)
       │                   │
       │                   ├─ Create PaymentIntent with Stripe
       │                   ├─ Return client_secret
       │                   │
       │                   ▼ (/checkout page)
       │                   │
       │                   ├─ Show Stripe card form
       │                   ├─ User enters card: 4242...
       │                   │
       │                   ▼ (Stripe JavaScript confirms payment)
       │                   │
       │                   ├─ Payment successful
       │                   ├─ Webhook: payment_intent.succeeded
       │                   │
       │                   ▼ (Backend webhook handler)
       │                   │
       │                   ├─ Create Order record
       │                   ├─ Create ProductPurchase if marketplace
       │                   ├─ Mark course as enrolled
       │                   ├─ Award coins: 10
       │                   ├─ Send confirmation email
       │                   │
       │                   ▼ (Database updates)
       │                   │
       │                   ├─ orders table: new row
       │                   ├─ course_enrollments: new row
       │                   ├─ coin_ledger: +10 coins
       │                   │
       │                   ▼ (Redirect to course)
       │                   │
       ├──────────────────┘
       │
       ▼
    Enroll in course
    │
    ├─ Create enrollment record
    │  (course_enrollments table)
    │
    ├─ Add to progress tracking
    │  (video_progress table)
    │
    ├─ Award coins: 5 (free course)
    │
    ├─ Check achievement unlock
    │  (e.g., "First Enrollment")
    │
    └─ Redirect to /watch/[course_id]
       │
       ▼
    VIDEO PLAYER PAGE
    │
    ├─ GET /api/v1/courses/{id}/videos
    │
    ├─ Load all videos in course
    │
    ├─ Display video list sidebar
    │
    ├─ Show current video player
    │
    ├─ Track video progress:
    │  ├─ On video play: POST /api/v1/progress/save
    │  ├─ Update video_progress.current_time
    │  ├─ If > 80% watched: mark_complete
    │  └─ Award coins on completion
    │
    ├─ After each video:
    │  ├─ Enable "Next Video" button
    │  ├─ Check if quiz available
    │  └─ Show "Take Quiz" button
    │
    └─ At course end:
       ├─ Award coins: 100
       ├─ Unlock achievement: "Course Completed"
       ├─ Check for certificate eligibility
       ├─ Generate certificate
       └─ Add to resume
```

### FLOW 3: MENTOR SESSION BOOKING & PAYMENT

```
┌────────────────────────────────────────┐
│ USER VISITS /mentors                   │
├────────────────────────────────────────┤
│ GET /api/v1x/mentors (list all)        │
│ ├─ mentor_id                           │
│ ├─ name, bio, expertise                │
│ ├─ hourly_rate: $75                    │
│ ├─ rating: 4.8/5                       │
│ ├─ availability slots                  │
│ └─ "Book Now" button                   │
└────────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │ Click on Mentor → View Profile │
    ├──────────────────────────────┤
    │ /mentors/[mentor_id]         │
    │                              │
    │ Shows:                       │
    │ ├─ Bio & achievements        │
    │ ├─ Reviews (star rating)     │
    │ ├─ Available time slots      │
    │ └─ "Book Session" button     │
    └────────────┬─────────────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │ Click "Book Session"         │
    └────────────┬─────────────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │ /mentor-booking page         │
    ├──────────────────────────────┤
    │ Form:                        │
    │ ├─ Select date (calendar)    │
    │ ├─ Select time (from slots)  │
    │ ├─ Select duration (30/60min)│
    │ ├─ Topic description         │
    │ └─ Special requests          │
    └────────────┬─────────────────┘
                 │
                 ▼ (Submit form)
    ┌──────────────────────────────────────┐
    │ POST /api/v1x/mentors/{id}/book      │
    ├──────────────────────────────────────┤
    │ Backend validates:                   │
    │ ├─ Slot is available                 │
    │ ├─ User has coins/credits            │
    │ └─ Slot not already booked           │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Create MentorSession)
    ┌──────────────────────────────────────┐
    │ Database: mentor_sessions            │
    ├──────────────────────────────────────┤
    │ ├─ id: NEW                           │
    │ ├─ mentor_id: 1                      │
    │ ├─ student_id: 5                     │
    │ ├─ scheduled_at: 2026-02-01 10:00 UTC
    │ ├─ status: PENDING                   │
    │ ├─ price: 75.00 (1 hour)             │
    │ ├─ topic: "Python Basics"            │
    │ ├─ duration_minutes: 60              │
    │ └─ payment_status: pending           │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Return confirmation)
    ┌──────────────────────────────────────┐
    │ Frontend redirect to /mentor-bookings │
    ├──────────────────────────────────────┤
    │ Shows confirmation:                  │
    │ ├─ Session scheduled with Sarah Chen │
    │ ├─ Time: Feb 1 @ 10:00 AM            │
    │ ├─ Price: $75.00                     │
    │ ├─ Status: PENDING (awaiting mentor) │
    │ └─ "Proceed to Payment" button       │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (User clicks payment)
    ┌──────────────────────────────────────┐
    │ /mentor-bookings > Payment Modal     │
    ├──────────────────────────────────────┤
    │ POST /api/v1x/payments/payment-intent│
    │                                      │
    │ Creates Stripe PaymentIntent         │
    │ amount: 7500 (cents)                 │
    │ currency: usd                        │
    │ metadata: {mentor_session_id: X}     │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Return client_secret)
    ┌──────────────────────────────────────┐
    │ Frontend: Stripe.confirmCardPayment() │
    ├──────────────────────────────────────┤
    │ ├─ Show card form                    │
    │ ├─ User enters: 4242 4242 4242 4242  │
    │ ├─ User enters: 12/25, 123           │
    │ └─ Submit payment                    │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Stripe processes)
    ┌──────────────────────────────────────┐
    │ Stripe: payment_intent.succeeded     │
    ├──────────────────────────────────────┤
    │ Webhook to /api/v1x/payments/webhook │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Backend webhook handler)
    ┌──────────────────────────────────────┐
    │ Update MentorSession:                │
    ├──────────────────────────────────────┤
    │ ├─ payment_status: completed         │
    │ ├─ payment_intent_id: pi_xxx         │
    │ ├─ paid_at: NOW                      │
    │ ├─ transaction_id: ch_xxx            │
    │ └─ status: CONFIRMED                 │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Update mentor earnings)
    ┌──────────────────────────────────────┐
    │ mentor_earnings table:               │
    ├──────────────────────────────────────┤
    │ ├─ mentor_id: 1                      │
    │ ├─ session_id: X                     │
    │ ├─ gross: 75.00                      │
    │ ├─ platform_fee: 15.00 (20%)         │
    │ ├─ net: 60.00 (mentor gets this)     │
    │ └─ status: pending (awaiting payout) │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Send emails)
    ┌──────────────────────────────────────┐
    │ Email to Student:                    │
    │ "Session booked! Mentor will call"   │
    │                                      │
    │ Email to Mentor:                     │
    │ "New session booked! Payment: $60"   │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (Redirect)
    ┌──────────────────────────────────────┐
    │ Frontend: /student/sessions          │
    │ Shows confirmed session              │
    │ Status: CONFIRMED                    │
    │ "Meeting starts in 2 days"           │
    └──────────────────────────────────────┘
```

### FLOW 4: MARKETPLACE PRODUCT PURCHASE

```
┌──────────────────────────────────────┐
│ User browses /marketplace            │
├──────────────────────────────────────┤
│ GET /api/v1x/marketplace/products    │
│                                      │
│ Database query:                      │
│ ├─ DigitalProduct.status = PUBLISHED│
│ ├─ DigitalProduct.visibility=public │
│ └─ Order by created_at DESC         │
└────────────┬─────────────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ Products displayed:        │
    │ ├─ React Template ($29.99) │
    │ ├─ Python Guide ($14.99)   │
    │ └─ ML Interview ($39.99)   │
    └────────────┬───────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    [Add to Cart]     [View Details]
         │                │
         │                ▼
         │          ┌─────────────────────────┐
         │          │ /marketplace/products/1 │
         │          ├─────────────────────────┤
         │          │ Full product info       │
         │          │ ├─ Images              │
         │          │ ├─ Description         │
         │          │ ├─ Reviews (4.9/5)     │
         │          │ ├─ Sales count: 12     │
         │          │ └─ "Add to Cart" btn   │
         │          └────────────┬────────────┘
         │                       │
         │        ┌──────────────┘
         │        │
         └────────┼─────────────────────┐
                  │                     │
                  ▼                     │
    ┌──────────────────────────────┐   │
    │ POST /api/v1x/marketplace/   │   │
    │       cart                   │   │
    ├──────────────────────────────┤   │
    │ Backend adds item to:        │   │
    │                              │   │
    │ SESSION CART (server-side)   │   │
    │ OR                           │   │
    │ SESSION CART (client-side)   │   │
    │                              │   │
    │ Returns:                     │   │
    │ ├─ Cart items (updated)      │   │
    │ ├─ Subtotal: 29.99           │   │
    │ ├─ Tax: 2.40                 │   │
    │ └─ Total: 32.39              │   │
    └────────────┬─────────────────┘   │
                 │                     │
                 ▼                     │
    ┌──────────────────────────────┐   │
    │ Frontend cart updated:        │   │
    │ ├─ "1 item in cart"           │   │
    │ ├─ Cart icon shows badge      │   │
    │ └─ Toast: "Added to cart"     │   │
    └────────────┬─────────────────┘   │
                 │                     │
                 │◄────────────────────┘ (continue shopping)
                 │
                 ▼
    ┌──────────────────────────────┐
    │ User clicks /checkout        │
    ├──────────────────────────────┤
    │ GET /api/v1x/marketplace/cart│
    │                              │
    │ Shows:                       │
    │ ├─ Items in cart (1)         │
    │ ├─ Subtotal: 29.99           │
    │ ├─ Tax: 2.40                 │
    │ ├─ Coupon field              │
    │ ├─ "Apply Coupon" btn        │
    │ ├─ Total: 32.39              │
    │ └─ "Proceed to Payment"      │
    └────────────┬─────────────────┘
                 │
                 ▼
    ┌──────────────────────────────┐
    │ Validate coupon (optional)   │
    │ POST /api/v1x/marketplace/   │
    │       validate-coupon        │
    │                              │
    │ If "SAVE10":                 │
    │ ├─ Valid                     │
    │ ├─ Discount: 10%             │
    │ └─ New Total: 29.15          │
    └────────────┬─────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ POST /api/v1x/marketplace/       │
    │       checkout                   │
    ├──────────────────────────────────┤
    │ Request:                         │
    │ ├─ product_ids: [1]              │
    │ ├─ coupon_code: "SAVE10"         │
    │ └─ payment_method: "stripe"      │
    │                                  │
    │ Backend:                         │
    │ ├─ Validate cart items exist     │
    │ ├─ Check inventory (digital=inf) │
    │ ├─ Calculate final price: 29.15  │
    │ ├─ Create Stripe PaymentIntent   │
    │ ├─ amount: 2915 (cents)          │
    │ └─ Return {client_secret, url}   │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Frontend Payment Modal           │
    ├──────────────────────────────────┤
    │ ├─ Show Stripe card form         │
    │ ├─ Display total: $29.15         │
    │ ├─ "Pay Now" button              │
    │ └─ User confirms payment         │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Stripe.confirmCardPayment()      │
    │                                  │
    │ User enters:                     │
    │ ├─ Card: 4242 4242 4242 4242    │
    │ ├─ Exp: 12/25                    │
    │ └─ CVC: 123                      │
    │                                  │
    │ Stripe processes & returns:      │
    │ ├─ status: succeeded             │
    │ ├─ payment_intent_id: pi_xxx    │
    │ └─ charge_id: ch_xxx             │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ POST /api/v1x/payments/          │
    │     confirm-payment              │
    │                                  │
    │ Manually confirm (optional)      │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Stripe Webhook (automatic):      │
    │ payment_intent.succeeded         │
    │                                  │
    │ → /api/v1x/payments/webhook      │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Backend Webhook Handler:         │
    ├──────────────────────────────────┤
    │ 1. Verify webhook signature      │
    │ 2. Find payment_intent_id        │
    │ 3. Create Order record:          │
    │    ├─ user_id: 5                 │
    │    ├─ product_ids: [1]           │
    │    ├─ amount: 29.15              │
    │    ├─ status: "completed"        │
    │    ├─ payment_method: "stripe"   │
    │    ├─ transaction_id: ch_xxx     │
    │    └─ paid_at: NOW               │
    │                                  │
    │ 4. Create ProductPurchase:       │
    │    ├─ product_id: 1              │
    │    ├─ buyer_id: 5                │
    │    ├─ seller_id: 3 (Sarah)       │
    │    ├─ purchase_price: 29.15      │
    │    ├─ platform_fee: 5.83 (20%)   │
    │    ├─ seller_payout: 23.32 (80%)│
    │    ├─ status: "completed"        │
    │    └─ delivered_at: NOW          │
    │                                  │
    │ 5. Update DigitalProduct:        │
    │    ├─ sales_count: 13 (+1)       │
    │    ├─ total_revenue: +29.15      │
    │    └─ views_count: calculated    │
    │                                  │
    │ 6. Update SellerAccount (Sarah): │
    │    ├─ total_sales: 13 (+1)       │
    │    ├─ total_revenue: +29.15      │
    │    └─ rating: recalculated       │
    │                                  │
    │ 7. Create SellerPayout entry:    │
    │    ├─ seller_id: 3               │
    │    ├─ period_start: 2026-01-01   │
    │    ├─ total_sales: 29.15 (sum)   │
    │    ├─ platform_fee: 5.83 (deduct)│
    │    ├─ payout_amount: 23.32       │
    │    └─ status: "pending"          │
    │                                  │
    │ 8. Award buyer coins:            │
    │    ├─ coin_ledger entry: +10     │
    │    ├─ reason: "Product purchase" │
    │    └─ user coins: updated        │
    │                                  │
    │ 9. Send emails:                  │
    │    ├─ To buyer: Confirmation     │
    │    ├─ Download link              │
    │    ├─ To seller: Sale alert      │
    │    └─ Revenue notification       │
    │                                  │
    │ 10. Logging:                     │
    │    ├─ admin_log entry            │
    │    ├─ activity log               │
    │    └─ analytics update           │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Frontend redirects:              │
    │ /checkout → /orders/[order_id]   │
    ├──────────────────────────────────┤
    │ Shows:                           │
    │ ├─ Order confirmation           │
    │ ├─ "Download" button            │
    │ ├─ "Leave Review" button        │
    │ └─ "Continue Shopping"          │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ User clicks "Download"           │
    ├──────────────────────────────────┤
    │ GET /api/v1x/marketplace/        │
    │     orders/[id]/download         │
    │                                  │
    │ Backend:                         │
    │ ├─ Verify user owns order        │
    │ ├─ Get download_url from Product │
    │ ├─ Increment download_count      │
    │ └─ Return download URL (S3/etc)  │
    │                                  │
    │ Result:                          │
    │ ├─ File downloads (PDF, ZIP)     │
    │ └─ download_count: 1 (+1)        │
    └────────────┬──────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Dashboard Analytics Updated:     │
    │                                  │
    │ MarketplaceAnalytics:            │
    │ ├─ total_sales: +1               │
    │ ├─ total_revenue: +29.15         │
    │ ├─ unique_buyers: +1             │
    │ └─ growth_rate: recalculated     │
    │                                  │
    │ Admin dashboard shows:           │
    │ ├─ New order: +$29.15            │
    │ ├─ Platform commission: +$5.83   │
    │ ├─ Seller payout pending: +$23.32
    │ └─ Charts update in real-time    │
    └──────────────────────────────────┘
```

---

## 🏗️ SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (FRONTEND)                      │
├─────────────────────────────────────────────────────────────────────┤
│                         Next.js React App                           │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │  Pages      │  │ Components  │  │   Hooks     │  │ Context  │ │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤  ├──────────┤ │
│  │ /dashboard  │  │ VideoPlayer │  │ useAuth     │  │ UserCtx  │ │
│  │ /marketplace│  │ CartWidget  │  │ useFetch    │  │ ThemeCtx │ │
│  │ /mentors    │  │ PaymentForm │  │ useNotif    │  │ CartCtx  │ │
│  │ /admin      │  │ Leaderboard │  │ useCoins    │  │ etc      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │            lib/api.ts - HTTP Client (Axios)                  │ │
│  │  - Base URL: http://localhost:8001                           │ │
│  │  - Auto-attach JWT token                                    │ │
│  │  - Global error handling                                    │ │
│  │  - Request/response interceptors                            │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │     Third-party SDKs: Stripe, GitHub, LinkedIn OAuth        │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS / WebSocket
                         │
┌────────────────────────┴─────────────────────────────────────────┐
│                    REVERSE PROXY / LB                             │
│                    (Optional: nginx)                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────────┐      ┌─────────────────────────┐
│  BACKEND API         │      │   STATIC FILES / CDN    │
│  (FastAPI)           │      │   - Images              │
│  :8001               │      │   - Videos (S3)         │
└──────────────┬───────┘      │   - CSS/JS bundles      │
               │              │   - Downloaded files    │
               │              └─────────────────────────┘
       ┌───────┴──────────────────┬──────────┐
       │                          │          │
       ▼                          ▼          ▼
    ┌────────────────┐  ┌──────────────┐  ┌────────────┐
    │  API Routers   │  │   Services   │  │ Middleware │
    ├────────────────┤  ├──────────────┤  ├────────────┤
    │ /api/v1/*      │  │ Auth Service │  │ Security   │
    │ /api/v1x/*     │  │ Email Svc    │  │ CORS       │
    │ /api/session   │  │ Stripe Svc   │  │ Logging    │
    │ /api/admin/*   │  │ Payment Proc │  │ Error Hnd  │
    │ /ws/*          │  │ Scheduler    │  │ Validators │
    │ /collab/*      │  │ Storage Svc  │  │ Auth Guard │
    └─────┬──────────┘  └──────────────┘  └────────────┘
          │
          ▼
    ┌────────────────────────────────────────┐
    │      CORE APPLICATION LAYER            │
    ├────────────────────────────────────────┤
    │                                        │
    │  ┌──────────────────────────────────┐ │
    │  │  Database Models (60+)           │ │
    │  │  ├─ User, Course, Mentor, etc   │ │
    │  │  ├─ Payment, Order, Marketplace │ │
    │  │  ├─ Badges, Achievements        │ │
    │  │  └─ All relationships defined   │ │
    │  └──────────────────────────────────┘ │
    │                                        │
    │  ┌──────────────────────────────────┐ │
    │  │  Business Logic Layers           │ │
    │  │  ├─ Auth & Permissions           │ │
    │  │  ├─ Payment Processing           │ │
    │  │  ├─ Mentor Booking Logic         │ │
    │  │  ├─ Marketplace Commission Calc  │ │
    │  │  ├─ Gamification Rules           │ │
    │  │  └─ Analytics Computation        │ │
    │  └──────────────────────────────────┘ │
    │                                        │
    └────────────┬─────────────────────────┘
                 │
        ┌────────┼────────┬──────────┐
        │        │        │          │
        ▼        ▼        ▼          ▼
    ┌──────┐ ┌──────┐ ┌──────┐  ┌──────────┐
    │ DB   │ │Cache │ │Queue │  │ Services │
    │SQLite│ │Redis │ │Celery│  │ External │
    │      │ │(opt) │ │(opt) │  │          │
    └──────┘ └──────┘ └──────┘  ├──────────┤
        │                       │Stripe API│
        │                       │Zoom API  │
        │                       │AWS S3    │
        │                       │SendGrid  │
        │                       │GitHub    │
        │                       │LinkedIn  │
        │                       └──────────┘
        │
        ▼
    ┌────────────────────────────────┐
    │   DATABASE LAYER               │
    ├────────────────────────────────┤
    │  SQLite (Development)          │
    │  PostgreSQL (Production Ready) │
    │                                │
    │  Tables:                       │
    │  ├─ users (auth)               │
    │  ├─ courses & videos           │
    │  ├─ mentors & sessions         │
    │  ├─ marketplace & orders       │
    │  ├─ coins & badges             │
    │  ├─ resumes & applications     │
    │  ├─ forums & discussions       │
    │  ├─ activity & notifications   │
    │  ├─ payments & payouts         │
    │  └─ 40+ more tables            │
    └────────────────────────────────┘
```

---

## 🔐 DATA SECURITY FLOW

```
┌─────────────────────────────────────────────────┐
│ INCOMING REQUEST                                │
└────────────┬────────────────────────────────────┘
             │
             ▼
    ┌─────────────────────────────────────┐
    │ 1. HTTPS TLS/SSL Encryption         │
    │    All data encrypted in transit    │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 2. CORS Validation                  │
    │    Verify origin allowed            │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 3. Request Parsing                  │
    │    JSON/FormData extraction         │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 4. Input Validation                 │
    │    Pydantic models validate types   │
    │    XSS/SQL injection prevention     │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 5. Authentication                   │
    │    Extract JWT from Authorization   │
    │    Verify signature & expiration    │
    │    Get current user                 │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 6. Authorization                    │
    │    Check user role & permissions    │
    │    Rate limiting applied            │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 7. Business Logic Execution         │
    │    Data operations                  │
    │    Payment processing (PCI-DSS)     │
    │    Sensitive data: encrypted        │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 8. Database Operations              │
    │    ORM prevents SQL injection       │
    │    Parameterized queries            │
    │    Row-level security               │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 9. Response Serialization           │
    │    Sensitive fields excluded        │
    │    JSON serialization               │
    └────────────┬────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────┐
    │ 10. Response Transmission           │
    │     HTTPS encryption                │
    │     Security headers added          │
    │     Content-Security-Policy         │
    └──────────────────────────────────────┘
```

---

## 💳 PAYMENT PROCESSING FLOW

```
┌──────────────────────────────────────┐
│ PAYMENT INITIATION                   │
└────────────┬─────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────────┐
    │ 1. Create PaymentIntent              │
    ├──────────────────────────────────────┤
    │ POST /api/v1x/payments/payment-intent│
    │                                      │
    │ Amount: 2915 (cents = $29.15)       │
    │ Currency: USD                        │
    │ Payment Method Types: [card]         │
    │ Metadata: {order_id, user_id}        │
    │ Confirm Method: automatic            │
    │ Return URL: http://localhost:3000    │
    │ Cancel URL: http://localhost:3000    │
    └────────────┬──────────────────────────┘
                 │
                 ▼ (via Stripe.js SDK)
    ┌──────────────────────────────────────┐
    │ 2. Stripe API Response               │
    ├──────────────────────────────────────┤
    │ {                                    │
    │   "client_secret": "pi_xxx_secret",│
    │   "intent_id": "pi_xxx",            │
    │   "status": "requires_payment_method"│
    │ }                                    │
    └────────────┬──────────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────────┐
    │ 3. Frontend: Show Payment Form       │
    ├──────────────────────────────────────┤
    │ <StripeCardElement />                │
    │                                      │
    │ User enters:                         │
    │ - Card number                        │
    │ - Expiration date                    │
    │ - CVC                                │
    │ - Billing zip code                   │
    └────────────┬──────────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────────┐
    │ 4. Stripe.confirmCardPayment()       │
    ├──────────────────────────────────────┤
    │ Sends encrypted card data to Stripe  │
    │ (NOT to your server - PCI compliance)│
    │                                      │
    │ Stripe validates:                    │
    │ ├─ Card is valid                     │
    │ ├─ CVV matches                       │
    │ ├─ Expiration not passed             │
    │ ├─ AVS address verification          │
    │ └─ 3D Secure (if needed)             │
    └────────────┬──────────────────────────┘
                 │
    ┌────────────┴──────────────┐
    │                           │
    ▼ (Success)            ▼ (Failure)
 ┌──────────────┐      ┌────────────────┐
 │ Payment OK   │      │ Payment Failed │
 │ client_secret│      │ Error message  │
 │ + token      │      │ displayed      │
 └──────┬───────┘      └────────────────┘
        │
        ▼
    ┌──────────────────────────────────┐
    │ 5. Auto-confirm Payment          │
    │    (Stripe automatically)         │
    │                                  │
    │    Stripe charges card:           │
    │    - Processes $29.15            │
    │    - Generates charge_id         │
    │    - Charge fee: ~$0.87          │
    │    - Net to account: $28.28      │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ 6. Stripe Webhook Sent           │
    │    (Asynchronously)              │
    │                                  │
    │    Event: payment_intent.succeeded
    │    ├─ Payment Intent ID          │
    │    ├─ Charge ID                  │
    │    ├─ Amount received            │
    │    ├─ Status: succeeded          │
    │    └─ Timestamp                  │
    │                                  │
    │    → /api/v1x/payments/webhook  │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ 7. Backend Webhook Handler       │
    ├──────────────────────────────────┤
    │ 1. Verify webhook signature      │
    │    (Using Stripe secret)         │
    │                                  │
    │ 2. Retrieve full payment intent  │
    │    via Stripe API                │
    │                                  │
    │ 3. Extract metadata:             │
    │    ├─ order_id                   │
    │    ├─ user_id                    │
    │    └─ product_id                 │
    │                                  │
    │ 4. Database transaction BEGIN    │
    │                                  │
    │ 5. Create order record           │
    │ 6. Create purchase record        │
    │ 7. Update product stats          │
    │ 8. Update seller account         │
    │ 9. Create seller payout entry    │
    │ 10. Award buyer coins            │
    │ 11. Update analytics             │
    │                                  │
    │ 12. Database transaction COMMIT  │
    │     (all-or-nothing)             │
    │                                  │
    │ 13. Send confirmation emails     │
    │ 14. Update user profile (coins)  │
    │ 15. Log transaction              │
    │ 16. Return HTTP 200 OK           │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ 8. Frontend Receives Status       │
    ├──────────────────────────────────┤
    │ Either:                          │
    │ ├─ Payment succeeded (return URL)│
    │ ├─ Webhook processed (polling)   │
    │ └─ User sees confirmation        │
    │                                  │
    │ Redirect to:                     │
    │ /orders/[order_id]               │
    │                                  │
    │ Display:                         │
    │ ├─ Order confirmation            │
    │ ├─ Download links                │
    │ ├─ Invoice                       │
    │ └─ "Leave Review" button         │
    └──────────────────────────────────┘

PAYMENT STATES:
├─ requires_payment_method (initial)
├─ requires_confirmation (card added)
├─ processing (being charged)
├─ requires_action (3D Secure, etc)
├─ succeeded (✅ payment complete)
└─ canceled (❌ payment failed)
```

---

## 📧 EMAIL & NOTIFICATION FLOW

```
TRIGGER EVENT
├─ User registers
├─ Course enrollment
├─ Mentor session booked
├─ Product purchased
├─ Mentor session completed
├─ Achievement unlocked
├─ Review posted
└─ Admin action
│
▼ (Async Task)
┌──────────────────────┐
│ Event Handler        │
├──────────────────────┤
│ Identify event type  │
│ Gather template data │
│ Queue notification   │
└────────────┬─────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Notification Queue      │
    │ (Redis/Celery/DB)       │
    │ ├─ User ID              │
    │ ├─ Email address        │
    │ ├─ Template name        │
    │ ├─ Template data        │
    │ ├─ Notification type    │
    │ └─ Scheduled time       │
    └────────────┬────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Email Service (SendGrid)         │
    ├──────────────────────────────────┤
    │ 1. Load template HTML/text       │
    │ 2. Replace variables:            │
    │    {user_name}, {product_name}   │
    │ 3. Add tracking pixel/links       │
    │ 4. Build MIME multipart (text)   │
    │ 5. Verify sender domain          │
    │ 6. Add DKIM/SPF signatures       │
    │ 7. Submit to SendGrid API        │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ Email Delivered                  │
    │                                  │
    │ To: user@example.com             │
    │ From: noreply@skillforge.com     │
    │ Subject: "Your course is ready!" │
    │                                  │
    │ Body:                            │
    │ "Hi John,                        │
    │  Your course enrollment is       │
    │  complete. [Start Learning]"     │
    │                                  │
    │ Footer:                          │
    │ ├─ Unsubscribe link              │
    │ ├─ Tracking pixel                │
    │ └─ "View in browser" link        │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ In-App Notification (DB)         │
    │                                  │
    │ notifications table:             │
    │ ├─ id: 1                         │
    │ ├─ user_id: 5                    │
    │ ├─ type: "order.confirmed"       │
    │ ├─ title: "Order confirmed"      │
    │ ├─ message: "Your order is ready"│
    │ ├─ is_read: false                │
    │ ├─ action_url: "/orders/123"     │
    │ └─ created_at: NOW               │
    │                                  │
    │ Frontend shows:                  │
    │ ├─ Bell icon with badge (1)      │
    │ ├─ Dropdown notification list    │
    │ ├─ Click to mark as read         │
    │ └─ Click to navigate to order    │
    └────────────┬─────────────────────┘
                 │
                 ▼
    ┌──────────────────────────────────┐
    │ WebSocket Notification (Realtime)│
    │                                  │
    │ WebSocket: /ws/notifications     │
    │                                  │
    │ Server sends:                    │
    │ {                                │
    │   "type": "notification_new",    │
    │   "data": {                      │
    │     "id": 1,                     │
    │     "title": "Order confirmed",  │
    │     "created_at": "2026-01-25"   │
    │   }                              │
    │ }                                │
    │                                  │
    │ Frontend:                        │
    │ ├─ Bell notification appears     │
    │ ├─ Sound alert (optional)        │
    │ ├─ Toast popup                   │
    │ └─ Realtime UI update            │
    └──────────────────────────────────┘

NOTIFICATION PREFERENCES:
├─ Email preferences (opt-in/out)
├─ In-app toggle
├─ WebSocket enabled
├─ Push notifications (PWA)
├─ Digest emails (daily/weekly)
└─ Do-not-disturb hours
```

---

## 🔄 REAL-TIME DATA SYNC FLOW

```
CLIENT (Browser)
    │
    ├─ WebSocket Connection
    │  WebSocket: /ws/notifications
    │
    └─ Polling (Fallback)
       GET /api/v1/notifications
       Interval: 10s


SERVER (FastAPI)
    │
    ├─ WebSocket Handler
    │  └─ /api/websocket/notifications
    │     ├─ Accept connection
    │     ├─ Send initial state
    │     ├─ Subscribe to events
    │     └─ Broadcast updates
    │
    ├─ Event System
    │  ├─ MentorSessionConfirmed
    │  ├─ PaymentReceived
    │  ├─ AchievementUnlocked
    │  ├─ ReviewPosted
    │  ├─ MentorAvailable
    │  └─ Custom events
    │
    └─ Cache Layer (Redis)
       ├─ Active user sessions
       ├─ Online mentors
       ├─ Leaderboard cache
       └─ Recent activities


DATA FLOW:

1. User takes quiz
   │
   ▼ POST /api/v1/quizzes/[id]/submit
   │
   ├─ Calculate score
   ├─ Update user progress
   ├─ Check achievement unlock
   ├─ Award coins
   │
   ▼ Emit Event: "quiz.completed"
   │
   ├─ Update leaderboard cache
   ├─ Broadcast to WebSocket subscribers
   │
   ▼ Clients receive:
   └─ Leaderboard updated in real-time
      Achievement notification appears
      Coins updated in header
```

---

This document shows complete data flow through all systems! 🎯
