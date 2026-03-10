# 🔄 Complete Data Flow: Courses & Products Display in Marketplace

**Date**: January 28, 2026  
**Purpose**: Understand how courses/products are fetched and displayed to users

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│              (Next.js Frontend on port 3000)                │
└─────────────────────────────────────────────────────────────┘
                              ↕
                   HTTP Request / JSON Response
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                           │
│          (Running on port 8001)                             │
│                                                             │
│  ├─ /api/v1x/marketplace/courses                          │
│  ├─ /api/v1x/marketplace/digital-products                │
│  ├─ /api/v1x/marketplace/search                          │
│  ├─ /api/v1x/marketplace/cart                            │
│  └─ ... (30+ endpoints)                                   │
└─────────────────────────────────────────────────────────────┘
                              ↕
                         SQLAlchemy ORM
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                          │
│        (backend/app/data/skillforge.db)                     │
│                                                             │
│  ├─ courses table                                           │
│  ├─ digital_products table                                 │
│  ├─ users table                                            │
│  ├─ cart_items table                                       │
│  ├─ orders table                                           │
│  └─ ... (40+ tables)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Step-by-Step Flow: User Browses Marketplace

### STEP 1️⃣: User Visits Marketplace Home Page

**URL**: `http://localhost:3000/marketplace`  
**Frontend Page**: `src/pages/marketplace/index.tsx`

### STEP 2️⃣: Frontend Initializes & Makes API Request

**Code in `index.tsx`**:
```typescript
useEffect(() => {
  fetchCourses();  // Called on page load
}, [selectedCategory, freeOnly]);

const fetchCourses = async () => {
  setLoading(true);
  try {
    // BUILD THE URL WITH QUERY PARAMS
    let url = `/api/session/v1x/marketplace/courses?`;
    if (selectedCategory && selectedCategory !== 'All') {
      url += `category=${encodeURIComponent(selectedCategory)}&`;
    }
    if (freeOnly) {
      url += `free_only=true&`;
    }
    if (searchQuery) {
      url += `search=${encodeURIComponent(searchQuery)}&`;
    }

    // MAKE HTTP REQUEST TO BACKEND
    const response = await fetch(url, {
      credentials: 'include'  // Include session cookie
    });

    if (response.ok) {
      const data = await response.json();
      setCourses(data);  // Store in React state
    }
  } catch (error) {
    console.error('Error fetching courses:', error);
  } finally {
    setLoading(false);
  }
};
```

**What Happens**:
- Frontend creates a GET request
- Sends to: `GET /api/session/v1x/marketplace/courses?category=Web%20Development`
- Includes session cookie for user authentication
- Waits for JSON response

---

### STEP 3️⃣: Backend Receives Request

**Backend Router**: `backend/app/api/v1x/marketplace.py`

**Endpoint Receives**:
```
GET /api/session/v1x/marketplace/courses
├─ Query Parameters:
│  ├─ category: "Web Development"
│  ├─ free_only: false
│  └─ search: (optional)
└─ Headers:
   └─ Cookie: session=xxx (user authentication)
```

---

### STEP 4️⃣: Backend Database Query

**Database Operation** (in `marketplace.py`):
```python
# Query the courses table from SQLite database
courses = db.query(Course).filter(
    and_(
        Course.is_paid == (not free_only),  # Filter by paid/free
        Course.category == selectedCategory  # Filter by category
    )
).limit(20).offset(0).all()

# Get additional info (videos, ratings, purchase status)
for course in courses:
    video_count = db.query(Video).filter(
        Video.course_id == course.id
    ).count()
    
    is_purchased = db.query(Order).filter(
        and_(
            Order.user_id == current_user.id,
            Order.course_id == course.id,
            Order.status == "completed"
        )
    ).first()
```

**What Gets Retrieved**:
- Course ID
- Title & Description
- Price (if paid)
- Category
- Video count
- Whether user purchased it
- Rating & reviews

---

### STEP 5️⃣: Backend Formats Response

**Response Schema** (defined in `marketplace.py`):
```python
class CourseListItem(BaseModel):
    id: int
    path: str
    title: str
    description: Optional[str]
    category: Optional[str]
    is_paid: bool
    price: Optional[float]
    video_count: int = 0
    is_purchased: bool = False
    is_in_cart: bool = False
    rating: Optional[float] = None
```

**Actual JSON Response**:
```json
[
  {
    "id": 1,
    "path": "python-fundamentals",
    "title": "Python Fundamentals",
    "description": "Learn Python from scratch",
    "category": "Programming",
    "is_paid": true,
    "price": 49.99,
    "video_count": 12,
    "is_purchased": false,
    "is_in_cart": false,
    "rating": 4.5
  },
  {
    "id": 2,
    "path": "web-dev-101",
    "title": "Web Development 101",
    "description": "Master HTML, CSS, JavaScript",
    "category": "Web Development",
    "is_paid": true,
    "price": 99.99,
    "video_count": 25,
    "is_purchased": false,
    "is_in_cart": false,
    "rating": 4.8
  }
]
```

---

### STEP 6️⃣: Frontend Receives Response

**What happens in React**:
```typescript
// Response arrives as JSON
const data = await response.json();
// [{ id: 1, title: "Python Fundamentals", ... }, ...]

// Store in React state
setCourses(data);

// Component re-renders with new data
```

---

### STEP 7️⃣: Frontend Renders UI

**Component Renders**:
```typescript
return (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {courses.map((course) => (
      <div key={course.id} className="course-card">
        <h3>{course.title}</h3>
        <p>{course.description}</p>
        <div className="course-meta">
          <span>{course.category}</span>
          <span>{course.video_count} videos</span>
          <span className="rating">⭐ {course.rating}</span>
        </div>
        
        {course.is_paid && (
          <span className="price">${course.price}</span>
        )}
        
        {course.is_purchased ? (
          <button disabled>Already Purchased</button>
        ) : course.is_in_cart ? (
          <button onClick={() => goToCart()}>In Cart</button>
        ) : (
          <button onClick={() => addToCart(course.id)}>
            <ShoppingCart /> Add to Cart
          </button>
        )}
      </div>
    ))}
  </div>
);
```

**What User Sees**:
- Grid of course cards
- Each showing: Title, Description, Category, Video count, Rating, Price
- Action buttons (Add to Cart, Already Purchased, etc.)

---

## 📱 Visual Flow Diagram

```
USER BROWSER (Frontend)
│
├─ User visits: http://localhost:3000/marketplace
│
├─ Page loads index.tsx
│  │
│  ├─ useEffect hook runs
│  │
│  └─ fetchCourses() function called
│     │
│     ├─ Build URL: /api/session/v1x/marketplace/courses?category=...
│     │
│     └─ fetch(url, { credentials: 'include' })
│        │
│        └─ ─────────────────────────────────────────→ HTTP GET Request
│
├─────────────────────────────────────────────────────────────────────
│
BACKEND (FastAPI)
│
├─ Router receives: GET /api/session/v1x/marketplace/courses
│  │
│  ├─ Extract query params (category, free_only, search)
│  │
│  ├─ Get current user from session cookie
│  │
│  └─ Execute database queries
│     │
│     └─ SQLAlchemy ORM translates to SQL
│        │
│        └─ ─────────────────────────────────────────→ SQL Query
│
├─────────────────────────────────────────────────────────────────────
│
DATABASE (SQLite)
│
├─ Execute SQL:
│  │
│  ├─ SELECT * FROM courses WHERE category = 'Web Development'
│  │
│  ├─ SELECT COUNT(*) FROM videos WHERE course_id = {id}
│  │
│  ├─ SELECT * FROM orders WHERE user_id = {uid} AND course_id = {cid}
│  │
│  └─ SELECT AVG(rating) FROM reviews WHERE course_id = {id}
│     │
│     └─ ←─────────────────────────────────────────── Return Results

├─────────────────────────────────────────────────────────────────────
│
BACKEND (FastAPI)
│
├─ Process results
│  │
│  ├─ Format as JSON using CourseListItem schema
│  │
│  └─ Return HTTP 200 response
│     │
│     └─ ←─────────────────────────────────────────── JSON Response

├─────────────────────────────────────────────────────────────────────
│
USER BROWSER (Frontend)
│
├─ Receive JSON response
│  │
│  ├─ setCourses(data)  // Store in React state
│  │
│  ├─ setLoading(false) // Stop showing spinner
│  │
│  └─ Component re-renders
│     │
│     └─ User sees course cards displayed
│
```

---

## 🔌 Backend API Endpoints for Display

### Courses Endpoint
```
GET /api/v1x/marketplace/courses

Query Parameters:
  - category: string (optional)
  - free_only: boolean (optional)
  - search: string (optional)
  - skip: int (default: 0)
  - limit: int (default: 20)

Returns:
  [
    {
      id: number,
      path: string,
      title: string,
      description: string,
      category: string,
      is_paid: boolean,
      price: number,
      video_count: number,
      is_purchased: boolean,
      is_in_cart: boolean,
      rating: number
    }
  ]

Authentication: Optional (cookie-based)
```

### Digital Products Endpoint
```
GET /api/v1x/marketplace/digital-products

Query Parameters:
  - search: string
  - category: string
  - product_type: string (ebook, template, guide, etc.)
  - min_price: float
  - max_price: float
  - sort_by: string (popularity, newest, price_low, price_high)
  - page: int (default: 1)

Returns:
  {
    total: number,
    items: [
      {
        id: number,
        name: string,
        slug: string,
        description: string,
        product_type: string,
        price: float,
        thumbnail_url: string,
        average_rating: float,
        sales_count: number,
        status: string,
        seller: {
          id: number,
          name: string
        }
      }
    ],
    page: number,
    total_pages: number
  }

Authentication: Not required
```

---

## 🛒 Adding to Cart Flow

### STEP 1: User Clicks "Add to Cart"

**Frontend Code** (in `index.tsx`):
```typescript
const addToCart = async (courseId: number) => {
  setAddingToCart(courseId);
  
  try {
    const response = await fetch(
      `/api/session/v1x/marketplace/cart/add`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ course_id: courseId })
      }
    );
    
    if (response.ok) {
      alert('Added to cart!');
      fetchCourses();  // Refresh to show updated status
      fetchCartCount();  // Update cart count badge
    }
  } catch (error) {
    console.error('Failed to add to cart:', error);
  } finally {
    setAddingToCart(null);
  }
};
```

### STEP 2: Backend Creates Cart Item

**Backend Code** (in `marketplace.py`):
```python
@router.post("/cart/add")
def add_to_cart(
    item: CartAddRequest,  # { course_id: 1, quantity: 1 }
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the course
    course = db.query(Course).filter_by(id=item.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already in cart
    existing = db.query(CartItem).filter(
        and_(
            CartItem.user_id == current_user.id,
            CartItem.course_id == item.course_id
        )
    ).first()
    
    if existing:
        existing.quantity += item.quantity
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=current_user.id,
            course_id=item.course_id,
            price=course.price,
            quantity=item.quantity,
            added_at=datetime.utcnow()
        )
        db.add(cart_item)
    
    db.commit()
    return { "message": "Added to cart" }
```

### STEP 3: Database Updates

```sql
INSERT INTO cart_items (user_id, course_id, price, quantity, added_at)
VALUES (5, 1, 49.99, 1, 2026-01-28 10:30:00)
```

---

## 🎨 Frontend Data State Management

### State Variables in `index.tsx`:

```typescript
// What data is stored in React state
const [courses, setCourses] = useState<Course[]>([]);
  // ↳ All courses to display

const [loading, setLoading] = useState(true);
  // ↳ Show/hide loading spinner

const [searchQuery, setSearchQuery] = useState('');
  // ↳ What user is searching for

const [selectedCategory, setSelectedCategory] = useState('');
  // ↳ Which category filter selected

const [freeOnly, setFreeOnly] = useState(false);
  // ↳ Show free courses only?

const [cartCount, setCartCount] = useState(0);
  // ↳ Number of items in cart (for badge)

const [addingToCart, setAddingToCart] = useState<number | null>(null);
  // ↳ Which course is being added (show spinner on button)
```

---

## 💾 Database Models

### Courses Table
```sql
CREATE TABLE courses (
  id INTEGER PRIMARY KEY,
  path VARCHAR UNIQUE,
  title VARCHAR,
  description TEXT,
  category VARCHAR,
  is_paid BOOLEAN,
  price FLOAT,
  created_at DATETIME
)

Sample Data:
id | path                  | title                   | price  | category
---|-----------------------|-------------------------|--------|--------
1  | python-fundamentals  | Python Fundamentals     | 49.99  | Programming
2  | web-dev-101          | Web Development 101     | 99.99  | Web Development
3  | react-advanced       | Advanced React          | 149.99 | Web Development
```

### Digital Products Table
```sql
CREATE TABLE digital_products (
  id INTEGER PRIMARY KEY,
  seller_id INTEGER,
  name VARCHAR,
  slug VARCHAR UNIQUE,
  description TEXT,
  product_type VARCHAR,
  category VARCHAR,
  price FLOAT,
  thumbnail_url VARCHAR,
  status VARCHAR,
  average_rating FLOAT,
  sales_count INTEGER,
  created_at DATETIME
)

Sample Data:
id | name           | product_type | price | status    | average_rating
---|----------------|--------------|-------|-----------|---------------
1  | React Cheatsheet | ebook       | 9.99  | PUBLISHED | 4.8
2  | Template Pack   | template      | 19.99 | PUBLISHED | 4.5
3  | Design Guide    | guide         | 14.99 | PUBLISHED | 4.7
```

### Cart Items Table
```sql
CREATE TABLE cart_items (
  id INTEGER PRIMARY KEY,
  user_id INTEGER,
  course_id INTEGER,
  price FLOAT,
  quantity INTEGER,
  added_at DATETIME
)

Sample Data:
id | user_id | course_id | price | quantity | added_at
---|---------|-----------|-------|----------|------------------
1  | 5       | 1         | 49.99 | 1        | 2026-01-28 10:30:00
2  | 5       | 3         | 149.99| 1        | 2026-01-28 10:35:00
```

---

## 🔄 Complete API Flow

### For Browsing Courses

```
1. User visits: http://localhost:3000/marketplace
   ↓
2. Frontend calls: GET /api/v1x/marketplace/courses?category=Web Development
   ↓
3. Backend receives request with session cookie
   ↓
4. Backend queries database:
   - SELECT * FROM courses WHERE category = 'Web Development'
   - For each course, get video count, rating, purchase status
   ↓
5. Backend returns JSON array of courses
   ↓
6. Frontend stores in React state: setCourses(data)
   ↓
7. Component renders course cards
   ↓
8. User sees marketplace homepage with courses displayed
```

### For Adding to Cart

```
1. User clicks "Add to Cart" button
   ↓
2. Frontend calls: POST /api/v1x/marketplace/cart/add
   Body: { course_id: 1 }
   ↓
3. Backend receives request, validates user is logged in
   ↓
4. Backend queries:
   - SELECT * FROM courses WHERE id = 1
   - SELECT * FROM cart_items WHERE user_id = 5 AND course_id = 1
   ↓
5. Backend either:
   - Updates existing cart item quantity, OR
   - Inserts new cart item
   ↓
6. Backend commits to database
   ↓
7. Frontend refreshes course list to show "In Cart" button
   ↓
8. User sees cart updated
```

---

## 🌐 Environment Setup

### Frontend Configuration (`.env.local`)
```bash
# API Base URL (backend)
NEXT_PUBLIC_API_BASE=http://localhost:8001

# Or leave empty to make relative URLs to same origin
# NEXT_PUBLIC_API_BASE=
```

### Backend Configuration (`backend/.env`)
```bash
# Database
DATABASE_URL=sqlite:///./app/data/skillforge.db

# Server
ENVIRONMENT=development
API_PORT=8001
```

---

## ✅ Key Points Summary

### Frontend (Next.js)
- **Pages**: `src/pages/marketplace/index.tsx`
- **API Calls**: Using `fetch()` with session cookies
- **State Management**: React `useState` hooks
- **Rendering**: Maps course/product arrays to JSX

### Backend (FastAPI)
- **Router**: `backend/app/api/v1x/marketplace.py`
- **Endpoints**: 30+ RESTful endpoints
- **Database**: SQLAlchemy ORM with SQLite
- **Authentication**: Session cookies (get_current_user)

### Database (SQLite)
- **Tables**: courses, digital_products, cart_items, orders, etc.
- **Relationships**: users → courses, products; users → cart_items
- **Location**: `backend/app/data/skillforge.db`

---

## 🎯 Complete Request/Response Example

### Request
```
GET http://localhost:8001/api/v1x/marketplace/courses?category=Web%20Development
Host: localhost:8001
Cookie: session=abc123xyz789
Accept: application/json
```

### Response
```json
[
  {
    "id": 2,
    "path": "web-dev-101",
    "title": "Web Development 101",
    "description": "Master HTML, CSS, JavaScript",
    "category": "Web Development",
    "is_paid": true,
    "price": 99.99,
    "video_count": 25,
    "is_purchased": false,
    "is_in_cart": false,
    "rating": 4.8
  },
  {
    "id": 3,
    "path": "react-advanced",
    "title": "Advanced React",
    "description": "Learn advanced React patterns",
    "category": "Web Development",
    "is_paid": true,
    "price": 149.99,
    "video_count": 18,
    "is_purchased": false,
    "is_in_cart": false,
    "rating": 4.9
  }
]
```

---

## 📊 Data Flow Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      BROWSER / USER                             │
├──────────────────────────────────────────────────────────────────┤
│  Marketplace Page (index.tsx)                                    │
│  ├─ Search Form                                                  │
│  ├─ Filter Sidebar (Categories, Price Range)                    │
│  └─ Course Grid                                                  │
│     ├─ Course Card 1 [Add to Cart]                             │
│     ├─ Course Card 2 [Add to Cart]                             │
│     └─ Course Card 3 [Already Purchased]                       │
└──────────────────────────────────────────────────────────────────┘
                              ↕ HTTP
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                         │
├──────────────────────────────────────────────────────────────────┤
│  /api/v1x/marketplace/courses [GET]                             │
│  ├─ Authenticate user (session cookie)                          │
│  ├─ Parse query parameters                                      │
│  ├─ Build SQLAlchemy query                                      │
│  └─ Get additional data (videos, ratings, cart status)         │
└──────────────────────────────────────────────────────────────────┘
                              ↕ SQL
┌──────────────────────────────────────────────────────────────────┐
│                    DATABASE (SQLite)                             │
├──────────────────────────────────────────────────────────────────┤
│  SELECT c.*, COUNT(v.id) as video_count                         │
│  FROM courses c                                                  │
│  LEFT JOIN videos v ON v.course_id = c.id                      │
│  LEFT JOIN orders o ON o.user_id = ? AND o.course_id = c.id   │
│  WHERE c.category = 'Web Development'                          │
│  GROUP BY c.id                                                  │
└──────────────────────────────────────────────────────────────────┘
                              ↕ Results
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND FORMATS & RETURNS                     │
├──────────────────────────────────────────────────────────────────┤
│  JSON Array of CourseListItem objects                           │
│  ├─ id, title, description, price, rating, video_count         │
│  ├─ is_purchased (user already took this course?)              │
│  └─ is_in_cart (user added to cart?)                           │
└──────────────────────────────────────────────────────────────────┘
                              ↕ HTTP Response
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND RENDERS                              │
├──────────────────────────────────────────────────────────────────┤
│  React Component receives JSON data                             │
│  ├─ Stores in state: setCourses(data)                          │
│  ├─ Maps over array: courses.map(course => <Card />)           │
│  └─ Renders course cards with buttons                          │
└──────────────────────────────────────────────────────────────────┘
```

---

**This is the complete flow for displaying courses and products in the SkillForge marketplace!**
