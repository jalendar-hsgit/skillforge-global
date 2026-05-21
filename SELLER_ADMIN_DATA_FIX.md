# SELLER & ADMIN DATA DISPLAY - FIX GUIDE

## 🎯 Problem Summary

1. **Seller pages not fetching demo data** → Products, sales, analytics not showing
2. **Admin pages missing complete features** → No proper design flow or theme
3. **No demo data visible** → Need proper API integration

---

## 🔧 PART 1: FIX SELLER DATA DISPLAY

### Current Status
```
/marketplace/seller/products     ❌ No products showing
/marketplace/seller/analytics    ❌ No sales data
/marketplace/seller/earnings     ❌ No earnings showing
/marketplace/seller/payouts      ❌ No payout history
```

### Solution: Update API Integration

#### Step 1: Verify Backend Seeding
```bash
cd backend
python seed_all_demo_data.py
```

#### Step 2: Check Database for Seller Data
```bash
cd backend
python -c "
import sqlite3
conn = sqlite3.connect('app/data/skillforge.db')
cursor = conn.cursor()
# Check products
cursor.execute('SELECT id, name, seller_id, price, status FROM digital_products')
print('Products:', cursor.fetchall())
# Check seller accounts
cursor.execute('SELECT id, user_id, is_verified FROM seller_accounts')
print('Sellers:', cursor.fetchall())
conn.close()
"
```

#### Step 3: API Endpoints to Fetch Data

**For Seller Dashboard - Get Products**
```javascript
// File: src/lib/api.ts or src/services/sellerService.ts

export async function getSellerProducts(token: string) {
  const response = await fetch('/api/v1x/seller/products', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Returns:
// {
//   "products": [
//     {
//       "id": 1,
//       "name": "Python Course",
//       "price": 19.99,
//       "status": "PUBLISHED",
//       "sales_count": 5,
//       "rating": 4.5
//     },
//     ...
//   ]
// }
```

**For Seller Analytics - Get Sales Data**
```javascript
export async function getSellerSales(token: string, period: string = 'month') {
  const response = await fetch(`/api/v1x/seller/analytics/sales?period=${period}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Returns:
// {
//   "total_sales": 45000,
//   "total_orders": 150,
//   "average_order_value": 300,
//   "by_date": [
//     { "date": "2026-01-27", "sales": 5000, "orders": 15 },
//     ...
//   ]
// }
```

**For Seller Earnings - Get Revenue Data**
```javascript
export async function getSellerEarnings(token: string) {
  const response = await fetch('/api/v1x/seller/analytics/earnings', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Returns:
// {
//   "total_earned": 13500,      // 70% of $19,286 sales
//   "pending_payout": 5000,      // Amount waiting to be approved
//   "paid_out": 8500,            // Amount already paid
//   "by_product": [
//     {
//       "product_id": 1,
//       "product_name": "Python Course",
//       "earnings": 13500
//     },
//     ...
//   ]
// }
```

**For Seller Payouts - Get Payout History**
```javascript
export async function getSellerPayouts(token: string) {
  const response = await fetch('/api/v1x/seller/payouts', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Returns:
// {
//   "payouts": [
//     {
//       "id": 1,
//       "amount": 5000,
//       "status": "COMPLETED",
//       "requested_date": "2026-01-20",
//       "processed_date": "2026-01-25"
//     },
//     {
//       "id": 2,
//       "amount": 3500,
//       "status": "PENDING",
//       "requested_date": "2026-01-27"
//     }
//   ]
// }
```

#### Step 4: Update React Components

**File: src/pages/marketplace/seller/products.tsx**
```typescript
import { useEffect, useState } from 'react';

export default function SellerProducts() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1x/seller/products', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error('Failed to fetch products');
      
      const data = await response.json();
      setProducts(data.products || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading products...</div>;
  if (error) return <div className="alert alert-danger">{error}</div>;
  if (!products.length) return <div>No products yet</div>;

  return (
    <div className="seller-products">
      <h2>My Products</h2>
      <div className="products-grid">
        {products.map(product => (
          <div key={product.id} className="product-card">
            <h3>{product.name}</h3>
            <p>Price: ${product.price}</p>
            <p>Status: <span className={`badge badge-${product.status.toLowerCase()}`}>
              {product.status}
            </span></p>
            <p>Sales: {product.sales_count}</p>
            <p>Rating: {product.rating}/5</p>
            <button onClick={() => editProduct(product.id)}>Edit</button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

**File: src/pages/marketplace/seller/analytics.tsx**
```typescript
import { useEffect, useState } from 'react';

export default function SellerAnalytics() {
  const [sales, setSales] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSalesData();
  }, []);

  const fetchSalesData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/v1x/seller/analytics/sales?period=month', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      setSales(data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading analytics...</div>;
  if (!sales) return <div>No data available</div>;

  return (
    <div className="seller-analytics">
      <h2>Sales Analytics</h2>
      <div className="metrics-row">
        <div className="metric-card">
          <h3>Total Sales</h3>
          <p className="amount">${sales.total_sales.toFixed(2)}</p>
        </div>
        <div className="metric-card">
          <h3>Total Orders</h3>
          <p className="amount">{sales.total_orders}</p>
        </div>
        <div className="metric-card">
          <h3>Average Order Value</h3>
          <p className="amount">${sales.average_order_value.toFixed(2)}</p>
        </div>
      </div>
      
      <div className="chart-section">
        <h3>Sales by Date</h3>
        {/* Use Chart.js or Recharts */}
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Sales</th>
              <th>Orders</th>
            </tr>
          </thead>
          <tbody>
            {sales.by_date.map((entry, idx) => (
              <tr key={idx}>
                <td>{entry.date}</td>
                <td>${entry.sales.toFixed(2)}</td>
                <td>{entry.orders}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## 🔧 PART 2: FIX ADMIN DATA DISPLAY

### Admin Pages Need

```
/admin                       ❌ Dashboard with metrics
/admin/marketplace           ❌ Product approval with list
/admin/payouts               ❌ Payout management with list
/admin/users                 ❌ User management with search
/admin/analytics             ❌ Platform analytics with charts
```

### Admin Dashboard Design

**File: src/pages/admin/index.tsx or src/pages/admin/dashboard.tsx**
```typescript
import { useEffect, useState } from 'react';

export default function AdminDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [pending, setPending] = useState({
    products: 0,
    sellers: 0,
    payouts: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Fetch metrics
      const metricsRes = await fetch('/api/v1x/admin/analytics/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);

      // Fetch pending items
      const productsRes = await fetch('/api/v1x/admin/products?status=pending', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const productsData = await productsRes.json();
      
      const payoutsRes = await fetch('/api/v1x/admin/payouts?status=pending', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const payoutsData = await payoutsRes.json();

      setPending({
        products: productsData.total || 0,
        sellers: 0, // From metricsData if available
        payouts: payoutsData.total || 0
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="admin-dashboard">
      <header className="dashboard-header">
        <h1>Admin Dashboard</h1>
        <p>Platform Overview & Metrics</p>
      </header>

      {/* Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card metric-primary">
          <h3>Total Revenue</h3>
          <p className="amount">${metrics.total_revenue.toFixed(2)}</p>
          <p className="sub">Platform fees (30%)</p>
        </div>
        
        <div className="metric-card metric-success">
          <h3>Total Users</h3>
          <p className="amount">{metrics.total_users}</p>
          <p className="sub">Active this month</p>
        </div>

        <div className="metric-card metric-info">
          <h3>Total Products</h3>
          <p className="amount">{metrics.total_products}</p>
          <p className="sub">Published products</p>
        </div>

        <div className="metric-card metric-warning">
          <h3>Pending Approvals</h3>
          <p className="amount">{pending.products}</p>
          <p className="sub">Products awaiting review</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Quick Actions</h2>
        <div className="action-buttons">
          <a href="/admin/marketplace" className="btn btn-primary">
            Approve Products ({pending.products})
          </a>
          <a href="/admin/payouts" className="btn btn-warning">
            Process Payouts ({pending.payouts})
          </a>
          <a href="/admin/users" className="btn btn-info">
            Manage Users
          </a>
          <a href="/admin/analytics" className="btn btn-secondary">
            View Analytics
          </a>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="recent-section">
        <h2>Recent Activities</h2>
        {/* Activity feed */}
      </div>

      {/* Charts */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Revenue Trend</h3>
          {/* Revenue chart */}
        </div>
        <div className="chart-container">
          <h3>User Growth</h3>
          {/* User growth chart */}
        </div>
        <div className="chart-container">
          <h3>Top Products</h3>
          {/* Top products chart */}
        </div>
      </div>
    </div>
  );
}
```

### Admin Product Approval Page

**File: src/pages/admin/marketplace.tsx**
```typescript
import { useEffect, useState } from 'react';

export default function AdminMarketplace() {
  const [products, setProducts] = useState([]);
  const [filter, setFilter] = useState('pending');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, [filter]);

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = filter === 'all' 
        ? '/api/v1x/admin/products'
        : `/api/v1x/admin/products?status=${filter}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setProducts(data.products || []);
    } finally {
      setLoading(false);
    }
  };

  const approveProduct = async (productId: string) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`/api/v1x/admin/products/${productId}/approve`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchProducts(); // Refresh list
    } catch (error) {
      console.error('Error approving product:', error);
    }
  };

  const rejectProduct = async (productId: string) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`/api/v1x/admin/products/${productId}/reject`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchProducts(); // Refresh list
    } catch (error) {
      console.error('Error rejecting product:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="admin-marketplace">
      <header>
        <h1>Marketplace Management</h1>
        <div className="filter-tabs">
          <button 
            className={filter === 'pending' ? 'active' : ''}
            onClick={() => setFilter('pending')}
          >
            Pending ({products.filter(p => p.status === 'PENDING').length})
          </button>
          <button 
            className={filter === 'approved' ? 'active' : ''}
            onClick={() => setFilter('approved')}
          >
            Approved
          </button>
          <button 
            className={filter === 'rejected' ? 'active' : ''}
            onClick={() => setFilter('rejected')}
          >
            Rejected
          </button>
          <button 
            className={filter === 'all' ? 'active' : ''}
            onClick={() => setFilter('all')}
          >
            All
          </button>
        </div>
      </header>

      <div className="products-table">
        <table>
          <thead>
            <tr>
              <th>Product Name</th>
              <th>Seller</th>
              <th>Price</th>
              <th>Status</th>
              <th>Submitted</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map(product => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.seller_name}</td>
                <td>${product.price}</td>
                <td>
                  <span className={`badge badge-${product.status.toLowerCase()}`}>
                    {product.status}
                  </span>
                </td>
                <td>{new Date(product.created_at).toLocaleDateString()}</td>
                <td>
                  {product.status === 'PENDING' && (
                    <>
                      <button 
                        className="btn btn-sm btn-success"
                        onClick={() => approveProduct(product.id)}
                      >
                        Approve
                      </button>
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => rejectProduct(product.id)}
                      >
                        Reject
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

### Admin Payouts Page

**File: src/pages/admin/payouts.tsx**
```typescript
import { useEffect, useState } from 'react';

export default function AdminPayouts() {
  const [payouts, setPayouts] = useState([]);
  const [filter, setFilter] = useState('pending');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPayouts();
  }, [filter]);

  const fetchPayouts = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = filter === 'all'
        ? '/api/v1x/admin/payouts'
        : `/api/v1x/admin/payouts?status=${filter}`;
      
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setPayouts(data.payouts || []);
    } finally {
      setLoading(false);
    }
  };

  const approvePayout = async (payoutId: string) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`/api/v1x/admin/payouts/${payoutId}/approve`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchPayouts();
    } catch (error) {
      console.error('Error approving payout:', error);
    }
  };

  const processPayout = async (payoutId: string) => {
    try {
      const token = localStorage.getItem('token');
      await fetch(`/api/v1x/admin/payouts/${payoutId}/process`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchPayouts();
    } catch (error) {
      console.error('Error processing payout:', error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="admin-payouts">
      <header>
        <h1>Payout Management</h1>
        <div className="stats">
          <div className="stat">
            <span>Total Pending:</span>
            <strong>${payouts
              .filter(p => p.status === 'PENDING')
              .reduce((sum, p) => sum + p.amount, 0)
              .toFixed(2)}</strong>
          </div>
        </div>
      </header>

      <div className="filter-tabs">
        <button 
          className={filter === 'pending' ? 'active' : ''}
          onClick={() => setFilter('pending')}
        >
          Pending
        </button>
        <button 
          className={filter === 'approved' ? 'active' : ''}
          onClick={() => setFilter('approved')}
        >
          Approved
        </button>
        <button 
          className={filter === 'processed' ? 'active' : ''}
          onClick={() => setFilter('processed')}
        >
          Processed
        </button>
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
      </div>

      <div className="payouts-table">
        <table>
          <thead>
            <tr>
              <th>Seller</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Requested</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payouts.map(payout => (
              <tr key={payout.id}>
                <td>{payout.seller_name}</td>
                <td>${payout.amount.toFixed(2)}</td>
                <td>
                  <span className={`badge badge-${payout.status.toLowerCase()}`}>
                    {payout.status}
                  </span>
                </td>
                <td>{new Date(payout.requested_date).toLocaleDateString()}</td>
                <td>
                  {payout.status === 'PENDING' && (
                    <button 
                      className="btn btn-sm btn-success"
                      onClick={() => approvePayout(payout.id)}
                    >
                      Approve
                    </button>
                  )}
                  {payout.status === 'APPROVED' && (
                    <button 
                      className="btn btn-sm btn-primary"
                      onClick={() => processPayout(payout.id)}
                    >
                      Process to Stripe
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

---

## 🎨 PART 3: THEME & STYLING

### CSS Structure

**File: src/styles/theme.css**
```css
:root {
  /* Colors */
  --primary: #007BFF;
  --success: #28A745;
  --warning: #FFC107;
  --danger: #DC3545;
  --info: #17A2B8;
  --light: #F8F9FA;
  --dark: #212529;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --font-size-base: 1rem;
  --font-size-large: 1.25rem;
  --font-size-small: 0.875rem;
}

/* Navbar */
.navbar {
  background-color: var(--dark);
  color: white;
  padding: var(--spacing-md);
  position: sticky;
  top: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Sidebar */
.sidebar {
  width: 250px;
  background-color: var(--light);
  border-right: 1px solid #ddd;
  position: fixed;
  left: 0;
  top: 60px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

/* Main Content */
.main-content {
  margin-left: 250px;
  padding: var(--spacing-lg);
}

/* Cards */
.card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: var(--spacing-lg);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* Badge Status */
.badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 4px;
  font-size: var(--font-size-small);
  font-weight: bold;
}

.badge-pending {
  background-color: var(--warning);
  color: white;
}

.badge-approved {
  background-color: var(--success);
  color: white;
}

.badge-rejected {
  background-color: var(--danger);
  color: white;
}

.badge-published {
  background-color: var(--success);
  color: white;
}

/* Buttons */
.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: var(--font-size-base);
  text-decoration: none;
  display: inline-block;
}

.btn-primary { background-color: var(--primary); color: white; }
.btn-success { background-color: var(--success); color: white; }
.btn-warning { background-color: var(--warning); color: white; }
.btn-danger { background-color: var(--danger); color: white; }
.btn-info { background-color: var(--info); color: white; }

.btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: var(--spacing-lg);
}

th {
  background-color: var(--light);
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: 2px solid #ddd;
}

td {
  padding: var(--spacing-md);
  border-bottom: 1px solid #ddd;
}

tr:hover {
  background-color: var(--light);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.metric-card {
  background: white;
  border-left: 4px solid var(--primary);
  padding: var(--spacing-lg);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.metric-card h3 {
  margin: 0 0 var(--spacing-md) 0;
  color: #666;
  font-size: var(--font-size-small);
  text-transform: uppercase;
}

.metric-card .amount {
  font-size: 2rem;
  font-weight: bold;
  color: var(--dark);
  margin: 0;
}

.metric-primary { border-left-color: var(--primary); }
.metric-success { border-left-color: var(--success); }
.metric-warning { border-left-color: var(--warning); }
.metric-danger { border-left-color: var(--danger); }
.metric-info { border-left-color: var(--info); }

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -250px;
    transition: left 0.3s;
  }

  .sidebar.open {
    left: 0;
  }

  .main-content {
    margin-left: 0;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## ✅ COMPLETE CHECKLIST

- [ ] Database seeded with demo data
- [ ] Seller products API endpoint working
- [ ] Seller analytics API endpoint working
- [ ] Admin dashboard API endpoint working
- [ ] Admin product approval API working
- [ ] Admin payout API working
- [ ] Seller products component renders data
- [ ] Seller analytics shows sales charts
- [ ] Admin dashboard shows metrics
- [ ] Admin marketplace page shows products
- [ ] Admin payouts page shows requests
- [ ] All styling applied (colors, badges, buttons)
- [ ] Responsive design working
- [ ] All URLs accessible without 404 errors

---

## 🚀 DEPLOYMENT STEPS

1. **Seed data**: `python backend/seed_all_demo_data.py`
2. **Start backend**: `cd backend && python -m uvicorn app.main:app --reload`
3. **Start frontend**: `npm run dev`
4. **Test URLs**: Follow checklist above
5. **Fix any 404s**: Check API endpoint implementations
6. **Verify data display**: Check browser console for errors

---

**Status**: Ready to implement ✅
