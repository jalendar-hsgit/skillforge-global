# 🗺️ Coding Practice - Complete Site Map & Flow

## 📍 URL Structure

```
/practice
├── index.tsx                          → Main hub (stats, challenges, simulators)
├── [slug].tsx                         → Individual challenge page
└── simulator/
    └── [type].tsx                     → Interactive simulator page
```

---

## 🔗 Navigation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN DASHBOARD                           │
│                  /dashboard                                  │
└──────────────┬──────────────────────────────────────────────┘
               │
               │ Click "Coding Practice" (banner/navbar/quick action)
               ↓
┌──────────────────────────────────────────────────────────────┐
│                   PRACTICE HUB                                │
│                  /practice                                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stats Overview                                        │   │
│  │ [Submissions] [Perfect] [Challenges] [Coins]         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Quick Actions                                         │   │
│  │ [Challenge] [Simulators] [Cloud Labs] [Live]         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ #challenges - Challenges Section                     │   │
│  │ Filters: [Category ▼] [Difficulty ▼]                 │   │
│  │ [Card] [Card] [Card] [Card] [Card] [Card]           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ #simulators - Code Simulators Section               │   │
│  │ [Editor] [Terminal] [SQL] [Cloud]                    │   │
│  │ [K8s] [Docker] [API] [Web]                          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ #cloud-labs - Cloud Labs Section                     │   │
│  │ [AWS] [Azure] [GCP]                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───┬────────────────────────────┬─────────────────────────────┘
    │                            │
    │ Click Challenge            │ Click Simulator
    ↓                            ↓
┌───────────────────┐    ┌──────────────────────────────────┐
│ CHALLENGE PAGE    │    │ SIMULATOR PAGE                    │
│ /practice/[slug]  │    │ /practice/simulator/[type]       │
│                   │    │                                   │
│ ┌──────┬────────┐ │    │ ┌────┬──────────────────────────┐│
│ │Desc  │ Editor │ │    │ │List│ Editor + Output          ││
│ │Hints │ Output │ │    │ │    │ [Run] [Reset] [Copy]     ││
│ │Disc  │ Tests  │ │    │ └────┴──────────────────────────┘│
│ └──────┴────────┘ │    │                                   │
│                   │    │ 8 Simulators:                     │
│ [Run] [Submit]    │    │ • Code Editor                     │
│                   │    │ • Terminal                        │
└───────────────────┘    │ • SQL Playground                  │
                         │ • Cloud Console                   │
                         │ • Kubernetes                      │
                         │ • Docker Lab                      │
                         │ • API Playground                  │
                         │ • Web Editor                      │
                         └──────────────────────────────────┘
```

---

## 🎯 Entry Points (How Users Find This)

### 1. From Dashboard
```
Dashboard → Coding Practice Banner → /practice
Dashboard → Quick Actions Card → /practice
```

### 2. From Navbar
```
Any Page → Navbar "Coding Practice" → /practice
```

### 3. Direct URL
```
Type URL: http://localhost:3000/practice
```

### 4. From Challenge List
```
/practice → Click Challenge Card → /practice/[slug]
```

### 5. From Simulator List
```
/practice → Click Simulator Card → /practice/simulator/[type]
```

---

## 📄 Page Breakdown

### Page 1: Practice Hub (`/practice`)
**Purpose:** Central hub for all coding practice activities

**Sections:**
1. **Stats Overview** (4 cards)
   - Total submissions
   - Perfect solutions
   - Challenges attempted
   - Coins earned

2. **Quick Actions** (4 buttons)
   - Start Challenge → Scrolls to #challenges
   - Code Simulators → Scrolls to #simulators
   - Cloud Labs → Scrolls to #cloud-labs
   - Live Sessions → Shows active count

3. **Challenges Section** (filterable grid)
   - Category filter (12 options)
   - Difficulty filter (5 levels)
   - Challenge cards (3 columns)
   - Each card links to `/practice/[slug]`

4. **Code Simulators Section** (8 cards)
   - 8 simulator types
   - Each links to `/practice/simulator/[type]`

5. **Cloud Labs Section** (3 cards)
   - AWS, Azure, GCP
   - Premium badges

6. **Recent Submissions** (list)
   - Last 10 submissions
   - Status, score, date

---

### Page 2: Challenge Detail (`/practice/[slug]`)
**Purpose:** Individual coding challenge with editor

**Layout:** Split View (1/3 - 2/3)

**Left Panel:**
- Tabs: Description | Hints | Discussion
- Problem statement
- Examples & constraints
- Tags
- Progressive hints
- Solution reveal

**Right Panel:**
- Language selector (8 languages)
- Code editor (full-height)
- Toolbar: [Reset] [Run Code] [Submit]
- Output panel
- Test case results

**Features:**
- Sticky header with challenge info
- Real-time code editing
- Mock test execution
- Visual test results (✅/❌)
- Hint system (costs coins)
- Solution reveal (costs 50 coins)

---

### Page 3: Simulator (`/practice/simulator/[type]`)
**Purpose:** Interactive coding environments

**Layout:** Sidebar + Full Editor

**Sidebar:**
- List of 8 simulators
- Click to switch
- Color-coded
- Language tags

**Main Area:**
- Simulator info banner
- Toolbar: [Copy] [Reset] [Run Code]
- Split view: Editor | Output
- Tips bar at bottom
- Fullscreen toggle

**Simulator Types:**
1. Code Editor (Python, JS, etc.)
2. Terminal (Bash, Shell)
3. SQL Playground (MySQL, PostgreSQL)
4. Cloud Console (AWS, Azure)
5. Kubernetes (kubectl, helm)
6. Docker Lab (docker, compose)
7. API Playground (REST, GraphQL)
8. Web Editor (HTML, CSS, JS)

---

## 🔄 State Management

### Practice Hub
```typescript
useState:
- stats: CodingStats | null
- challenges: Challenge[]
- recentSubmissions: Submission[]
- selectedCategory: string
- selectedDifficulty: string
- loading: boolean

useEffect:
- Fetch stats from API
- Fetch challenges from API
- Fetch recent submissions from API
```

### Challenge Page
```typescript
useState:
- challenge: Challenge | null
- code: string
- language: string
- output: string
- testResults: TestResult[]
- isRunning: boolean
- showHints: boolean
- showSolution: boolean
- activeTab: 'description' | 'hints' | 'discussion'
- executionTime: number
- passedTests: number

useEffect:
- Fetch challenge by slug
- Update code when language changes
```

### Simulator Page
```typescript
useState:
- selectedSimulator: Simulator
- code: string
- output: string
- isRunning: boolean
- isFullscreen: boolean

useEffect:
- Load default code template
- Update when simulator changes
```

---

## 🎨 Design System

### Colors
```css
Background:     #0a0e27 (darkNavy)
Primary:        #7c3aed (forgePurple)
Secondary:      #2563eb (neuralBlue)
Accent:         #0ea5e9 (techBlue)
Success:        #10b981 (green)
Warning:        #f59e0b (yellow)
Error:          #ef4444 (red)
Premium:        #f59e0b (yellow/gold)
```

### Gradients
```css
Purple/Blue:    from-forgePurple to-neuralBlue
Green/Teal:     from-green-500 to-teal-500
Blue/Indigo:    from-blue-500 to-indigo-500
Orange/Red:     from-orange-500 to-red-500
Yellow/Amber:   from-yellow-500 to-amber-500
```

### Spacing
```css
Card Padding:   1.5rem (24px)
Grid Gap:       1rem (16px)
Section Gap:    2rem (32px)
Border Radius:  0.5rem (8px) / 1rem (16px)
```

### Typography
```css
Heading 1:      2rem / font-bold
Heading 2:      1.5rem / font-bold
Heading 3:      1.25rem / font-semibold
Body:           1rem / font-normal
Small:          0.875rem / font-normal
Code:           Fira Code / Consolas / Monaco
```

---

## 🔌 API Integration Points

### Practice Hub
```typescript
GET /api/v1x/coding-practice/my-stats
→ Returns user stats

GET /api/v1x/coding-practice/challenges?limit=20
→ Returns challenge list

GET /api/v1x/coding-practice/challenges?category=X&difficulty=Y
→ Filtered challenges

GET /api/v1x/coding-practice/my-submissions?limit=10
→ Recent submissions
```

### Challenge Page
```typescript
GET /api/v1x/coding-practice/challenges/{slug}
→ Returns challenge details

POST /api/v1x/coding-practice/challenges/{id}/submit
→ Submit solution for grading

GET /api/v1x/coding-practice/challenges/{id}/hints
→ Get progressive hints
```

### Simulator Page
```typescript
// Currently mock execution
// Future: Real code execution service
POST /api/v1x/coding-practice/execute
→ Execute code in sandbox
```

---

## 🎮 User Interactions

### Challenge Page Interactions
1. **Select Language** → Updates code template
2. **Edit Code** → Saves to state
3. **Run Code** → Executes tests, shows results
4. **Submit Code** → Sends to API, records submission
5. **View Hints** → Reveals hint one by one
6. **Reveal Solution** → Costs 50 coins, shows answer
7. **Switch Tab** → Changes left panel content
8. **Reset Code** → Restores starter template

### Simulator Page Interactions
1. **Select Simulator** → Switches environment
2. **Edit Code** → Updates editor
3. **Run Code** → Executes in sandbox
4. **Reset** → Restores template
5. **Copy** → Copies code to clipboard
6. **Fullscreen** → Hides sidebar, maximizes editor
7. **Switch Language** → Updates template

---

## 📊 Data Flow

```
User Action → State Update → API Call → Backend Processing → Response → UI Update

Example: Submit Challenge
1. User clicks "Submit"
2. isRunning = true
3. POST /api/v1x/coding-practice/challenges/{id}/submit
4. Backend: Execute code, grade, save submission
5. Response: { score: 85, coins_earned: 10, status: 'success' }
6. Update UI: Show results, update stats
7. isRunning = false
```

---

## 🎯 Success Metrics

### Track These:
- Challenge start rate (clicks / views)
- Challenge completion rate (submits / starts)
- Perfect solution rate (100% scores / submits)
- Simulator usage (sessions / views)
- Time on page (engagement)
- Return rate (repeat visits)
- Premium conversions (upgrades from simulator)

---

## 🚀 Future Enhancements

### Phase 2
- [ ] Real code execution (Judge0, Piston)
- [ ] Monaco Editor integration
- [ ] Split panel resizing
- [ ] Code diff viewer
- [ ] Submission history modal

### Phase 3
- [ ] Live leaderboard
- [ ] Social sharing
- [ ] Code review system
- [ ] Team competitions
- [ ] Custom challenge creation

### Phase 4
- [ ] AI-powered hints
- [ ] Video explanations
- [ ] Interview prep mode
- [ ] Company-specific tracks
- [ ] Certification system

---

## ✅ Completion Checklist

- [✅] Practice hub page created
- [✅] Challenge detail page created
- [✅] Simulator page created
- [✅] Navigation links added
- [✅] Dashboard integration complete
- [✅] Filters implemented
- [✅] Mock data working
- [✅] Responsive design
- [✅] Documentation complete
- [ ] Backend API connected
- [ ] Real code execution
- [ ] Production deployment

---

**Status:** ✅ Frontend Complete & Ready for Testing  
**Next:** Connect to backend APIs and add real code execution  
**Test:** `npm run dev` → Visit `http://localhost:3000/practice`
