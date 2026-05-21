# 🎯 Marketplace Display Flow - Quick Reference

**Purpose**: Quick visual guide for courses/products display flow

---

## 1️⃣ User Opens Marketplace

```
User: I want to browse courses
       ↓
URL: http://localhost:3000/marketplace
       ↓
Frontend loads: src/pages/marketplace/index.tsx
```

---

## 2️⃣ Frontend Makes API Request

```typescript
// Frontend Code
const fetchCourses = async () => {
  const url = `/api/v1x/marketplace/courses?category=${category}`;
  
  const response = await fetch(url, {
    credentials: 'include'  // Include session cookie
  });
  
  const data = await response.json();  // Parse JSON
  setCourses(data);  // Store in React state
};
```

**HTTP Request Sent**:
```
GET /api/v1x/marketplace/courses?category=Web%20Development HTTP/1.1
Host: localhost:8001
Cookie: session=abc123xyz
Accept: application/json
```

---

## 3️⃣ Backend Receives & Queries

```python
# Backend Code (marketplace.py)
@router.get("/courses")
def get_courses(category: str = None, db: Session = Depends(get_db)):
    # Query database
    courses = db.query(Course).filter(
        Course.category == category
    ).all()
    
    # Add extra info for each course
    for course in courses:
        course.video_count = db.query(Video).filter_by(course_id=course.id).count()
        course.rating = db.query(Review).filter_by(course_id=course.id).avg()
    
    # Return JSON
    return courses
```

**SQL Query Executed**:
```sql
SELECT * FROM courses WHERE category = 'Web Development'
SELECT COUNT(*) FROM videos WHERE course_id = 1
SELECT AVG(rating) FROM reviews WHERE course_id = 1
...
```

---

## 4️⃣ Backend Returns JSON Response

```json
[
  {
    "id": 2,
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
    "title": "Advanced React",
    "category": "Web Development",
    "is_paid": true,
    "price": 149.99,
    "video_count": 18,
    "rating": 4.9
  }
]
```

---

## 5️⃣ Frontend Renders UI

```typescript
// React renders the data
return (
  <div className="course-grid">
    {courses.map(course => (
      <div className="course-card" key={course.id}>
        <h3>{course.title}</h3>
        <p>{course.description}</p>
        <span className="rating">⭐ {course.rating}</span>
        <span className="price">${course.price}</span>
        <span className="videos">📹 {course.video_count} videos</span>
        
        <button onClick={() => addToCart(course.id)}>
          🛒 Add to Cart
        </button>
      </div>
    ))}
  </div>
);
```

---

## 6️⃣ User Sees Marketplace

```
┌─────────────────────────────────────────┐
│         SkillForge Marketplace          │
├─────────────────────────────────────────┤
│  🔍 Search [_____________]  🛒 Cart (0) │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐   │
│  │ Web Dev 101  │  │ React Adv.   │   │
│  │              │  │              │   │
│  │ Master HTML, │  │ Learn adv.   │   │
│  │ CSS, JS      │  │ patterns     │   │
│  │              │  │              │   │
│  │ ⭐ 4.8      │  │ ⭐ 4.9      │   │
│  │ 📹 25 videos │  │ 📹 18 videos │   │
│  │              │  │              │   │
│  │ $99.99       │  │ $149.99      │   │
│  │              │  │              │   │
│  │ [Add to Cart]│  │[Add to Cart]│   │
│  └──────────────┘  └──────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🛒 Adding to Cart Flow

```
User clicks [Add to Cart] on course card
        ↓
Frontend calls: POST /api/v1x/marketplace/cart/add
Body: { course_id: 2 }
        ↓
Backend inserts into cart_items table:
  INSERT INTO cart_items (user_id, course_id, price, added_at)
  VALUES (5, 2, 99.99, 2026-01-28 10:30:00)
        ↓
Frontend refreshes data:
  - Calls fetchCourses() again
  - Updates cartCount badge
        ↓
Button changes from [Add to Cart] to [In Cart]
```

---

## 📊 Database Tables Involved

```
┌─ COURSES Table
│  id | title | description | price | category | video_count
│  1  | Python... | Learn Python | 49.99 | Programming | 12
│  2  | Web Dev... | Master web | 99.99 | Web Dev | 25
│
├─ VIDEOS Table (for video_count)
│  id | course_id | title | duration
│  1  | 1 | Intro | 5:30
│  2  | 1 | Variables | 12:00
│
├─ REVIEWS Table (for rating)
│  id | course_id | user_id | rating | comment
│  1  | 1 | 3 | 5 | Great course!
│  2  | 1 | 4 | 4 | Good
│
├─ CART_ITEMS Table
│  id | user_id | course_id | price | quantity | added_at
│  1  | 5 | 2 | 99.99 | 1 | 2026-01-28
│
└─ ORDERS Table
   id | user_id | course_id | amount | status | order_date
   1  | 5 | 1 | 49.99 | completed | 2026-01-27
```

---

## 🔌 API Endpoints Used

### For Displaying Products

```
GET /api/v1x/marketplace/courses
├─ Query Params: category, free_only, search, skip, limit
└─ Returns: Array of CourseListItem objects

GET /api/v1x/marketplace/digital-products
├─ Query Params: search, category, product_type, min_price, max_price
└─ Returns: { total, items, page, total_pages }

GET /api/v1x/marketplace/search
├─ Query Params: q (search term)
└─ Returns: Array of matching products

GET /api/v1x/marketplace/trending
└─ Returns: Popular products

GET /api/v1x/marketplace/categories
└─ Returns: Array of category names
```

### For Cart Operations

```
POST /api/v1x/marketplace/cart/add
├─ Body: { course_id: 1 }
└─ Returns: { message: "Added to cart" }

GET /api/v1x/marketplace/cart
└─ Returns: { items: [], subtotal, tax, total }

DELETE /api/v1x/marketplace/cart/{item_id}
└─ Returns: { message: "Removed from cart" }

POST /api/v1x/marketplace/checkout
├─ Body: { items: [...], payment_method: "stripe" }
└─ Returns: { order_id, total_amount, status }
```

---

## 🔄 Complete Flow Diagram

```
BROWSER SIDE (Next.js)
┌─────────────────────────────────┐
│ Marketplace Index Page          │
│ src/pages/marketplace/index.tsx │
└─────────────────────────────────┘
         useEffect()
           ↓
    fetchCourses()
           ↓
    setState(courses)
           ↓
   courses.map(...) → render cards
           ↓
┌─────────────────────────────────┐
│ Display Course Cards to User    │
│ Each with: title, price, rating │
│ Button: Add to Cart             │
└─────────────────────────────────┘

─────────────────────────────────────── HTTP ──────────────────────

BACKEND SIDE (FastAPI)
┌──────────────────────────────────┐
│ Marketplace Router               │
│ backend/app/api/v1x/marketplace  │
└──────────────────────────────────┘
       @router.get("/courses")
           ↓
    Query Database (SQLAlchemy)
           ↓
    Fetch courses, videos, ratings
           ↓
    Format as JSON (CourseListItem)
           ↓
    Return Response

──────────────────────────────────────── SQL ──────────────────────

DATABASE SIDE (SQLite)
┌──────────────────────────────────┐
│ SQLite Database                  │
│ skillforge.db                    │
│                                  │
│ courses table                    │
│ videos table                     │
│ reviews table                    │
│ cart_items table                 │
│ orders table                     │
└──────────────────────────────────┘
```

---

## ⚙️ Key Configuration

### Frontend Environment
```
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### Backend Server
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Server
```
npm run dev (runs on port 3000)
```

---

## 📱 Typical Course Display Response

```json
{
  "courses": [
    {
      "id": 1,
      "path": "python-fundamentals",
      "title": "Python Fundamentals",
      "description": "Learn Python from scratch...",
      "category": "Programming",
      "is_paid": true,
      "price": 49.99,
      "video_count": 12,
      "is_purchased": false,
      "is_in_cart": false,
      "rating": 4.5,
      "thumbnail": "https://...",
      "instructor": {
        "name": "John Doe",
        "id": 3
      }
    },
    {
      "id": 2,
      "path": "web-development-101",
      "title": "Web Development 101",
      "description": "Master HTML, CSS, JavaScript...",
      "category": "Web Development",
      "is_paid": true,
      "price": 99.99,
      "video_count": 25,
      "is_purchased": false,
      "is_in_cart": false,
      "rating": 4.8
    }
  ]
}
```

---

## ✅ Summary

| Layer | Component | What Happens |
|-------|-----------|---|
| **Frontend** | User clicks marketplace link | Navigates to `/marketplace` page |
| **Frontend** | Page loads (index.tsx) | useEffect runs fetchCourses() |
| **Frontend** | React state | Sets loading = true |
| **Network** | HTTP Request | GET /api/v1x/marketplace/courses |
| **Backend** | Router receives request | Processes query params |
| **Backend** | Database query | SELECT * FROM courses |
| **Backend** | Response formatting | Converts to JSON |
| **Network** | HTTP Response | Returns JSON array |
| **Frontend** | Data arrives | Sets courses state |
| **Frontend** | React render | maps courses to JSX cards |
| **User** | Sees page | Courses displayed with options |

---

**COMPLETE FLOW: Frontend → Network → Backend → Database → Backend → Network → Frontend → UI**
