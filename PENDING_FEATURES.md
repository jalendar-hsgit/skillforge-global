# PENDING FEATURES - QUICK REFERENCE

**Updated**: January 1, 2026  
**Priority Guide**: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

---

## 🔴 CRITICAL FIXES (Do First)

### 1. Forum API Routes - 404 Error
**Problem**: `/api/v1x/forums/categories` returns 404
**Fix Location**: `backend/app/main.py`
**Action**: Register forum router properly
**Time**: 30 mins

### 2. Notification Routes - 404 Error  
**Problem**: Notifications API not responding
**Fix Location**: `backend/app/main.py`
**Action**: Check v1x notifications router
**Time**: 30 mins

### 3. Marketplace Routes - 404 Error
**Problem**: `/api/v1x/marketplace/products` fails
**Fix Location**: Check router registration
**Time**: 30 mins

---

## 🟠 HIGH PRIORITY (This Week)

### 4. Forum System Frontend
**Status**: Backend ready, frontend 50%
**Pages**: `/forums`, `/forums/create`, `/forums/[id]`
**Components Needed**:
- ForumCategoryList
- ThreadList
- ThreadDetail
- ReplyForm
**Time**: 6-8 hours

### 5. Social Features Integration
**Status**: Backend ready, frontend 40%
**Pages**: `/social`, `/social/following`, `/social/feed`
**Features Needed**:
- Follow/unfollow users
- Activity feed
- Solution sharing
**Time**: 8-10 hours

### 6. Coding Practice Testing
**Status**: API works (200), frontend exists
**Test Items**:
- Load challenges list
- Start a challenge
- Submit solution
- View results
**Time**: 2-3 hours testing

---

## 🟡 MEDIUM PRIORITY (Next Week)

### 7. Contest System
**Status**: 20% - Models ready
**Backend**: `backend/app/api/v1x/contests.py`
**Frontend**: `/contests`, `/contests/[id]`
**Features**:
- Contest creation (admin)
- Registration
- Leaderboard
- Prize distribution
**Time**: 10-15 hours

### 8. PWA Features
**Status**: 15% - Config exists
**Features Needed**:
- Service worker
- Offline mode
- Push notifications
- Install prompt
**Time**: 8-12 hours

### 9. Video Conferencing
**Status**: Not started
**For**: Mentor sessions
**Tech**: WebRTC or Twilio
**Features**:
- Video call
- Screen share
- Recording
**Time**: 12-15 hours

---

## 🟢 LOW PRIORITY (Later)

### 10. AI Hints System
**Status**: 10% - Schema ready
**Backend**: `backend/app/api/v1x/ai_hints.py`
**Features**:
- Contextual hints
- Adaptive suggestions
- Usage tracking
**Time**: 10-15 hours

### 11. GitHub Integration
**Status**: OAuth ready
**Features**:
- Portfolio sync
- Contribution display
- Project showcase
**Time**: 6-8 hours

### 12. Referral Program
**Status**: Schema ready
**Features**:
- Referral codes
- Reward system
- Tracking
**Time**: 4-6 hours

### 13. Certificate Generation
**Status**: Not started
**Features**:
- PDF certificates
- Path completion
- LinkedIn share
**Time**: 4-6 hours

### 14. Mobile App
**Status**: 0%
**Tech**: React Native
**Time**: 40+ hours

---

## 📊 FEATURE COMPLETION MATRIX

| Feature | Backend | Frontend | API Test | UI Test | Docs |
|---------|---------|----------|----------|---------|------|
| Forums | ✅ | 50% | ❌ | ❌ | ❌ |
| Social | ✅ | 40% | ❌ | ❌ | ❌ |
| Contests | ⚠️ | 20% | ❌ | ❌ | ❌ |
| Practice | ✅ | 80% | ✅ | ❌ | ❌ |
| Notifications | ⚠️ | 30% | ❌ | ❌ | ❌ |
| PWA | ⚠️ | 15% | ❌ | ❌ | ❌ |
| AI Hints | ❌ | 10% | ❌ | ❌ | ❌ |
| GitHub | ⚠️ | 10% | ❌ | ❌ | ❌ |
| Referral | ⚠️ | 10% | ❌ | ❌ | ❌ |
| Video Call | ❌ | ❌ | ❌ | ❌ | ❌ |
| Certificates | ❌ | ❌ | ❌ | ❌ | ❌ |
| Mobile | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 RECOMMENDED ORDER

### Session 1 (2-3 hours)
1. Fix forum API routes
2. Fix notification routes
3. Test all fixed endpoints

### Session 2 (4-6 hours)
1. Complete forum frontend
2. Test forum flow end-to-end

### Session 3 (4-6 hours)
1. Social features integration
2. Following system
3. Activity feed

### Session 4 (3-4 hours)
1. Test coding practice thoroughly
2. Fix any issues found

### Session 5 (6-8 hours)
1. Contest system
2. Basic functionality

### Session 6+ (Ongoing)
- PWA features
- Video conferencing
- AI hints
- Polish and testing

---

## 🔗 RELATED FILES

| Feature | Backend Files | Frontend Files |
|---------|---------------|----------------|
| Forums | `api/v1x/forums.py`, `modelsx/forums.py` | `pages/forums/`, `components/forum/` |
| Social | `api/v1x/social.py`, `modelsx/social.py` | `pages/social/`, `components/social/` |
| Contests | `api/v1x/contests.py`, `modelsx/contests.py` | `pages/contests/` |
| Practice | `api/v1x/coding_practice.py` | `pages/practice/` |
| Notifications | `api/v1x/notifications.py` | `pages/notifications/` |

---

## ⚡ QUICK WIN OPPORTUNITIES

These can be done in under 1 hour each:

1. **Add /health endpoint** - Simple status check
2. **Seed forum data** - Add demo categories/threads
3. **Seed contest data** - Add sample contest
4. **Fix 404 routes** - Register missing routers
5. **Add loading states** - Improve UX

---

*Reference this document when planning development sessions.*
