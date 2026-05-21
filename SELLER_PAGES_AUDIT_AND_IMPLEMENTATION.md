# Seller Pages Status & Implementation Guide
**Date**: January 29, 2026  
**Purpose**: Audit and Complete Seller Dashboard Features

---

## 📊 SELLER PAGES INVENTORY

### Pages Overview
```
src/pages/marketplace/seller/
├── index.tsx                  - Seller Dashboard (Status: ?)
├── account.tsx               - Account Settings (Status: ?)
├── analytics.tsx             - Sales Analytics (Status: ?)
├── create-product.tsx        - Create Product Form (Status: ?)
├── orders.tsx                - Seller Orders (Status: ?)
└── products.tsx              - Manage Products (Status: ?)
```

---

## 🔍 DETAILED FILE ANALYSIS

### File 1: seller/index.tsx (Dashboard)
**Purpose**: Main seller dashboard showing key metrics

**Should Display**:
- Total sales
- Revenue this month
- Total products
- Orders pending
- Quick action buttons

**Status**: ❓ UNKNOWN - Need to check
**Todo**: Read and verify functionality

---

### File 2: seller/account.tsx (Settings)
**Purpose**: Seller account and payout settings

**Should Contain**:
- Account info (name, email, bio)
- Bank details for payout
- Tax info
- Account status
- Verification status

**Status**: ❓ UNKNOWN
**Todo**: Read and verify

---

### File 3: seller/analytics.tsx (Analytics)
**Purpose**: Sales charts and statistics

**Should Show**:
- Revenue chart (monthly/daily)
- Sales by product
- Conversion rate
- Top products
- Customer insights

**Status**: ❓ UNKNOWN
**Todo**: Read and verify

---

### File 4: seller/create-product.tsx (Create Form)
**Purpose**: Form to create new digital product

**Form Fields**:
- Product name
- Description
- Category
- Product type (template, guide, etc.)
- Price
- File upload
- Thumbnail
- Tags

**Status**: ❓ UNKNOWN
**Todo**: Read and verify backend integration

---

### File 5: seller/orders.tsx (Orders)
**Purpose**: View orders for seller's products

**Should Display**:
- Customer name
- Product purchased
- Amount earned
- Order date
- Order status
- Download tracking

**Status**: ❓ UNKNOWN
**Todo**: Read and verify

---

### File 6: seller/products.tsx (Product List)
**Purpose**: Manage seller's products

**Features**:
- List all products
- Edit product
- Delete product
- View sales count
- Change status (draft/published/archived)
- View analytics per product

**Status**: ❓ UNKNOWN
**Todo**: Read and verify

---

## 🔌 REQUIRED BACKEND ENDPOINTS FOR SELLERS

### Authentication
```
POST /api/v1/auth/login - Login to seller account
Must return seller with seller_id or seller_account_id
```

### Product Management
```
GET  /api/v1x/marketplace/seller/products
GET  /api/v1x/marketplace/seller/products/{id}
POST /api/v1x/marketplace/seller/products
PUT  /api/v1x/marketplace/seller/products/{id}
DELETE /api/v1x/marketplace/seller/products/{id}
```

### Analytics
```
GET /api/v1x/marketplace/seller/analytics
GET /api/v1x/marketplace/seller/analytics/revenue
GET /api/v1x/marketplace/seller/analytics/products
GET /api/v1x/marketplace/seller/analytics/customers
```

### Orders & Sales
```
GET /api/v1x/marketplace/seller/orders
GET /api/v1x/marketplace/seller/orders/{id}
GET /api/v1x/marketplace/seller/sales
```

### Account & Payouts
```
GET  /api/v1x/marketplace/seller/account
PUT  /api/v1x/marketplace/seller/account
POST /api/v1x/marketplace/seller/payout-method
GET  /api/v1x/marketplace/seller/earnings
POST /api/v1x/marketplace/seller/withdraw
GET  /api/v1x/marketplace/seller/transactions
```

---

## 🧪 SELLER DASHBOARD TEST FLOW

### Login as Seller
```
1. Go to http://localhost:3000/login
2. Use mentor/seller account:
   Email: mentor_name@example.com (from seed data)
   OR create seller account via backend
3. After login, go to /marketplace/seller
4. Should see dashboard
```

### Demo Seller Accounts (From Seed Data)
Check `backend/seed_all_demo_data.py` for accounts like:
- Sarah Chen (mentor → can be seller)
- David Kumar (mentor → can be seller)
- Emily Rodriguez (mentor → can be seller)
- James Patterson (mentor → can be seller)

Each would have credentials from seed script.

---

## 📋 SELLER PAGES CHECKLIST

### Dashboard (index.tsx)
- [ ] Page loads without errors
- [ ] Shows seller's total sales
- [ ] Shows current month revenue
- [ ] Shows total products count
- [ ] Shows pending orders count
- [ ] Has "Create Product" button
- [ ] Has navigation to other seller pages
- [ ] Dark theme applied

### Account (account.tsx)
- [ ] Loads seller account info
- [ ] Can edit name/bio
- [ ] Shows bank details form (if any)
- [ ] Shows verification status
- [ ] Has "Save" button
- [ ] Shows success message on save
- [ ] Dark theme applied

### Analytics (analytics.tsx)
- [ ] Revenue chart loads
- [ ] Products chart loads
- [ ] Shows date range filter
- [ ] Shows sales statistics
- [ ] Shows product breakdown
- [ ] Responsive on mobile
- [ ] Dark theme applied

### Create Product (create-product.tsx)
- [ ] Form loads
- [ ] All fields present (name, desc, category, price, file)
- [ ] File upload works
- [ ] Form validation works
- [ ] Success message on create
- [ ] Redirects to products list
- [ ] Dark theme applied

### Orders (orders.tsx)
- [ ] Loads seller's orders
- [ ] Shows customer names
- [ ] Shows products purchased
- [ ] Shows amount earned
- [ ] Shows order dates
- [ ] Can filter by status
- [ ] Dark theme applied

### Products (products.tsx)
- [ ] Loads seller's products
- [ ] Shows product name, price, sales
- [ ] Edit button works
- [ ] Delete button works
- [ ] Status toggle works (draft/published)
- [ ] Pagination if many products
- [ ] Dark theme applied

---

## 🎨 DARK THEME APPLICATION FOR SELLER PAGES

Each page should follow pattern:
```tsx
import Layout from '@/components/Layout';

export default function SellerPage() {
  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="container">
          {/* Page content here */}
        </div>
      </div>
    </Layout>
  );
}
```

### Component Styling
```tsx
// Cards
className="bg-deepTech-700 border border-techGray-700 rounded-lg p-6"

// Buttons
className="bg-forgePurple hover:bg-forgePurple-600 text-white"

// Text
className="text-techGray-300" // Regular text
className="text-techGray-500" // Muted text
className="text-white" // Headings

// Inputs
className="bg-deepTech border border-techGray-600 text-techGray-300"

// Charts
// If using chart library, make sure background is transparent
// and text is light colored
```

---

## 🚀 IMPLEMENTATION CHECKLIST

### Phase 1: Verify Current State (TODAY)
- [ ] Read all 6 seller page files
- [ ] Check what components are present
- [ ] Check if they have data fetching
- [ ] List what's working vs broken
- [ ] Document all missing pieces

### Phase 2: Fix Core Functionality (THIS WEEK)
- [ ] Complete all page components
- [ ] Add API calls to each page
- [ ] Implement forms properly
- [ ] Add error handling
- [ ] Add loading states
- [ ] Add success messages

### Phase 3: Style All Pages (THIS WEEK)
- [ ] Apply dark theme to all pages
- [ ] Check contrast and readability
- [ ] Make buttons consistent
- [ ] Style forms properly
- [ ] Test on mobile

### Phase 4: Test Complete Flow (NEXT WEEK)
- [ ] Login as seller
- [ ] Navigate dashboard
- [ ] Create a product
- [ ] View analytics
- [ ] Check earnings
- [ ] Complete a sale flow

### Phase 5: Polish & Deploy (NEXT WEEK)
- [ ] Fix any remaining bugs
- [ ] Optimize performance
- [ ] Security review
- [ ] Final testing
- [ ] Deploy to production

---

## 🔑 KEY INTEGRATION POINTS

### User Must Be Seller
Check before accessing seller pages:
```tsx
// In seller/index.tsx
const { user } = useMe();

if (!user || !user.is_seller) {
  router.push('/marketplace'); // Redirect non-sellers
}
```

### Seller ID Required
All seller endpoints need:
```tsx
const response = await fetch(
  `/api/v1x/marketplace/seller/products`,
  { credentials: 'include' } // Session has seller_id
);
```

### Demo Seller Setup
```python
# From seed_all_demo_data.py
# Mentors become sellers automatically
# Or SellerAccount is created separately
```

---

## 📊 SELLER FEATURES BY PRIORITY

### Must Have (MVP)
1. View dashboard with basic stats
2. Create new products
3. Edit/delete products
4. View orders
5. See earnings

### Should Have (Phase 2)
1. Analytics dashboard with charts
2. Download sales reports
3. Verify account status
4. Update payout method
5. Customer messages

### Nice to Have (Phase 3)
1. Bulk upload products
2. Product templates
3. Advanced filtering
4. Export data
5. Marketing tools

---

## 🧑‍💻 NEXT STEPS

1. **Read all 6 seller files** to understand current state
2. **Document what exists** vs what's missing
3. **Identify backend endpoint gaps** that need implementation
4. **Create detailed fix list** for each file
5. **Apply dark theme** consistently
6. **Test with demo seller account**

---

## 📝 SELLER PAGE TEMPLATE

Use this template for consistency:

```tsx
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { useRouter } from 'next/router';
import { useMe } from '@/hooks/useMe';
import { API_BASE } from '@/lib/apiBase';

interface SellerData {
  // Define interface
}

export default function SellerPage() {
  const router = useRouter();
  const { user } = useMe();
  const [data, setData] = useState<SellerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Check if user is seller
  useEffect(() => {
    if (user && !user.is_seller) {
      router.push('/marketplace');
    }
  }, [user]);

  // Fetch data
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1x/marketplace/seller/endpoint`,
        { credentials: 'include' }
      );
      if (response.ok) {
        setData(await response.json());
      }
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-deepTech via-deepTech-900 to-deepTech py-12">
        <div className="container">
          {/* Content here */}
        </div>
      </div>
    </Layout>
  );
}
```

---

## 🎯 SUCCESS CRITERIA FOR SELLER DASHBOARD

When complete:
- ✅ All 6 pages load without errors
- ✅ All pages use dark theme consistently
- ✅ Seller can see their data
- ✅ Seller can create products
- ✅ Seller can edit/delete products
- ✅ Seller can view orders/sales
- ✅ Seller can see analytics
- ✅ Mobile responsive
- ✅ No console errors
- ✅ Proper error handling
- ✅ Loading states show
- ✅ Success messages display

---

**Status**: Ready for detailed audit of each file
**Next**: Read all 6 seller page files and report findings
