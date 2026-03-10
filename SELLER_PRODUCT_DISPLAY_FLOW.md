# SELLER PRODUCT DISPLAY FLOW - COMPLETE GUIDE

## Overview

This document explains the **complete end-to-end flow** of how seller courses/products are created, stored, approved, and displayed to buyers in the SkillForge Global marketplace.

---

## THE COMPLETE JOURNEY

```
SELLER                    BACKEND                   DATABASE              CUSTOMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Seller visits
   /marketplace/seller/
   create-product
                │
                ├──> Form renders
                │    (name, price, files)
                │
2. Seller fills                │
   form + uploads              ├──> Collects data:
   files (thumbnail,           │    • name, description
   content, preview)           │    • price, category
                               │    • product_type
                               │    • files
                │
3. Clicks "Create"             │
                ├──────────────────>  POST /api/v1x/marketplace/
                │                       seller/products
                │
                │                   DigitalProduct created:
                │                   • seller_id = current_user
                │                   • status = DRAFT
                │                   • price, name, etc.
                │                   <─────────────┤ Stored in
                │                                │ digital_products
                │                                │ table
                │ Returns: {id, status:DRAFT}
                │
4. Uploads files                │
   (thumbnail, content,         ├──────────────────>  POST /api/v1x/marketplace/
   preview)                      │                       seller/products/{id}/
                │               │                       upload-thumbnail
                │               │                       (and other files)
                │               │
                │               ├──> File stored, URL
                │               │    saved in DigitalProduct
                │               └──> thumbnail_url updated
                │                    <─────────────┤
                │
5. (OPTIONAL: Admin │          ├──────────────────>  GET /api/v1x/marketplace/
   Approval)        │            │                    admin/marketplace/products
   Admin sees       │            │
   DRAFT products   │            ├──> Shows all products
   and approves     │            │    (all statuses)
                │            │
                │   Admin clicks           ├──> PUT /api/v1x/marketplace/
                │   "Approve"              │     admin/products/{id}/approve
                │                │         │
                │                ├──────────────> Updates status:
                │                │         │     DRAFT → PUBLISHED
                │                │         │
                │                │         └──> digital_products.status
                │                │              = PUBLISHED
                │                │              <──────────┤
                │
6. SELLER'S PRODUCTS NOW VISIBLE TO CUSTOMERS:

   Customer visits              ├──> GET /api/v1x/marketplace/
   /marketplace                 │    digital-products
                                │
                                ├──> Query filters:
                                │    WHERE status = PUBLISHED
                                │    ONLY shows PUBLISHED
                                │    <─────────────┤
                                │
   Customer sees              └──> Frontend renders
   product list               │    product cards
   with thumbnail,            │    (name, price,
   price, ratings             │     thumbnail,
                                    ratings)
                │
7. Customer clicks             │
   "Buy"                        ├──────────────────> POST /api/v1x/marketplace/
                │              │                     digital-products/{id}/
                │              │                     purchase
                │              │
                │              ├──> Creates ProductPurchase
                │              │
                │              └──> Updates:
                │                   • product.sales_count += 1
                │                   • product.total_revenue += price
                │                   <─────────────┤
                │
8. Seller sees                 │
   order in:                    ├──> GET /api/v1x/marketplace/
   /marketplace/seller/         │    seller/orders
   orders                       │
                                └──> Shows all orders
                                     for products
                                     <─────────────┤
```

---

## DETAILED BREAKDOWN

### PHASE 1: SELLER CREATES PRODUCT

#### Frontend: Seller Product Creation Form
**File**: [src/pages/marketplace/seller/create-product.tsx](src/pages/marketplace/seller/create-product.tsx#L1-L100)

```typescript
// Seller fills this form:
interface ProductFormData {
  name: string;              // "Python Guide"
  description: string;       // "Complete Python learning"
  product_type: string;      // "course", "template", "bundle", etc.
  category: string;          // "programming", "design", etc.
  price: number;             // 49.99
  original_price?: number;   // 99.99 (before discount)
  tags: string[];            // ["python", "beginner"]
  requirements: string[];    // ["Basic computer knowledge"]
  features: string[];        // ["50 videos", "Lifetime access"]
  status: string;            // "draft"
  visibility: string;        // "public"
}

// Seller clicks "Create Product" → calls:
POST /api/v1x/marketplace/seller/products
Content-Type: application/json

{
  "name": "Python Guide",
  "description": "Complete Python learning...",
  "product_type": "course",
  "category": "programming",
  "price": 49.99,
  "tags": ["python", "beginner"],
  "requirements": ["Basic knowledge"],
  "features": ["50 videos", "Access forever"]
}
```

#### Backend: Product Creation Endpoint
**File**: [backend/app/api/v1x/marketplace.py](backend/app/api/v1x/marketplace.py#L1080-L1130)

```python
@router.post("/seller/products")
def create_product(
    product_data: DigitalProductCreate,  # ✅ Validates all fields
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new digital product"""
    
    # Step 1: Check seller account exists
    seller_account = db.query(SellerAccount).filter_by(user_id=current_user.id).first()
    if not seller_account:
        raise HTTPException(status_code=404, detail="Please create a seller account first")
    
    # Step 2: Generate unique slug
    name = product_data.name
    slug = name.lower().replace(" ", "-") + "-" + secrets.token_hex(3)
    
    # Step 3: Create DigitalProduct in database
    product = DigitalProduct(
        seller_id=current_user.id,           # ✅ Link to seller
        name=name,
        slug=slug,
        description=product_data.description,
        product_type=product_data.product_type,
        category=product_data.category,
        price=float(product_data.price),
        original_price=float(product_data.original_price) if product_data.original_price else None,
        tags=product_data.tags if product_data.tags else [],
        requirements=product_data.requirements if product_data.requirements else [],
        features=product_data.features if product_data.features else [],
        status=ProductStatus.DRAFT,          # ✅ Status starts as DRAFT
        visibility="public"
    )
    
    # Step 4: Save to database
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Step 5: Return created product info
    return {
        "id": product.id,                    # ← Frontend gets this ID
        "name": product.name,
        "slug": product.slug,
        "status": "draft",                   # ← NOT visible to customers yet
        "price": product.price,
        "created_at": product.created_at
    }
```

#### Database: Digital Product Created
**Table**: `digital_products`

```sql
-- New row created:
INSERT INTO digital_products (
    id,
    seller_id,
    name,
    slug,
    description,
    product_type,
    category,
    price,
    original_price,
    tags,
    requirements,
    features,
    status,              -- ← "DRAFT"
    visibility,
    thumbnail_url,       -- ← NULL initially
    content_url,         -- ← NULL initially
    preview_url,         -- ← NULL initially
    sales_count,
    average_rating,
    created_at,
    updated_at
) VALUES (
    123,                 -- product.id
    456,                 -- seller_id (current_user.id)
    'Python Guide',
    'python-guide-a1b2c3',
    'Complete Python learning',
    'course',
    'programming',
    49.99,
    99.99,
    '["python","beginner"]',
    '["Basic knowledge"]',
    '["50 videos","Lifetime access"]',
    'DRAFT',             -- ← Status: NOT visible to customers
    'public',
    NULL,                -- ← Will be filled when seller uploads
    NULL,
    NULL,
    0,                   -- ← No sales yet
    0.0,
    NOW(),
    NOW()
);
```

---

### PHASE 2: SELLER UPLOADS FILES

#### Frontend: File Upload
**File**: [src/pages/marketplace/seller/create-product.tsx](src/pages/marketplace/seller/create-product.tsx#L168-L220)

```typescript
const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    fileType: 'thumbnail' | 'content' | 'preview'
) => {
    if (!e.target.files || !e.target.files[0]) return;

    const file = e.target.files[0];
    setUploading(true);

    try {
        // Create FormData for file upload
        const formDataUpload = new FormData();
        formDataUpload.append('file', file);
        
        // Upload thumbnail
        const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/seller/products/${productId}/upload-${fileType}`,
            {
                method: 'POST',
                credentials: 'include',
                body: formDataUpload
            }
        );

        if (res.ok) {
            const result = await res.json();
            // Update UI with uploaded file URL
            setUploadedFiles(prev => ({
                ...prev,
                [fileType]: result.url
            }));
        }
    } finally {
        setUploading(false);
    }
};
```

#### Backend: File Upload Endpoints
**File**: [backend/app/api/v1x/marketplace.py](backend/app/api/v1x/marketplace.py#L1567-L1690)

```python
@router.post("/seller/products/{product_id}/upload-thumbnail")
def upload_product_thumbnail(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product thumbnail"""
    
    # Verify seller owns product
    product = db.query(DigitalProduct).filter(
        and_(
            DigitalProduct.id == product_id,
            DigitalProduct.seller_id == current_user.id
        )
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Save file to server
    filename = f"products/thumbnails/{product_id}_{file.filename}"
    file_path = f"./uploads/{filename}"
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Update product with thumbnail URL
    product.thumbnail_url = f"/uploads/{filename}"  # ← Saved to DB
    db.commit()
    db.refresh(product)
    
    return {"url": product.thumbnail_url}


@router.post("/seller/products/{product_id}/upload-content")
def upload_product_content(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product content file"""
    # Similar to thumbnail...
    product.content_url = f"/uploads/{filename}"
    db.commit()
    return {"url": product.content_url}


@router.post("/seller/products/{product_id}/upload-preview")
def upload_product_preview(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload product preview file"""
    # Similar to thumbnail...
    product.preview_url = f"/uploads/{filename}"
    db.commit()
    return {"url": product.preview_url}
```

#### Database Updated
```sql
UPDATE digital_products
SET 
    thumbnail_url = '/uploads/products/thumbnails/123_python-logo.png',
    content_url = '/uploads/products/content/123_python-guide.pdf',
    preview_url = '/uploads/products/preview/123_preview.pdf'
WHERE id = 123;
```

---

### PHASE 3: ADMIN APPROVES PRODUCT (Optional but Recommended)

#### Admin Approval Endpoint
**File**: [backend/app/api/v1x/marketplace.py](backend/app/api/v1x/marketplace.py) (Admin routes)

```python
@router.get("/admin/marketplace/products")
def admin_list_products(
    status: Optional[str] = None,  # Can filter: "draft", "pending", "published"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin views all products (all statuses) for approval"""
    
    # Check user is admin
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all products (including DRAFT, PENDING_APPROVAL, etc.)
    query = db.query(DigitalProduct)
    
    if status:
        query = query.filter_by(status=status)
    
    products = query.all()
    
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "seller_id": p.seller_id,
                "price": p.price,
                "status": p.status,
                "created_at": p.created_at,
                "description": p.description[:200]
            }
            for p in products
        ]
    }


@router.put("/admin/marketplace/products/{product_id}/approve")
def admin_approve_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin approves product - changes status to PUBLISHED"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update status
    product.status = ProductStatus.PUBLISHED    # ✅ NOW visible to customers!
    product.approved_at = datetime.utcnow()
    product.approved_by = current_user.id
    
    db.commit()
    db.refresh(product)
    
    return {
        "id": product.id,
        "status": "published",
        "approved_at": product.approved_at,
        "message": "Product approved and now visible to customers"
    }
```

#### Database Update - Product Becomes Public
```sql
UPDATE digital_products
SET 
    status = 'PUBLISHED',           -- ✅ NOW PUBLISHED
    approved_at = NOW(),
    approved_by = 2                 -- Admin user ID
WHERE id = 123;
```

---

### PHASE 4: CUSTOMERS SEE PRODUCTS IN MARKETPLACE

#### Frontend: Customer Views Marketplace
**File**: [src/pages/marketplace/index.tsx](src/pages/marketplace/index.tsx)

```typescript
export default function Marketplace() {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                // ✅ Fetches ONLY PUBLISHED products
                const res = await fetch(
                    `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/digital-products?page=1&per_page=20`,
                    { credentials: 'include' }
                );

                if (res.ok) {
                    const data = await res.json();
                    setProducts(data.products);  // ← Only PUBLISHED items
                }
            } catch (err) {
                console.error('Failed to load products:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchProducts();
    }, []);

    return (
        <Layout>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {products.map(product => (
                    <div key={product.id} className="product-card">
                        <img 
                            src={product.thumbnail_url} 
                            alt={product.name}
                            className="w-full h-48 object-cover rounded"
                        />
                        <h3 className="text-lg font-bold mt-2">{product.name}</h3>
                        <p className="text-gray-600">{product.description}</p>
                        <div className="flex justify-between items-center mt-4">
                            <span className="text-2xl font-bold">${product.price}</span>
                            <button 
                                onClick={() => buyProduct(product.id)}
                                className="bg-blue-600 text-white px-4 py-2 rounded"
                            >
                                Buy Now
                            </button>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                            <span className="text-yellow-500">★ {product.average_rating}</span>
                            <span className="text-gray-500">({product.sales_count} sales)</span>
                        </div>
                    </div>
                ))}
            </div>
        </Layout>
    );
}
```

#### Backend: Get Published Products Only
**File**: [backend/app/api/v1x/marketplace.py](backend/app/api/v1x/marketplace.py#L684-L760)

```python
@router.get("/digital-products", response_model=ProductListingResponse)
def list_digital_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    product_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "popularity",
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db)
):
    """List and search digital products with filters"""
    
    # ✅ KEY FILTER: Only published products shown to customers
    query = db.query(DigitalProduct).filter(
        DigitalProduct.status == ProductStatus.PUBLISHED    # ← CRITICAL!
    )
    
    # Search
    if search:
        query = query.filter(
            or_(
                DigitalProduct.name.ilike(f"%{search}%"),
                DigitalProduct.description.ilike(f"%{search}%")
            )
        )
    
    # Category filter
    if category:
        query = query.filter_by(category=category)
    
    # Type filter
    if product_type:
        query = query.filter_by(product_type=product_type)
    
    # Price range
    if min_price is not None:
        query = query.filter(DigitalProduct.price >= min_price)
    if max_price is not None:
        query = query.filter(DigitalProduct.price <= max_price)
    
    # Sorting options
    if sort_by == "newest":
        query = query.order_by(desc(DigitalProduct.created_at))
    elif sort_by == "price_low":
        query = query.order_by(DigitalProduct.price)
    elif sort_by == "price_high":
        query = query.order_by(desc(DigitalProduct.price))
    elif sort_by == "rating":
        query = query.order_by(desc(DigitalProduct.average_rating))
    else:  # popularity (default)
        query = query.order_by(desc(DigitalProduct.sales_count))
    
    # Pagination
    total = query.count()
    products = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return ProductListingResponse(
        products=[DigitalProductResponse.from_orm(p) for p in products],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )
```

#### Database Query
```sql
-- What the backend actually runs:
SELECT id, name, description, price, thumbnail_url, 
       average_rating, sales_count, category, product_type
FROM digital_products
WHERE status = 'PUBLISHED'          -- ✅ ONLY published!
ORDER BY sales_count DESC           -- Sort by popularity
LIMIT 20;

-- DRAFT products are NOT returned:
-- WHERE status IN ('PUBLISHED') filters out DRAFT
```

---

### PHASE 5: CUSTOMER PURCHASES PRODUCT

#### Customer Clicks "Buy"
```typescript
// Frontend calls:
async function buyProduct(productId: number) {
    const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/digital-products/${productId}/purchase`,
        {
            method: 'POST',
            credentials: 'include'
        }
    );

    if (res.ok) {
        const purchase = await res.json();
        alert(`Purchase successful! Order ID: ${purchase.id}`);
    }
}
```

#### Backend: Process Purchase
**File**: [backend/app/api/v1x/marketplace.py](backend/app/api/v1x/marketplace.py#L762-L810)

```python
@router.post("/digital-products/{product_id}/purchase")
def purchase_digital_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Purchase a digital product"""
    
    # Get product
    product = db.query(DigitalProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check not already owned
    existing = db.query(ProductPurchase).filter(
        and_(
            ProductPurchase.product_id == product_id,
            ProductPurchase.buyer_id == current_user.id,
            ProductPurchase.status == "completed"
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already purchased")
    
    # Create purchase record
    db_purchase = ProductPurchase(
        product_id=product_id,
        buyer_id=current_user.id,
        seller_id=product.seller_id,           # ← Links to seller
        purchase_price=product.price,
        currency=product.currency,
        payment_method="coins",
        status="completed",
        delivered_at=datetime.utcnow(),
        platform_fee=product.price * 0.30,     # Platform takes 30%
        seller_payout=product.price * 0.70     # Seller gets 70%
    )
    
    # Update product stats
    product.sales_count += 1                   # ← Increment sales
    product.total_revenue += product.price     # ← Update revenue
    
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return {
        "id": db_purchase.id,
        "product_id": db_purchase.product_id,
        "status": "completed",
        "purchase_price": db_purchase.purchase_price,
        "seller_payout": db_purchase.seller_payout,
        "platform_fee": db_purchase.platform_fee
    }
```

#### Database Update - New Purchase
```sql
-- New purchase record created:
INSERT INTO product_purchases (
    product_id,
    buyer_id,
    seller_id,
    purchase_price,
    currency,
    payment_method,
    status,
    delivered_at,
    platform_fee,
    seller_payout,
    created_at
) VALUES (
    123,           -- product.id
    789,           -- current_user.id (buyer)
    456,           -- product.seller_id
    49.99,
    'USD',
    'coins',
    'completed',
    NOW(),
    14.997,        -- 30% of 49.99
    34.993,        -- 70% of 49.99
    NOW()
);

-- Product stats updated:
UPDATE digital_products
SET 
    sales_count = 1,                    -- Was 0
    total_revenue = 49.99               -- Was 0
WHERE id = 123;
```

---

### PHASE 6: SELLER SEES ORDERS

#### Frontend: Seller Orders Page
**File**: [src/pages/marketplace/seller/orders.tsx](src/pages/marketplace/seller/orders.tsx)

```typescript
export default function SellerOrders() {
    const [orders, setOrders] = useState([]);

    useEffect(() => {
        const fetchOrders = async () => {
            const res = await fetch(
                `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/seller/orders`,
                { credentials: 'include' }
            );

            if (res.ok) {
                const data = await res.json();
                setOrders(data.orders);  // ← All customer purchases
            }
        };

        fetchOrders();
    }, []);

    return (
        <Layout>
            <table className="w-full">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Buyer</th>
                        <th>Amount</th>
                        <th>Your Payout (70%)</th>
                        <th>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {orders.map(order => (
                        <tr key={order.id}>
                            <td>{order.product_name}</td>
                            <td>{order.buyer_name}</td>
                            <td>${order.purchase_price}</td>
                            <td>${order.seller_payout}</td>
                            <td>{new Date(order.created_at).toLocaleDateString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </Layout>
    );
}
```

#### Backend: Get Seller Orders
```python
@router.get("/seller/orders")
def get_seller_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for seller's products"""
    
    # Get all purchases where seller_id = current_user
    orders = db.query(ProductPurchase).filter(
        ProductPurchase.seller_id == current_user.id
    ).all()
    
    result = []
    for order in orders:
        product = db.query(DigitalProduct).filter_by(id=order.product_id).first()
        buyer = db.query(User).filter_by(id=order.buyer_id).first()
        
        result.append({
            "id": order.id,
            "product_id": order.product_id,
            "product_name": product.name,
            "buyer_id": order.buyer_id,
            "buyer_name": buyer.name,
            "purchase_price": order.purchase_price,
            "seller_payout": order.seller_payout,
            "platform_fee": order.platform_fee,
            "status": order.status,
            "created_at": order.created_at
        })
    
    return {"orders": result}
```

---

## PRODUCT STATUS LIFECYCLE

### Status States

| Status | Visibility | Description | Seller Can | Admin Can |
|--------|-----------|-------------|-----------|----------|
| **DRAFT** | ❌ Hidden | Initial state after creation | Edit, Upload files, Publish | View, Approve |
| **PENDING_APPROVAL** | ❌ Hidden | Awaiting admin review | - | Approve, Reject |
| **PUBLISHED** | ✅ Visible | Available for purchase | Edit, Archive, View sales | Edit, Suspend |
| **ARCHIVED** | ❌ Hidden | Seller archived (removed from sale) | Unarchive | View |
| **SUSPENDED** | ❌ Hidden | Admin suspended (violates policy) | Appeal | Review |

### Status Transitions

```
CREATE
  ↓
DRAFT ──→ (Seller submits for approval)
  ↓
PENDING_APPROVAL ──→ (Admin approves)
  ↓
PUBLISHED ←─────── (Seller publishes directly)
  ↓
(Available for customers to see)
```

---

## KEY DATABASE TABLES

### 1. digital_products (Store Product Info)
```sql
CREATE TABLE digital_products (
    id INTEGER PRIMARY KEY,
    seller_id INTEGER NOT NULL,              -- Links to seller (User)
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    description TEXT,
    product_type VARCHAR(50),                -- "course", "template", etc.
    category VARCHAR(50),
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),
    thumbnail_url VARCHAR(500),
    content_url VARCHAR(500),
    preview_url VARCHAR(500),
    tags TEXT,                               -- JSON array
    requirements TEXT,                       -- JSON array
    features TEXT,                           -- JSON array
    status VARCHAR(50),                      -- DRAFT, PUBLISHED, etc.
    visibility VARCHAR(50),                  -- "public", "private"
    sales_count INTEGER DEFAULT 0,           -- Updates on purchase
    average_rating DECIMAL(3, 2),
    total_revenue DECIMAL(10, 2),
    views_count INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME,
    approved_at DATETIME,                    -- When admin approved
    approved_by INTEGER,                     -- Admin who approved
    
    FOREIGN KEY (seller_id) REFERENCES users(id)
);
```

### 2. product_purchases (Track Sales)
```sql
CREATE TABLE product_purchases (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,             -- Links to product
    buyer_id INTEGER NOT NULL,               -- Links to buyer (User)
    seller_id INTEGER NOT NULL,              -- Copy of seller for reporting
    purchase_price DECIMAL(10, 2),
    currency VARCHAR(3),
    payment_method VARCHAR(50),
    status VARCHAR(50),                      -- "completed", "refunded"
    delivered_at DATETIME,
    platform_fee DECIMAL(10, 2),             -- 30% platform take
    seller_payout DECIMAL(10, 2),            -- 70% seller gets
    created_at DATETIME,
    
    FOREIGN KEY (product_id) REFERENCES digital_products(id),
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (seller_id) REFERENCES users(id)
);
```

### 3. seller_accounts (Seller Profiles)
```sql
CREATE TABLE seller_accounts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    bank_details TEXT,
    tax_id VARCHAR(50),
    paypal_email VARCHAR(255),
    total_earnings DECIMAL(15, 2),
    total_payouts DECIMAL(15, 2),
    created_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API ENDPOINT REFERENCE

### For Sellers
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1x/marketplace/seller/products` | Create new product |
| GET | `/api/v1x/marketplace/seller/products` | List seller's products |
| GET | `/api/v1x/marketplace/seller/products/{id}` | Get product details |
| PUT | `/api/v1x/marketplace/seller/products/{id}` | Edit product |
| DELETE | `/api/v1x/marketplace/seller/products/{id}` | Delete product |
| POST | `/api/v1x/marketplace/seller/products/{id}/upload-thumbnail` | Upload thumbnail |
| POST | `/api/v1x/marketplace/seller/products/{id}/upload-content` | Upload content file |
| POST | `/api/v1x/marketplace/seller/products/{id}/upload-preview` | Upload preview |
| GET | `/api/v1x/marketplace/seller/orders` | View customer orders |

### For Customers
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1x/marketplace/digital-products` | Browse all published products |
| GET | `/api/v1x/marketplace/digital-products/{id}` | Get product details |
| POST | `/api/v1x/marketplace/digital-products/{id}/purchase` | Buy product |
| GET | `/api/v1x/marketplace/digital-products/{id}/check-purchase` | Verify ownership |
| POST | `/api/v1x/marketplace/digital-products/{id}/reviews` | Write review |

### For Admins
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1x/marketplace/admin/marketplace/products` | View all products |
| PUT | `/api/v1x/marketplace/admin/products/{id}/approve` | Approve product |
| PUT | `/api/v1x/marketplace/admin/products/{id}/suspend` | Suspend product |

---

## REAL-WORLD EXAMPLE: COMPLETE FLOW

### Sarah's Python Course Journey

```
1. CREATION (Sarah - Seller)
   ────────────────────────────
   Sarah goes to: /marketplace/seller/create-product
   
   Form:
   - Name: "Python for Data Science"
   - Price: $79.99
   - Category: Programming
   - Type: Course
   
   Clicks "Create" → Backend creates DigitalProduct
   Status: DRAFT (not visible to customers yet)
   
   Database:
   digital_products.id = 1
   digital_products.seller_id = 5 (Sarah's user ID)
   digital_products.status = 'DRAFT'

2. FILE UPLOAD (Sarah)
   ────────────────────────────
   Sarah uploads:
   - thumbnail: python-data-science.jpg
   - content: python-course-videos.zip
   - preview: preview-lesson.pdf
   
   Backend updates:
   digital_products.thumbnail_url = '/uploads/products/1/python-data-science.jpg'
   digital_products.content_url = '/uploads/products/1/python-course-videos.zip'
   digital_products.preview_url = '/uploads/products/1/preview-lesson.pdf'

3. ADMIN APPROVAL (Admin - Optional)
   ────────────────────────────
   Admin visits: /admin/marketplace
   
   Sees Sarah's product in DRAFT status
   Reviews content, clicks "Approve"
   
   Backend updates:
   digital_products.status = 'PUBLISHED'
   digital_products.approved_at = NOW()
   digital_products.approved_by = 2 (admin ID)

4. CUSTOMER BROWSES (John - Customer)
   ────────────────────────────
   John visits: /marketplace
   
   Frontend calls:
   GET /api/v1x/marketplace/digital-products
   
   Backend returns only PUBLISHED products (Sarah's course included)
   
   John sees:
   - Thumbnail: python-data-science.jpg
   - Title: "Python for Data Science"
   - Price: $79.99
   - Rating: ⭐ 4.5 (from other buyers)
   - Sales: 23 people bought

5. PURCHASE (John)
   ────────────────────────────
   John clicks "Buy Now"
   
   Frontend calls:
   POST /api/v1x/marketplace/digital-products/1/purchase
   
   Backend creates purchase record:
   - product_id = 1
   - buyer_id = 7 (John's ID)
   - seller_id = 5 (Sarah's ID)
   - purchase_price = 79.99
   - platform_fee = 23.997 (30%)
   - seller_payout = 55.993 (70%)
   
   Updates product:
   digital_products.sales_count = 24
   digital_products.total_revenue += 79.99

6. SELLER SEES ORDER (Sarah)
   ────────────────────────────
   Sarah goes to: /marketplace/seller/orders
   
   Frontend calls:
   GET /api/v1x/marketplace/seller/orders
   
   Backend returns:
   [
     {
       id: 15,
       product: "Python for Data Science",
       buyer: "John Doe",
       amount: $79.99,
       your_payout: $55.99,
       date: "2024-01-28"
     }
   ]
   
   Sarah sees her earnings!
```

---

## DATA FLOW SUMMARY

### From Creation to Sale

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SELLER CREATES PRODUCT                                   │
│    Frontend: create-product.tsx → Form Data                 │
│    Backend: POST /seller/products → DigitalProductCreate   │
│    Database: INSERT digital_products (status = DRAFT)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SELLER UPLOADS FILES                                     │
│    Frontend: File upload → FormData                         │
│    Backend: POST /seller/products/{id}/upload-* → Save URL │
│    Database: UPDATE digital_products (thumbnail_url, etc)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ADMIN APPROVES (OPTIONAL)                                │
│    Frontend: Admin panel                                    │
│    Backend: PUT /admin/products/{id}/approve               │
│    Database: UPDATE status = PUBLISHED                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CUSTOMER SEES PRODUCT                                    │
│    Frontend: /marketplace → fetch published products        │
│    Backend: GET /digital-products (WHERE status=PUBLISHED) │
│    Database: SELECT from digital_products (published only)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. CUSTOMER PURCHASES                                       │
│    Frontend: Click "Buy Now"                                │
│    Backend: POST /digital-products/{id}/purchase            │
│    Database: INSERT product_purchases, UPDATE sales_count   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. SELLER SEES ORDER                                        │
│    Frontend: /marketplace/seller/orders                     │
│    Backend: GET /seller/orders (WHERE seller_id=current)   │
│    Database: SELECT product_purchases for seller            │
└─────────────────────────────────────────────────────────────┘
```

---

## IMPORTANT NOTES

### ✅ Key Points for Sellers

1. **Product Starts as DRAFT** - Products are hidden until status changes
2. **Files Are Optional Initially** - Seller can create product, then upload files
3. **Admin Approval Recommended** - Products should be reviewed before going live
4. **Products Auto-Update Stats** - sales_count, total_revenue update on purchase
5. **70/30 Split** - Seller gets 70%, Platform takes 30% of each sale
6. **Unique Slug** - Each product gets unique slug for URL

### ✅ Key Points for Customers

1. **Only See Published** - Cannot see DRAFT, ARCHIVED, or SUSPENDED products
2. **Search & Filter** - Can search by name, filter by category, price, etc.
3. **See Seller Info** - Can see which user is selling
4. **Purchase Creates Record** - Gets ownership record in database
5. **Can't Buy Twice** - System prevents duplicate purchases
6. **Can Write Reviews** - Buyers can rate and review products

### ✅ Key Points for Admins

1. **Full Visibility** - Can see ALL products regardless of status
2. **Approve Products** - Move status from DRAFT → PUBLISHED
3. **Suspend Products** - Hide products that violate policies
4. **View Earnings** - See sales data and payout information

---

## Testing the Flow

### Create a Product
```bash
curl -X POST "http://localhost:8001/api/v1x/marketplace/seller/products" \
  -H "Content-Type: application/json" \
  -b "session=your_session_cookie" \
  -d '{
    "name": "Python Course",
    "description": "Learn Python",
    "product_type": "course",
    "category": "programming",
    "price": 49.99,
    "tags": ["python", "beginner"],
    "requirements": ["Computer"],
    "features": ["50 videos", "Lifetime access"]
  }'
```

### View Products (Customers See Only Published)
```bash
curl "http://localhost:8001/api/v1x/marketplace/digital-products"
```

### Buy Product
```bash
curl -X POST "http://localhost:8001/api/v1x/marketplace/digital-products/1/purchase" \
  -b "session=your_session_cookie"
```

### View Seller Orders
```bash
curl "http://localhost:8001/api/v1x/marketplace/seller/orders" \
  -b "session=your_session_cookie"
```

---

## Summary

The marketplace flow is:

1. **Seller creates** → Product in DRAFT (hidden)
2. **Seller uploads** → Files attached, product ready
3. **Admin approves** → Status → PUBLISHED (visible)
4. **Customer sees** → Browse published products only
5. **Customer buys** → Purchase created, stats updated
6. **Seller earns** → 70% of sale price paid out

This ensures quality control (admin approval) while enabling sellers to easily create and manage digital products for sale.
