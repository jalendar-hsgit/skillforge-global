# 💻 Marketplace Display - Code Examples & Implementation

**Purpose**: Real code examples for displaying courses/products

---

## Frontend Implementation

### 1. Fetch Data from Backend

**File**: `src/pages/marketplace/index.tsx`

```typescript
import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { ShoppingCart, Search, Filter, Star } from 'lucide-react';

interface Course {
  id: number;
  path: string;
  title: string;
  description: string;
  category: string;
  is_paid: boolean;
  price: number | null;
  video_count: number;
  is_purchased: boolean;
  is_in_cart: boolean;
  rating?: number;
}

export default function MarketplacePage() {
  // State variables
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [cartCount, setCartCount] = useState(0);

  // Fetch courses when component loads or filters change
  useEffect(() => {
    fetchCourses();
  }, [selectedCategory]);

  // Main fetch function
  const fetchCourses = async () => {
    setLoading(true);
    try {
      // Build URL with query parameters
      let url = `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/courses?`;
      
      if (selectedCategory && selectedCategory !== 'All') {
        url += `category=${encodeURIComponent(selectedCategory)}&`;
      }
      
      if (searchQuery) {
        url += `search=${encodeURIComponent(searchQuery)}&`;
      }

      // Make API request
      const response = await fetch(url, {
        credentials: 'include'  // Include session cookie
      });

      if (response.ok) {
        const data = await response.json();
        setCourses(data);  // Store in state
      } else {
        console.error('Failed to fetch:', response.status);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCourses();
  };

  // Add to cart
  const addToCart = async (courseId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart/add`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ course_id: courseId })
        }
      );

      if (response.ok) {
        // Refresh cart and courses
        await fetchCourses();
        await fetchCartCount();
        alert('Added to cart!');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  // Fetch cart count for badge
  const fetchCartCount = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/cart`,
        {
          credentials: 'include'
        }
      );
      if (response.ok) {
        const data = await response.json();
        setCartCount(data.items?.length || 0);
      }
    } catch (error) {
      setCartCount(0);
    }
  };

  // Render
  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">SkillForge Marketplace</h1>
          
          {/* Search Bar */}
          <form onSubmit={handleSearch} className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-4 py-2 border rounded"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <Search className="inline mr-2" /> Search
            </button>
            
            {/* Cart Badge */}
            <div className="px-4 py-2 bg-gray-100 rounded flex items-center">
              <ShoppingCart className="mr-2" />
              <span>{cartCount}</span>
            </div>
          </form>

          {/* Category Filter */}
          <div className="flex gap-2 flex-wrap">
            {['All', 'Web Development', 'Data Science', 'AI/ML', 'Cloud'].map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin">⟳</div>
            <p className="mt-4">Loading courses...</p>
          </div>
        )}

        {/* Courses Grid */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.length === 0 ? (
              <p className="col-span-full text-center text-gray-500">
                No courses found
              </p>
            ) : (
              courses.map(course => (
                <div
                  key={course.id}
                  className="bg-white border rounded-lg overflow-hidden hover:shadow-lg transition"
                >
                  {/* Course Card */}
                  <div className="p-6">
                    <h3 className="text-xl font-semibold mb-2">
                      {course.title}
                    </h3>
                    
                    <p className="text-gray-600 text-sm mb-4">
                      {course.description}
                    </p>

                    {/* Meta Info */}
                    <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
                      <span className="bg-blue-50 px-2 py-1 rounded">
                        {course.category}
                      </span>
                      
                      {course.rating && (
                        <span className="flex items-center gap-1">
                          <Star className="w-4 h-4 fill-yellow-400" />
                          {course.rating.toFixed(1)}
                        </span>
                      )}
                    </div>

                    {/* Videos & Price */}
                    <div className="flex justify-between items-center mb-6">
                      <span className="text-gray-600">
                        📹 {course.video_count} videos
                      </span>
                      
                      {course.is_paid && (
                        <span className="text-2xl font-bold text-blue-600">
                          ${course.price}
                        </span>
                      )}
                      {!course.is_paid && (
                        <span className="text-green-600 font-semibold">
                          FREE
                        </span>
                      )}
                    </div>

                    {/* Action Button */}
                    {course.is_purchased ? (
                      <button
                        disabled
                        className="w-full py-2 bg-green-500 text-white rounded disabled:opacity-50"
                      >
                        ✓ Already Purchased
                      </button>
                    ) : course.is_in_cart ? (
                      <button
                        className="w-full py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
                        onClick={() => window.location.href = '/marketplace/cart'}
                      >
                        View in Cart
                      </button>
                    ) : (
                      <button
                        onClick={() => addToCart(course.id)}
                        className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center justify-center gap-2"
                      >
                        <ShoppingCart className="w-4 h-4" />
                        Add to Cart
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
```

---

## Backend Implementation

### 1. Backend Endpoint

**File**: `backend/app/api/v1x/marketplace.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from app.core.db import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.modelsx.course import Course
from app.modelsx.video import Video
from app.modelsx.order import CartItem, Order
from pydantic import BaseModel
from sqlalchemy import func

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


# ===== Schemas =====
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

    class Config:
        from_attributes = True


# ===== Endpoints =====

@router.get("/courses", response_model=List[CourseListItem])
def get_courses(
    category: Optional[str] = None,
    free_only: bool = False,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Get list of courses with filtering and pagination
    
    Query Parameters:
    - category: Filter by category (e.g., "Web Development")
    - free_only: Show only free courses
    - search: Search by title or description
    - skip: Pagination offset (default: 0)
    - limit: Pagination limit (default: 20)
    """
    
    # Start with base query
    query = db.query(Course)
    
    # Apply filters
    if category:
        query = query.filter(Course.category == category)
    
    if free_only:
        query = query.filter(Course.is_paid == False)
    
    if search:
        # Search in title or description
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term)
            )
        )
    
    # Apply pagination
    courses = query.offset(skip).limit(limit).all()
    
    # Build response with additional data
    result = []
    for course in courses:
        # Count videos
        video_count = db.query(Video).filter(
            Video.course_id == course.id
        ).count()
        
        # Check if user purchased
        is_purchased = False
        is_in_cart = False
        
        if current_user:
            is_purchased = bool(
                db.query(Order).filter(
                    and_(
                        Order.user_id == current_user.id,
                        Order.course_id == course.id,
                        Order.status == "completed"
                    )
                ).first()
            )
            
            is_in_cart = bool(
                db.query(CartItem).filter(
                    and_(
                        CartItem.user_id == current_user.id,
                        CartItem.course_id == course.id
                    )
                ).first()
            )
        
        # Get average rating
        rating = db.query(
            func.avg(Review.rating)
        ).filter(
            Review.course_id == course.id
        ).scalar()
        
        # Build response object
        item = CourseListItem(
            id=course.id,
            path=course.path,
            title=course.title,
            description=course.description,
            category=course.category,
            is_paid=course.is_paid,
            price=course.price,
            video_count=video_count,
            is_purchased=is_purchased,
            is_in_cart=is_in_cart,
            rating=float(rating) if rating else None
        )
        result.append(item)
    
    return result


@router.post("/cart/add")
def add_to_cart(
    item_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add item to shopping cart
    
    Request Body:
    {
        "course_id": 1,
        "quantity": 1
    }
    """
    
    course_id = item_data.get("course_id")
    quantity = item_data.get("quantity", 1)
    
    # Validate course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check if already in cart
    existing_item = db.query(CartItem).filter(
        and_(
            CartItem.user_id == current_user.id,
            CartItem.course_id == course_id
        )
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        db.commit()
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=current_user.id,
            course_id=course_id,
            price=course.price,
            quantity=quantity,
            added_at=datetime.utcnow()
        )
        db.add(cart_item)
        db.commit()
    
    return {
        "message": "Added to cart successfully",
        "course_id": course_id,
        "quantity": quantity
    }
```

---

## Database Schema

### Courses Table
```sql
CREATE TABLE courses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path VARCHAR(255) UNIQUE NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  is_paid BOOLEAN DEFAULT FALSE,
  price FLOAT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO courses (path, title, description, category, is_paid, price)
VALUES 
  ('python-fundamentals', 'Python Fundamentals', 'Learn Python from scratch', 'Programming', TRUE, 49.99),
  ('web-development-101', 'Web Development 101', 'Master HTML, CSS, JavaScript', 'Web Development', TRUE, 99.99),
  ('react-advanced', 'Advanced React', 'Learn advanced React patterns', 'Web Development', TRUE, 149.99);
```

### Videos Table
```sql
CREATE TABLE videos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER NOT NULL,
  title VARCHAR(255),
  duration INTEGER,
  url VARCHAR(500),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- Sample data
INSERT INTO videos (course_id, title, duration) VALUES
  (1, 'Introduction to Python', 330),
  (1, 'Variables and Data Types', 720),
  (1, 'Control Flow', 900);
```

### Cart Items Table
```sql
CREATE TABLE cart_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  course_id INTEGER NOT NULL,
  price FLOAT,
  quantity INTEGER DEFAULT 1,
  added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- Sample data
INSERT INTO cart_items (user_id, course_id, price, quantity)
VALUES (5, 1, 49.99, 1);
```

---

## Environment Setup

### Frontend (.env.local)
```bash
# API Base URL
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

### Backend (.env)
```bash
# Database
DATABASE_URL=sqlite:///./app/data/skillforge.db

# Server
ENVIRONMENT=development
API_PORT=8001
DEBUG=true
```

---

## Running the Application

### Terminal 1: Backend
```bash
cd d:\python\ code\sfg\skillforge-global\backend

# Install dependencies
pip install -r requirements.txt

# Run migrations (if any)
python init_db.py

# Seed demo data
python seed_all_demo_data.py

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Terminal 2: Frontend
```bash
cd d:\python\ code\sfg\skillforge-global

# Install dependencies
npm install

# Start dev server
npm run dev

# Frontend runs on http://localhost:3000
```

---

## Testing with curl

### Fetch Courses
```bash
curl -X GET "http://localhost:8001/api/v1x/marketplace/courses?category=Web%20Development" \
  -H "Accept: application/json"

# With search
curl -X GET "http://localhost:8001/api/v1x/marketplace/courses?search=python" \
  -H "Accept: application/json"
```

### Add to Cart
```bash
curl -X POST "http://localhost:8001/api/v1x/marketplace/cart/add" \
  -H "Content-Type: application/json" \
  -H "Cookie: session=abc123xyz" \
  -d '{"course_id": 1, "quantity": 1}'
```

### Get Cart
```bash
curl -X GET "http://localhost:8001/api/v1x/marketplace/cart" \
  -H "Cookie: session=abc123xyz" \
  -H "Accept: application/json"
```

---

## Key Points

1. **Frontend State Management**: React `useState` for courses, loading, etc.
2. **API Communication**: Using `fetch()` with credentials for session
3. **Backend Validation**: All queries check user permissions
4. **Database Queries**: SQLAlchemy ORM for type safety
5. **Response Format**: Consistent JSON schema with Pydantic
6. **Error Handling**: HTTP status codes and meaningful messages
7. **Pagination**: Skip/limit for large datasets
8. **Authentication**: Session cookie with credentials: 'include'

---

**This is the complete implementation for displaying courses/products in the marketplace!**
