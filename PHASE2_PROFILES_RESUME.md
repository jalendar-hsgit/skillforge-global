# PHASE 2: USER PROFILES & RESUME - IMPLEMENTATION GUIDES

**Timeline**: Parallel with Mentor Features (Week 2)  
**Total Duration**: 12 hours combined

---

## 📌 GUIDE 1: USER PROFILES (6 hours)

### Overview
Build complete user profile system for students

### Feature 1: Profile Page (3 hours)
**File**: `src/pages/profile/index.tsx` (NEW)

**What to Include**:
```tsx
// Profile page structure
- Header section
  ├─ Avatar/profile picture
  ├─ Username & title
  ├─ Bio section
  ├─ Skills tags
  └─ Edit button

- Stats section
  ├─ Sessions completed
  ├─ Courses enrolled
  ├─ Total learning hours
  └─ Achievements

- Recent activity
  ├─ Recent sessions
  ├─ Recent certifications
  └─ Timeline view

- Public profile link
  └─ Share button
```

**Backend Endpoints Needed**:
```
GET /api/v1x/users/profile
GET /api/v1x/users/{id}/public-profile
GET /api/v1x/users/stats
```

**Tasks**:
```
BACKEND (1 hour):
- [ ] GET /api/v1x/users/profile - Load user data
- [ ] GET /api/v1x/users/stats - Load stats
- [ ] GET /api/v1x/users/{id}/public-profile - Public view

FRONTEND (2 hours):
- [ ] Create profile page layout
- [ ] Fetch & display user data
- [ ] Calculate stats
- [ ] Add edit button
- [ ] Make responsive
- [ ] Error handling
```

### Feature 2: Settings Page (2 hours)
**File**: `src/pages/profile/settings.tsx` (NEW)

**Sections**:
```
Account Settings
├─ Email (change, verify)
├─ Password change
├─ Two-factor auth
└─ Account deletion

Privacy Settings
├─ Profile visibility
├─ Show/hide stats
├─ Notification preferences
└─ Data export

Learning Preferences
├─ Learning goals
├─ Preferred languages
├─ Difficulty level
└─ Newsletter subscription

Notifications
├─ Email notifications
├─ In-app notifications
├─ SMS notifications (optional)
└─ Notification frequency
```

**Tasks**:
```
BACKEND (1 hour):
- [ ] PATCH /api/v1x/users/profile
- [ ] PATCH /api/v1x/users/settings
- [ ] PATCH /api/v1x/users/notifications
- [ ] POST /api/v1x/users/password-change

FRONTEND (1 hour):
- [ ] Create settings form
- [ ] Form validation
- [ ] Success/error notifications
- [ ] Confirmation modals (for sensitive actions)
```

### Feature 3: Learning Dashboard (1 hour)
**File**: `src/pages/profile/learning.tsx` (NEW)

**Content**:
```
- Learning progress
  ├─ Courses in progress
  ├─ Completion percentage
  ├─ Time spent
  └─ Estimated time remaining

- Certificates
  ├─ Completed certificates
  ├─ Certificate display
  └─ Download option

- Recommendations
  ├─ Next courses
  ├─ Trending skills
  └─ Personalized paths
```

---

## 📌 GUIDE 2: RESUME ENHANCEMENTS (6 hours)

### Feature 1: Enhanced Editor (3 hours)
**File**: `src/pages/resumes/[id]/edit.tsx` (ENHANCE existing)

**Improvements to Add**:
```
Rich Text Editor
├─ Bold, italic, underline
├─ Bullet points
├─ Link insertion
├─ Auto-formatting
└─ Word count

AI Suggestions Button
├─ "Improve this" on each field
├─ Rewrite suggestions
├─ Grammar check
├─ Action verb suggestions
└─ Metrics suggestions

Section Management
├─ Add new sections
├─ Reorder sections (drag-drop)
├─ Delete sections
└─ Show/hide sections

Live Preview
├─ Side-by-side view
├─ Mobile preview
├─ PDF preview
└─ Auto-update preview
```

**Tasks**:
```
FRONTEND (3 hours):
- [ ] Install rich text editor (react-quill or slate)
- [ ] Add "Improve with AI" button
- [ ] Implement section drag-drop
- [ ] Add live preview toggle
- [ ] Add word count
- [ ] Add auto-save indicator
- [ ] Mobile-friendly rich text
```

### Feature 2: ATS Score Improvements Page (2 hours)
**File**: `src/pages/resumes/[id]/ats-score.tsx` (ENHANCE existing)

**Current Status**: Backend done, frontend needs work

**What to Add**:
```
ATS Score Display
├─ Overall score (0-100)
├─ Score breakdown by section
├─ Improvement suggestions
└─ Priority levels

Line-by-line Analysis
├─ Which lines hurt score
├─ Why they're problems
├─ Suggested fixes
└─ Before/after preview

Format Issues
├─ File format compatibility
├─ Font/styling issues
├─ White space analysis
└─ Readability score

Improvement Tips
├─ High-impact changes first
├─ Quick wins
├─ Estimated score increase
└─ How-to implement each
```

**Tasks**:
```
FRONTEND (2 hours):
- [ ] Display score with progress bar
- [ ] Show breakdown by section
- [ ] Highlight problematic areas
- [ ] Implement improvement suggestions
- [ ] Add "Apply suggestion" button
- [ ] Track score before/after
```

### Feature 3: Resume Sharing (1 hour)
**File**: `src/pages/resumes/[id]/share.tsx` (NEW)

**Features**:
```
Share Methods
├─ Copy public link
├─ Email resume
├─ Download as PDF
└─ QR code

Access Control
├─ View only / Download
├─ Expiration date
├─ Password protected
└─ Track views

Share History
├─ Who viewed
├─ When viewed
├─ From where
└─ Actions taken
```

**Tasks**:
```
BACKEND (30 min):
- [ ] POST /api/v1x/resumes/{id}/share
- [ ] GET /api/v1x/resumes/{id}/share-history
- [ ] PATCH /api/v1x/resumes/{id}/share-settings

FRONTEND (30 min):
- [ ] Share modal
- [ ] Link copy button
- [ ] QR code generation
- [ ] View history display
```

---

## 🗂️ FILE STRUCTURE FOR PHASE 2

```
NEW FILES:
src/pages/profile/
├─ index.tsx (Profile page)
├─ settings.tsx (Settings)
├─ learning.tsx (Learning dashboard)
└─ layout.tsx (Profile layout)

src/pages/resumes/[id]/
├─ share.tsx (NEW: Share page)
└─ edit.tsx (ENHANCE: Add features)

src/components/
├─ ProfileCard.tsx
├─ SettingsForm.tsx
├─ RichTextEditor.tsx
├─ ATSScoreChart.tsx
└─ ShareModal.tsx
```

---

## 💻 COMPONENT EXAMPLES

### Rich Text Editor Component
```tsx
// src/components/RichTextEditor.tsx
import ReactQuill from 'react-quill'

export default function RichTextEditor({ value, onChange }) {
  const modules = {
    toolbar: [
      ['bold', 'italic', 'underline'],
      ['bullet'],
      ['link']
    ]
  }
  
  return (
    <div>
      <ReactQuill 
        value={value} 
        onChange={onChange}
        modules={modules}
        theme="snow"
      />
      <div className="text-sm text-gray-400 mt-2">
        {value.length} characters
      </div>
    </div>
  )
}
```

### ATS Score Display
```tsx
// Component to show score with breakdown
<div className="space-y-4">
  <div>
    <div className="flex justify-between mb-2">
      <span>Overall Score</span>
      <span className="text-2xl font-bold">{score}/100</span>
    </div>
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div 
        className="bg-green-500 h-2 rounded-full" 
        style={{width: `${score}%`}}
      />
    </div>
  </div>
  
  {breakdown.map(item => (
    <div key={item.name} className="flex justify-between">
      <span>{item.name}</span>
      <span>{item.score}%</span>
    </div>
  ))}
</div>
```

---

## 🧪 TESTING CHECKLIST

### User Profiles
- [ ] Profile page loads user data
- [ ] Stats calculate correctly
- [ ] Avatar displays
- [ ] Settings form submits
- [ ] Password change works
- [ ] Notification preferences save
- [ ] Mobile responsive
- [ ] Can access own profile
- [ ] Can view other public profiles
- [ ] Privacy settings respected

### Resume Enhancements
- [ ] Rich text editor renders
- [ ] Can bold/italic text
- [ ] Can add bullets
- [ ] Links insert correctly
- [ ] ATS score displays
- [ ] Suggestions show
- [ ] Can apply suggestions
- [ ] Score updates after changes
- [ ] Share link works
- [ ] View history tracks correctly

---

## ⏱️ TIME BREAKDOWN

| Component | Hours | Status |
|-----------|-------|--------|
| Profile Page | 3 | ⏳ |
| Settings Page | 2 | ⏳ |
| Learning Dashboard | 1 | ⏳ |
| Resume Editor | 3 | ⏳ |
| ATS Improvements | 2 | ⏳ |
| Resume Sharing | 1 | ⏳ |
| **TOTAL** | **12** | |

---

## 🚀 QUICK START

### Day 1: User Profiles (6 hours)
```
Hour 1-3: Profile page + settings backend
Hour 3-6: Settings UI + learning dashboard
```

### Day 2: Resume (6 hours)
```
Hour 1-2: Install rich text editor
Hour 2-4: Enhanced editor UI
Hour 4-5: ATS improvements display
Hour 5-6: Share functionality
```

---

## 📚 DEPENDENCIES

### Libraries to Install
```bash
npm install react-quill react-rich-text-editor
npm install qrcode.react (for QR codes)
npm install date-fns (for date formatting)
```

### Backend Endpoints (Summary)
```
Profile:
GET  /api/v1x/users/profile
PATCH /api/v1x/users/profile
GET  /api/v1x/users/stats

Settings:
PATCH /api/v1x/users/settings
POST  /api/v1x/users/password-change

Resume:
POST  /api/v1x/resumes/{id}/share
GET   /api/v1x/resumes/{id}/share-history
```

---

**Phase**: 2 of 4  
**Total Hours**: 12 (6 profiles + 6 resume)  
**Start**: Same week as mentor features  
**Parallel Work**: Can do with mentor features

✅ **READY TO IMPLEMENT!**
