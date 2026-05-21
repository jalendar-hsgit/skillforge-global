# 📚 Complete Marketplace Data Flow - Documentation Index

**Purpose**: Index for all marketplace display flow documentation  
**Date**: January 28, 2026

---

## Quick Navigation

### 🚀 Start Here - Quick Reference
**5 Minute Read** - Get the overview quickly
- **[MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md](MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md)**
  - Visual diagrams
  - Step-by-step flow
  - Database tables
  - API endpoints used

### 📖 Detailed Flow Explanation
**15 Minute Read** - Understand the complete architecture
- **[MARKETPLACE_COMPLETE_DATA_FLOW.md](MARKETPLACE_COMPLETE_DATA_FLOW.md)**
  - High-level architecture
  - Step-by-step flow with code snippets
  - Database models with examples
  - Request/response examples
  - Complete flow diagram

### 💻 Code Examples
**20 Minute Read** - See actual implementation
- **[MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md)**
  - Frontend React component (full code)
  - Backend FastAPI endpoints (full code)
  - Database schema & SQL
  - Environment setup
  - Testing with curl

---

## Understanding the Flow

### What Happens When User Visits Marketplace?

```
User Opens Browser
       ↓
Navigates to: http://localhost:3000/marketplace
       ↓
Frontend loads: src/pages/marketplace/index.tsx
       ↓
React useEffect runs fetchCourses()
       ↓
Makes HTTP GET to: /api/v1x/marketplace/courses
       ↓
Backend receives request
       ↓
Database queried for courses
       ↓
Backend returns JSON array
       ↓
Frontend stores in React state: setCourses(data)
       ↓
Component re-renders
       ↓
User sees marketplace with course cards
```

---

## By Layer

### Frontend (Next.js TypeScript)
**Location**: `src/pages/marketplace/index.tsx`

**Responsibilities**:
- Display UI to user
- Accept user input (search, filters)
- Make API requests to backend
- Store data in React state
- Handle loading/error states
- Render course cards
- Handle add-to-cart button clicks

**Key Functions**:
```typescript
fetchCourses()      // Get courses from backend
addToCart()         // Add item to cart
fetchCartCount()    // Update cart badge count
handleSearch()      // Search courses
```

**Key State Variables**:
```typescript
courses[]           // Array of courses to display
loading             // Is data loading?
searchQuery         // User's search input
selectedCategory    // Which category filter?
cartCount           // Items in cart
```

---

### Backend (FastAPI Python)
**Location**: `backend/app/api/v1x/marketplace.py`

**Responsibilities**:
- Receive HTTP requests from frontend
- Validate user authentication
- Query database
- Process/format data
- Return JSON responses
- Handle errors

**Key Endpoints**:
```python
GET /api/v1x/marketplace/courses      # List courses
POST /api/v1x/marketplace/cart/add     # Add to cart
GET /api/v1x/marketplace/cart          # Get cart
DELETE /api/v1x/marketplace/cart/{id}  # Remove from cart
POST /api/v1x/marketplace/checkout     # Checkout
```

**Key Functions**:
```python
get_courses()       # Fetch and filter courses
add_to_cart()       # Add item to cart
get_cart()          # Get user's cart
```

---

### Database (SQLite)
**Location**: `backend/app/data/skillforge.db`

**Key Tables**:
```
courses              # Course information (id, title, price, category, etc.)
videos              # Videos in each course (for video_count)
reviews             # Reviews and ratings (for rating calculation)
cart_items          # Shopping cart contents (user's selected courses)
orders              # Completed purchases
users               # User accounts and authentication
```

**Key Relationships**:
```
courses      1 ←→ Many videos
courses      1 ←→ Many reviews
users        1 ←→ Many cart_items
users        1 ←→ Many orders
```

---

## Data Flow Example

### Request
```
GET http://localhost:8001/api/v1x/marketplace/courses?category=Web%20Development
Host: localhost:8001
Cookie: session=abc123xyz
Accept: application/json
```

### Processing
```
1. Backend receives request
2. Extracts query parameters: category="Web Development"
3. Gets session cookie: session=abc123xyz
4. Authenticates user (optional)
5. Builds SQL query:
   SELECT * FROM courses WHERE category = 'Web Development'
6. Executes query on database
7. For each course:
   - Count videos: SELECT COUNT(*) FROM videos
   - Calculate rating: SELECT AVG(rating) FROM reviews
   - Check purchase: SELECT * FROM orders WHERE user_id=X AND course_id=Y
   - Check cart: SELECT * FROM cart_items WHERE user_id=X AND course_id=Y
8. Formats response as JSON
9. Returns HTTP 200 with JSON data
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
  }
]
```

---

## API Endpoints Reference

### For Displaying Products

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/v1x/marketplace/courses` | List courses | Optional |
| GET | `/api/v1x/marketplace/digital-products` | List digital products | No |
| GET | `/api/v1x/marketplace/search` | Search products | No |
| GET | `/api/v1x/marketplace/trending` | Get trending items | No |
| GET | `/api/v1x/marketplace/categories` | List categories | No |

### For Cart Operations

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/v1x/marketplace/cart` | Get cart contents | Yes |
| POST | `/api/v1x/marketplace/cart/add` | Add item | Yes |
| DELETE | `/api/v1x/marketplace/cart/{id}` | Remove item | Yes |
| POST | `/api/v1x/marketplace/checkout` | Checkout | Yes |

---

## Environment Configuration

### Frontend (.env.local)
```bash
# API endpoint for backend requests
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### Backend (.env)
```bash
# Database connection
DATABASE_URL=sqlite:///./app/data/skillforge.db

# Server settings
ENVIRONMENT=development
API_PORT=8001
DEBUG=true
```

---

## Running the System

### 1. Start Backend Server
```bash
cd backend
pip install -r requirements.txt
python init_db.py                    # Create tables
python seed_all_demo_data.py         # Add sample data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Start Frontend Server
```bash
npm run dev

# Runs on http://localhost:3000
```

### 3. Open Browser
```
Visit: http://localhost:3000/marketplace
```

---

## Common Tasks

### Display Courses with Filtering
**Frontend File**: `src/pages/marketplace/index.tsx` (Line 53-70)
**Backend Endpoint**: `GET /api/v1x/marketplace/courses`
**See**: [MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md) - Frontend Implementation

### Add Item to Cart
**Frontend Function**: `addToCart()` (Line 95-115)
**Backend Endpoint**: `POST /api/v1x/marketplace/cart/add`
**See**: [MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md) - Backend Implementation

### Handle Search
**Frontend Function**: `handleSearch()` (Line 145-148)
**Backend Query Parameter**: `search=...`
**See**: [MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md](MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md)

### Database Queries
**Database File**: `backend/app/data/skillforge.db`
**See**: [MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md) - Database Schema

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              BROWSER (User)                 │
└─────────────────────────────────────────────┘
              ↕ HTTP Requests/Responses
┌─────────────────────────────────────────────┐
│    FRONTEND (Next.js TypeScript)            │
│  src/pages/marketplace/index.tsx            │
│  - React components                         │
│  - State management                         │
│  - API requests                             │
└─────────────────────────────────────────────┘
              ↕ fetch() calls
┌─────────────────────────────────────────────┐
│      BACKEND (FastAPI Python)               │
│  backend/app/api/v1x/marketplace.py         │
│  - HTTP endpoints                           │
│  - Business logic                           │
│  - Database queries                         │
└─────────────────────────────────────────────┘
              ↕ SQLAlchemy ORM
┌─────────────────────────────────────────────┐
│    DATABASE (SQLite)                        │
│  backend/app/data/skillforge.db             │
│  - 40+ tables                               │
│  - User data, courses, products, orders     │
└─────────────────────────────────────────────┘
```

---

## Key Concepts

### State Management
Frontend uses React `useState()` to manage:
- Course data loaded from backend
- Loading/error states
- Search query and filters
- Cart count for badge

### API Communication
Frontend uses `fetch()` to call backend:
- With `credentials: 'include'` for session cookie
- Returns JSON responses
- Handles errors with HTTP status codes

### Database Queries
Backend uses SQLAlchemy ORM:
- Type-safe queries
- Relationship handling
- Automatic SQL generation
- Session management

### Response Format
Backend returns Pydantic models:
- Validated data structures
- Automatic JSON serialization
- Type hints for frontend

---

## Troubleshooting

### "Failed to load courses"
**Likely Cause**: Backend not running or wrong API path  
**Solution**: Check backend is running on port 8001, verify `NEXT_PUBLIC_API_BASE` is set

### "404 Not Found"
**Likely Cause**: Wrong endpoint path in frontend  
**Solution**: Verify endpoint matches backend router (should use `/api/v1x/marketplace/`)

### "Cannot read property 'map' of undefined"
**Likely Cause**: courses state not updated properly  
**Solution**: Check response is array, setCourses() called with correct data

### "Session cookie not sent"
**Likely Cause**: `credentials: 'include'` not set in fetch()  
**Solution**: Add `credentials: 'include'` to all authenticated API calls

---

## Files to Reference

### Frontend
- **Main Page**: `src/pages/marketplace/index.tsx` (363 lines)
- **Cart**: `src/pages/marketplace/cart.tsx`
- **Checkout**: `src/pages/marketplace/checkout.tsx`
- **Orders**: `src/pages/marketplace/orders.tsx`

### Backend
- **Main Router**: `backend/app/api/v1x/marketplace.py` (2735 lines)
- **Models**: `backend/app/modelsx/marketplace.py`
- **Schemas**: `backend/app/schemas/marketplace.py`

### Database
- **Database**: `backend/app/data/skillforge.db`
- **Models**: `backend/app/models/user.py`, `backend/app/modelsx/course.py`

---

## Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Next.js, React, TypeScript | User interface, state management |
| Backend | FastAPI, Python | API endpoints, business logic |
| Database | SQLite | Data persistence |
| Communication | HTTP/REST | Request-response between layers |

---

## Documentation Files

1. **[MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md](MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md)** - Quick reference with diagrams
2. **[MARKETPLACE_COMPLETE_DATA_FLOW.md](MARKETPLACE_COMPLETE_DATA_FLOW.md)** - Detailed flow explanation
3. **[MARKETPLACE_CODE_EXAMPLES.md](MARKETPLACE_CODE_EXAMPLES.md)** - Real code implementation

---

**Start with [MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md](MARKETPLACE_DISPLAY_FLOW_QUICK_REF.md) for a quick overview, then dive into specific files as needed.**
