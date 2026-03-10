# 📘 Marketplace Data Flow - Complete Documentation Created

**Date**: January 28, 2026  
**Topic**: How courses & products are displayed in the marketplace frontend

---

## What Was Created

### 4 Comprehensive Documentation Files

#### 1. **MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md** ⭐ START HERE
- **Time to Read**: 5-10 minutes
- **Best For**: Quick understanding of the flow
- **Contains**:
  - Visual step-by-step flow (6 steps)
  - Frontend code snippets showing API calls
  - Backend query examples
  - Database tables involved
  - Complete flow diagram
  - API endpoints summary
  - Typical response examples

#### 2. **MARKETPLACE_COMPLETE_DATA_FLOW.md** 📚 DETAILED
- **Time to Read**: 15-20 minutes
- **Best For**: Deep understanding of architecture
- **Contains**:
  - High-level architecture diagram
  - Step-by-step flow with full context
  - Frontend state management details
  - Backend API endpoint specifications
  - Database models with sample data
  - Adding to cart flow explanation
  - Complete request/response examples
  - Data flow architecture diagram

#### 3. **MARKETPLACE_CODE_EXAMPLES.md** 💻 IMPLEMENTATION
- **Time to Read**: 20-25 minutes
- **Best For**: Understanding actual code
- **Contains**:
  - Complete React component (full code - 363 lines)
  - Complete Backend endpoint (full code)
  - Database schema with SQL
  - Sample data inserts
  - Environment setup (.env files)
  - How to run the application
  - Testing with curl commands

#### 4. **MARKETPLACE_DATA_FLOW_INDEX.md** 🗺️ NAVIGATION
- **Time to Read**: 5 minutes
- **Best For**: Navigation and overview
- **Contains**:
  - Quick navigation guide
  - Summary by layer (Frontend, Backend, Database)
  - Data flow example
  - API endpoints reference table
  - Environment configuration
  - Running instructions
  - Common tasks guide
  - Troubleshooting section

---

## The Complete Flow Explained

### 6-Step Process

```
Step 1: User Opens Marketplace
        ↓ 
        URL: http://localhost:3000/marketplace

Step 2: Frontend Makes API Request
        ↓
        const response = await fetch(`/api/v1x/marketplace/courses?category=...`)

Step 3: Backend Receives Request
        ↓
        @router.get("/courses")
        def get_courses(category: str, db: Session)

Step 4: Database Query Executed
        ↓
        SELECT * FROM courses WHERE category = 'Web Development'
        SELECT COUNT(*) FROM videos WHERE course_id = ...
        SELECT AVG(rating) FROM reviews WHERE course_id = ...

Step 5: Backend Returns JSON Response
        ↓
        [{
          "id": 1,
          "title": "Python Fundamentals",
          "price": 49.99,
          "rating": 4.5,
          "video_count": 12,
          "is_in_cart": false
        }, ...]

Step 6: Frontend Renders UI
        ↓
        courses.map(course => <CourseCard />) 
        ↓
        User sees marketplace with course cards
```

---

## Key Components Explained

### Frontend (Next.js)
**File**: `src/pages/marketplace/index.tsx`

**What It Does**:
1. User visits `http://localhost:3000/marketplace`
2. Component loads with `useEffect()`
3. Calls `fetchCourses()` function
4. Makes `fetch()` request to backend API
5. Receives JSON response
6. Stores data in React state with `setCourses(data)`
7. Component re-renders
8. Maps over courses array to create course cards
9. Shows UI to user

**Key State Variables**:
```typescript
const [courses, setCourses] = useState([])     // Array of courses
const [loading, setLoading] = useState(true)   // Is loading?
const [cartCount, setCartCount] = useState(0)  // Cart badge
const [selectedCategory, setSelectedCategory] = '' // Filter
```

---

### Backend (FastAPI)
**File**: `backend/app/api/v1x/marketplace.py`

**What It Does**:
1. Receives HTTP GET request from frontend
2. Extracts query parameters (category, search, etc.)
3. Validates user authentication (optional)
4. Builds SQLAlchemy query to database
5. Fetches courses matching criteria
6. For each course, gets:
   - Video count
   - Average rating
   - Whether user purchased it
   - Whether user has it in cart
7. Formats response as JSON (using Pydantic schema)
8. Returns JSON array to frontend

**Key Endpoint**:
```python
GET /api/v1x/marketplace/courses
Query Parameters:
  - category: str (optional)
  - search: str (optional)
  - free_only: bool (optional)
  - skip: int (default 0)
  - limit: int (default 20)

Returns: List[CourseListItem]
```

---

### Database (SQLite)
**File**: `backend/app/data/skillforge.db`

**Tables Involved**:
```sql
-- Main courses data
CREATE TABLE courses (
  id, path, title, description, category, 
  is_paid, price, created_at
)

-- Videos in each course (for video_count)
CREATE TABLE videos (
  id, course_id, title, duration, url
)

-- Reviews and ratings (for average rating)
CREATE TABLE reviews (
  id, course_id, user_id, rating, comment
)

-- User's shopping cart (for is_in_cart check)
CREATE TABLE cart_items (
  id, user_id, course_id, price, quantity
)

-- User's purchases (for is_purchased check)
CREATE TABLE orders (
  id, user_id, course_id, amount, status
)
```

---

## Visual Architecture

```
┌────────────────────────────┐
│    USER BROWSER            │
│  http://localhost:3000     │
└────────────────────────────┘
            ↕ HTTP
┌────────────────────────────┐
│  FRONTEND (Next.js)        │
│  - React component         │
│  - fetch() API calls       │
│  - React state (useState)  │
│  - Renders UI              │
└────────────────────────────┘
            ↕ fetch()
┌────────────────────────────┐
│  BACKEND (FastAPI)         │
│  - @router.get("/courses") │
│  - Authenticate user       │
│  - Query database          │
│  - Return JSON             │
└────────────────────────────┘
            ↕ SQLAlchemy ORM
┌────────────────────────────┐
│  DATABASE (SQLite)         │
│  - courses table           │
│  - videos table            │
│  - reviews table           │
│  - orders table            │
│  - cart_items table        │
└────────────────────────────┘
```

---

## How Data Flows

### Request Path
```
Browser 
  → fetch(`/api/v1x/marketplace/courses?category=Web Development`)
    → Network (HTTP GET)
      → Backend receives
        → SQLAlchemy builds query
          → SQLite executes SQL
```

### Response Path
```
Database (rows)
  → SQLAlchemy returns objects
    → Backend formats as Pydantic models
      → Converts to JSON
        → Network (HTTP 200)
          → Browser receives JSON
            → Frontend parses with await response.json()
              → React state updated (setCourses)
                → Component re-renders
                  → User sees course cards
```

---

## API Endpoints

### For Displaying Products

```
GET /api/v1x/marketplace/courses
  → Returns: Array of Course objects
  
GET /api/v1x/marketplace/digital-products  
  → Returns: { total, items[], page, total_pages }
  
GET /api/v1x/marketplace/search?q=python
  → Returns: Array of matching products
  
GET /api/v1x/marketplace/trending
  → Returns: Popular products
  
GET /api/v1x/marketplace/categories
  → Returns: Array of category names
```

### For Cart Operations

```
GET /api/v1x/marketplace/cart
  → Returns: { items[], subtotal, tax, total }
  
POST /api/v1x/marketplace/cart/add
  Body: { course_id, quantity }
  → Returns: { message, course_id, quantity }
  
DELETE /api/v1x/marketplace/cart/{item_id}
  → Returns: { message }
  
POST /api/v1x/marketplace/checkout
  Body: { items[], payment_method }
  → Returns: { order_id, amount, status }
```

---

## Quick Start Guide

### To View the Documentation

1. **Quick Overview** (5 min): [MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md](MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md)
2. **Complete Details** (20 min): [MARKETPLACE_COMPLETE_DATA_FLOW.md](MARKETPLACE_COMPLETE_DATA_FLOW.md)
3. **Code Examples** (25 min): [MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md)
4. **Navigation Help** (5 min): [MARKETPLACE_DATA_FLOW_INDEX.md](MARKETPLACE_DATA_FLOW_INDEX.md)

### To Run the System

```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python init_db.py
python seed_all_demo_data.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Terminal 2: Frontend
npm run dev

# Visit http://localhost:3000/marketplace
```

---

## Summary Table

| Aspect | Technology | File | Key Function |
|--------|-----------|------|---|
| **Frontend UI** | Next.js/React | `src/pages/marketplace/index.tsx` | `fetchCourses()` |
| **Backend API** | FastAPI | `backend/app/api/v1x/marketplace.py` | `@router.get("/courses")` |
| **Database** | SQLite | `backend/app/data/skillforge.db` | SQL queries |
| **State** | React hooks | `index.tsx` | `useState()` |
| **HTTP** | fetch API | `index.tsx` | `await fetch()` |
| **ORM** | SQLAlchemy | `marketplace.py` | `db.query()` |

---

## Documentation Files Created

✅ **MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md**  
✅ **MARKETPLACE_COMPLETE_DATA_FLOW.md**  
✅ **MARKETPLACE_CODE_EXAMPLES.md**  
✅ **MARKETPLACE_DATA_FLOW_INDEX.md**  

**Total Documentation**: 4 files with comprehensive explanations

---

## Key Takeaways

1. **Frontend**: Fetches courses from backend API using `fetch()`
2. **Backend**: Queries SQLite database using SQLAlchemy ORM
3. **Database**: Stores courses, videos, reviews, cart items, orders
4. **Flow**: Browser → Frontend → Backend → Database → Backend → Frontend → Browser
5. **Authentication**: Optional, using session cookies
6. **Response Format**: JSON arrays of course objects

---

**All documentation files are ready in the workspace. Start with the Quick Reference guide!**
