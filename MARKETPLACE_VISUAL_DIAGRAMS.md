# 📊 Marketplace Data Flow - Visual Diagrams

**Purpose**: Visual representation of how courses/products flow through the system

---

## 1. Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                          │
│              (http://localhost:3000)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        SkillForge Marketplace Page                  │  │
│  │                                                      │  │
│  │  [Search courses...]  [Filter by category]  Cart(5) │  │
│  │                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐                │  │
│  │  │ Course Card  │  │ Course Card  │                │  │
│  │  │              │  │              │                │  │
│  │  │ Python Funda │  │ Web Dev 101  │                │  │
│  │  │ $49.99       │  │ $99.99       │                │  │
│  │  │ ⭐ 4.5       │  │ ⭐ 4.8       │                │  │
│  │  │              │  │              │                │  │
│  │  │ [Add to Cart]│  │ [In Cart ✓]  │                │  │
│  │  └──────────────┘  └──────────────┘                │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  React Code:                                                │
│  - useState(courses)                                        │
│  - useState(loading)                                        │
│  - useEffect(() => fetchCourses())                         │
│  - courses.map(c => <CourseCard />)                        │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP Requests
                    fetch('/api/v1x/marketplace/courses')
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                          │
│              (http://localhost:8001)                        │
│                                                             │
│  Router: /api/v1x/marketplace                              │
│  │                                                          │
│  ├─ @router.get("/courses")                                │
│  │  def get_courses(category, search, db):                 │
│  │     # 1. Get user from session                          │
│  │     # 2. Build database query                           │
│  │     # 3. Fetch courses                                  │
│  │     # 4. Get videos for each                            │
│  │     # 5. Get ratings for each                           │
│  │     # 6. Check if purchased/in cart                     │
│  │     # 7. Format as JSON                                 │
│  │     return CourseListItem[]                             │
│  │                                                          │
│  ├─ @router.post("/cart/add")                              │
│  │  def add_to_cart(course_id, user, db):                  │
│  │     # Add to cart_items table                           │
│  │     # Return success                                    │
│  │                                                          │
│  └─ ... (30+ more endpoints)                               │
│                                                             │
│  SQLAlchemy ORM:                                            │
│  - Converts Python objects to SQL                          │
│  - Manages database relationships                          │
│  - Handles transactions                                    │
└─────────────────────────────────────────────────────────────┘
                      ↕ SQLAlchemy ORM
                   db.query(Course).filter()
                      ↕
┌─────────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                         │
│         (backend/app/data/skillforge.db)                    │
│                                                             │
│  ┌─ COURSES TABLE                                          │
│  │ id | path | title | price | category | created_at      │
│  │─────────────────────────────────────────────────────────│
│  │ 1  | python-fund | Python Fund... | 49.99 | Prog...    │
│  │ 2  | web-dev     | Web Dev 101... | 99.99 | Web...     │
│  │ 3  | react-adv   | React Adv...  | 149.99 | Web...    │
│  │                                                          │
│  ├─ VIDEOS TABLE                                           │
│  │ id | course_id | title | duration                       │
│  │─────────────────────────────────────────────────────────│
│  │ 1  | 1 | Intro | 330                                    │
│  │ 2  | 1 | Variables | 720                                │
│  │ 3  | 2 | HTML | 450                                     │
│  │                                                          │
│  ├─ REVIEWS TABLE                                          │
│  │ id | course_id | user_id | rating | created_at         │
│  │─────────────────────────────────────────────────────────│
│  │ 1  | 1 | 5 | 5 | 2026-01-20                             │
│  │ 2  | 1 | 6 | 4 | 2026-01-19                             │
│  │ 3  | 2 | 7 | 5 | 2026-01-18                             │
│  │                                                          │
│  ├─ CART_ITEMS TABLE                                       │
│  │ id | user_id | course_id | price | quantity             │
│  │─────────────────────────────────────────────────────────│
│  │ 1  | 5 | 2 | 99.99 | 1                                  │
│  │ 2  | 5 | 3 | 149.99 | 1                                 │
│  │                                                          │
│  └─ ORDERS TABLE                                           │
│    id | user_id | course_id | amount | status | created_at│
│    ────────────────────────────────────────────────────────│
│    1  | 5 | 1 | 49.99 | completed | 2026-01-15           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Request Flow

```
STEP 1: User visits marketplace
┌─────────────┐
│   Browser   │ → http://localhost:3000/marketplace
└─────────────┘
       │
       ↓

STEP 2: Frontend loads index.tsx
┌────────────────────────┐
│ src/pages/marketplace  │
│ /index.tsx             │
└────────────────────────┘
       │
       ├─ Import React hooks
       ├─ Declare state (courses, loading, etc)
       └─ Define fetchCourses()
       │
       ↓

STEP 3: useEffect runs on mount
┌────────────────────────────────────┐
│ useEffect(() => {                  │
│   fetchCourses();                  │
│ }, [selectedCategory])             │
└────────────────────────────────────┘
       │
       ↓

STEP 4: fetchCourses() makes API request
┌────────────────────────────────────────────────┐
│ const response = await fetch(                  │
│   `/api/v1x/marketplace/courses?              │
│    category=Web%20Development`                 │
│   , { credentials: 'include' }                 │
│ );                                             │
└────────────────────────────────────────────────┘
       │
       ├─ Build URL with query params
       ├─ Include session cookie
       ├─ Set headers
       └─ Send HTTP GET request
       │
       ↓ (Network - HTTP)

STEP 5: Backend receives request
┌──────────────────────────────────────────┐
│ @router.get("/courses")                  │
│ def get_courses(                         │
│     category: str,                       │
│     db: Session = Depends(get_db)        │
│ ):                                       │
└──────────────────────────────────────────┘
       │
       ├─ Extract query params
       ├─ Get user from session
       └─ Validate permissions
       │
       ↓

STEP 6: Backend builds database query
┌────────────────────────────────────────┐
│ query = db.query(Course)                │
│ if category:                           │
│     query = query.filter(              │
│         Course.category == category    │
│     )                                   │
│ courses = query.all()                  │
└────────────────────────────────────────┘
       │
       ↓ (SQLAlchemy ORM → SQL)

STEP 7: Database executes SQL
┌──────────────────────────────────────────────┐
│ SELECT * FROM courses                        │
│ WHERE category = 'Web Development'           │
│                                              │
│ Result: 2 rows                               │
│ - Python Fundamentals (id=1)                 │
│ - Web Development 101 (id=2)                 │
└──────────────────────────────────────────────┘
       │
       ↓

STEP 8: Backend enriches data
┌────────────────────────────────────────────────────┐
│ For each course:                                   │
│   - Count videos: SELECT COUNT(*) FROM videos     │
│   - Get rating: SELECT AVG(rating) FROM reviews   │
│   - Check purchase: SELECT * FROM orders          │
│   - Check cart: SELECT * FROM cart_items          │
└────────────────────────────────────────────────────┘
       │
       ↓

STEP 9: Backend formats response
┌────────────────────────────────────────────┐
│ [                                          │
│   CourseListItem(                          │
│     id=2,                                  │
│     title="Web Development 101",           │
│     price=99.99,                           │
│     rating=4.8,                            │
│     video_count=25,                        │
│     is_purchased=false,                    │
│     is_in_cart=false                       │
│   ),                                       │
│   ...                                      │
│ ]                                          │
└────────────────────────────────────────────┘
       │
       └─ Serialize to JSON via Pydantic
       │
       ↓ (Network - HTTP 200)

STEP 10: Frontend receives response
┌───────────────────────────────────┐
│ const data = await response.json() │
│ // Data is now an array of objects │
└───────────────────────────────────┘
       │
       ↓

STEP 11: Update React state
┌──────────────────────┐
│ setCourses(data)     │
│ setLoading(false)    │
└──────────────────────┘
       │
       ↓

STEP 12: React re-renders
┌─────────────────────────────────┐
│ return (                        │
│   <div>                         │
│     {courses.map(course =>      │
│       <CourseCard {...course} />│
│     )}                          │
│   </div>                        │
│ )                               │
└─────────────────────────────────┘
       │
       ↓

STEP 13: Browser displays UI
┌─────────────────────────────────┐
│   SkillForge Marketplace        │
│                                 │
│   ┌──────────────────────────┐  │
│   │ Web Development 101       │  │
│   │ $99.99 ⭐ 4.8          │  │
│   │ 📹 25 videos            │  │
│   │ [Add to Cart]            │  │
│   └──────────────────────────┘  │
└─────────────────────────────────┘
       │
       ↓

USER SEES MARKETPLACE WITH COURSES!
```

---

## 3. Data Structure Flow

```
┌─────────────────────────────────┐
│  Frontend React State           │
├─────────────────────────────────┤
│ courses: Course[] = [           │
│   {                             │
│     id: 1,                      │
│     title: string,              │
│     description: string,        │
│     price: number,              │
│     category: string,           │
│     rating: number,             │
│     video_count: number,        │
│     is_purchased: boolean,      │
│     is_in_cart: boolean         │
│   },                            │
│   ...                           │
│ ]                               │
│                                 │
│ loading: boolean = false        │
│ cartCount: number = 0           │
│ selectedCategory: string = ""   │
└─────────────────────────────────┘
       ↕ (fetch → JSON parse)
┌─────────────────────────────────┐
│  Backend Pydantic Schema        │
├─────────────────────────────────┤
│ class CourseListItem(BaseModel):│
│   id: int                       │
│   path: str                     │
│   title: str                    │
│   description: Optional[str]    │
│   category: Optional[str]       │
│   is_paid: bool                 │
│   price: Optional[float]        │
│   video_count: int = 0          │
│   is_purchased: bool = False    │
│   is_in_cart: bool = False      │
│   rating: Optional[float] = None│
│                                 │
│   class Config:                 │
│     from_attributes = True      │
└─────────────────────────────────┘
       ↕ (SQLAlchemy ORM → objects)
┌─────────────────────────────────┐
│  Database Model                 │
├─────────────────────────────────┤
│ class Course(Base):             │
│   id: int                       │
│   path: str                     │
│   title: str                    │
│   description: str              │
│   category: str                 │
│   is_paid: bool                 │
│   price: float                  │
│   created_at: datetime          │
│                                 │
│ class Video(Base):              │
│   id: int                       │
│   course_id: int (FK)           │
│   title: str                    │
│   duration: int                 │
│                                 │
│ class Review(Base):             │
│   id: int                       │
│   course_id: int (FK)           │
│   user_id: int (FK)             │
│   rating: float                 │
│                                 │
│ class CartItem(Base):           │
│   id: int                       │
│   user_id: int (FK)             │
│   course_id: int (FK)           │
│   price: float                  │
│   quantity: int                 │
└─────────────────────────────────┘
       ↕ (SQL queries)
┌─────────────────────────────────┐
│  Database Tables                │
├─────────────────────────────────┤
│ courses                         │
│ videos                          │
│ reviews                         │
│ cart_items                      │
│ orders                          │
│ users                           │
│ ... (40+ total tables)          │
└─────────────────────────────────┘
```

---

## 4. Component Rendering Flow

```
┌─────────────────────────────────────┐
│  MarketplacePage Component          │
├─────────────────────────────────────┤
│                                     │
│  1. Parse props & initialize state  │
│     - courses: []                   │
│     - loading: true                 │
│     - filters: { category: "" }     │
│                                     │
│  2. useEffect hook runs             │
│     - Calls fetchCourses()          │
│     - API request to backend        │
│     - Receives JSON                 │
│     - setCourses(data)              │
│     - Component re-renders          │
│                                     │
│  3. Conditional rendering           │
│     if (loading) show spinner       │
│     else if (courses.length === 0)  │
│       show "No courses"             │
│     else                            │
│       map courses → CourseCard      │
│                                     │
└─────────────────────────────────────┘
              ↓ renders
┌─────────────────────────────────────┐
│  <Layout>                           │
├─────────────────────────────────────┤
│  ┌─────────────────────────────────┐│
│  │ <Header>                        ││
│  │ - Title                         ││
│  │ - Search bar                    ││
│  │ - Category filters              ││
│  │ - Cart badge                    ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ <div className="grid">          ││
│  │   {courses.map(course =>        ││
│  │    <CourseCard                  ││
│  │      key={course.id}            ││
│  │      id={course.id}             ││
│  │      title={course.title}       ││
│  │      price={course.price}       ││
│  │      rating={course.rating}     ││
│  │      videoCount={...}           ││
│  │      onAddCart={addToCart}      ││
│  │    />                           ││
│  │   )}                            ││
│  │ </div>                          ││
│  └─────────────────────────────────┘│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ <CourseCard>                    ││
│  │ ├─ <h3>{title}</h3>             ││
│  │ ├─ <p>{description}</p>         ││
│  │ ├─ <div>category</div>          ││
│  │ ├─ <span>⭐ {rating}</span>     ││
│  │ ├─ <span>${price}</span>        ││
│  │ ├─ <span>📹 {videoCount}</span> ││
│  │ └─ <button onClick>             ││
│  │      {isPurchased ?              ││
│  │       "Already Purchased"        ││
│  │       : "Add to Cart"}           ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
              ↓ renders to
┌─────────────────────────────────────┐
│  HTML DOM                           │
├─────────────────────────────────────┤
│  <div id="__next">                  │
│    <nav>...</nav>                   │
│    <h1>Marketplace</h1>             │
│    <input placeholder="Search..." /> │
│    <div class="grid">               │
│      <div class="course-card">      │
│        <h3>Web Dev 101</h3>         │
│        <p>Master HTML...</p>        │
│        <span>Web Development</span> │
│        <span>⭐ 4.8</span>          │
│        <span>$99.99</span>          │
│        <span>📹 25 videos</span>    │
│        <button>Add to Cart</button> │
│      </div>                         │
│      <div class="course-card">      │
│        ...                          │
│      </div>                         │
│    </div>                           │
│  </div>                             │
└─────────────────────────────────────┘
              ↓ renders in
┌─────────────────────────────────────┐
│  BROWSER WINDOW                     │
├─────────────────────────────────────┤
│                                     │
│  SkillForge Marketplace             │
│  [Search...]         Cart (5)       │
│                                     │
│  [All] [Web Dev] [Data Sci]...      │
│                                     │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ Web Dev 101  │  │ Python Fund  │ │
│  │              │  │              │ │
│  │ Master HTML, │  │ Learn Python │ │
│  │ CSS, JS      │  │              │ │
│  │              │  │              │ │
│  │ Web Dev      │  │ Programming  │ │
│  │ ⭐ 4.8      │  │ ⭐ 4.5      │ │
│  │ $99.99       │  │ $49.99       │ │
│  │ 📹 25 videos │  │ 📹 12 videos │ │
│  │              │  │              │ │
│  │[Add to Cart] │  │[Add to Cart] │ │
│  └──────────────┘  └──────────────┘ │
│                                     │
│  [Load More...]                     │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Cart Operations Flow

```
┌────────────────────────────────────┐
│ User clicks [Add to Cart]          │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│ Frontend: addToCart(courseId)       │
│                                    │
│ await fetch(                       │
│   `/api/v1x/marketplace/cart/add`, │
│   {                                │
│     method: 'POST',                │
│     body: {course_id: 1}           │
│   }                                │
│ )                                  │
└────────────────────────────────────┘
              ↓ (HTTP POST)
┌────────────────────────────────────┐
│ Backend: add_to_cart()              │
│                                    │
│ @router.post("/cart/add")          │
│ def add_to_cart(item_data):        │
│   course = get_course(id)          │
│   existing = get_cart_item()       │
│   if existing:                     │
│     update quantity                │
│   else:                            │
│     insert new cart_item           │
│   db.commit()                      │
└────────────────────────────────────┘
              ↓ (SQL INSERT/UPDATE)
┌────────────────────────────────────┐
│ Database: cart_items table updated  │
│                                    │
│ INSERT INTO cart_items (           │
│   user_id, course_id, price, qty   │
│ ) VALUES (5, 1, 49.99, 1)          │
│                                    │
│ OR                                 │
│                                    │
│ UPDATE cart_items                  │
│ SET quantity = quantity + 1        │
│ WHERE user_id=5 AND course_id=1    │
└────────────────────────────────────┘
              ↓ (HTTP 200 response)
┌────────────────────────────────────┐
│ Frontend: Receive success response  │
│                                    │
│ if (response.ok) {                 │
│   fetchCourses()   // Refresh      │
│   fetchCartCount() // Update badge │
│   alert("Added!")                  │
│ }                                  │
└────────────────────────────────────┘
              ↓
┌────────────────────────────────────┐
│ UI Updates                         │
│                                    │
│ - Button changes to [In Cart ✓]    │
│ - Cart badge count increases       │
│ - Course card shows updated status │
└────────────────────────────────────┘
```

---

## 6. Authentication Flow

```
┌──────────────────────────────────┐
│ User Login (separate page)       │
├──────────────────────────────────┤
│ POST /api/v1x/auth/login         │
│ Body: {email, password}          │
│                                  │
│ Response: Sets cookie            │
│ Set-Cookie: session=abc123...    │
└──────────────────────────────────┘
              ↓
┌──────────────────────────────────┐
│ Browser stores session cookie    │
└──────────────────────────────────┘
              ↓
┌──────────────────────────────────┐
│ Frontend makes API requests      │
│ with credentials: 'include'      │
│                                  │
│ fetch(url, {                     │
│   credentials: 'include'         │
│ })                               │
│                                  │
│ Automatically includes cookie    │
└──────────────────────────────────┘
              ↓
┌──────────────────────────────────┐
│ Backend receives request with    │
│ Cookie header:                   │
│ Cookie: session=abc123...        │
│                                  │
│ Validates and gets current_user  │
│ from session                     │
└──────────────────────────────────┘
              ↓
┌──────────────────────────────────┐
│ Backend can now:                 │
│ - Know who the user is           │
│ - Check purchase history         │
│ - Check cart contents            │
│ - Return user-specific data      │
└──────────────────────────────────┘
```

---

## 7. Error Handling Flow

```
┌─────────────────────────────────┐
│ Frontend makes request          │
│ fetch(url)                      │
└─────────────────────────────────┘
              ↓
        ┌─────┴─────┐
        ↓           ↓
    ✅ OK         ❌ Error
    200 OK        404, 500
        ↓           ↓
    Response    Error handling
    received    in catch block
        ↓           ↓
    Parse      Show error to user
    JSON       console.error()
        ↓           ↓
    Set state  Retry logic
    Re-render  Fallback values
        ↓           ↓
    Show data  Show error message
```

---

**These diagrams show how courses and products flow through the entire system from database to user interface!**
