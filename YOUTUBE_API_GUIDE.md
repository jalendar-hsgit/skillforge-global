# 🎬 YouTube API Integration Guide

## Current Status: ✅ CONFIGURED and READY

Your YouTube API key is configured and working! Here's what you need to know:

---

## 📊 Current Data Source

### **Static JSON (Currently Active)**
- **Location:** `backend/app/data/courses.json`
- **Endpoint:** `GET /api/v1/courses?path={slug}`
- **Source:** Manually curated video IDs
- **Pros:** Fast, predictable, no API quota usage
- **Cons:** Must manually update, not dynamic

### **YouTube API (Available but Not Active)**
- **Service:** `backend/app/api/v1x/youtube_sync.py`
- **Status:** ✅ Configured, ✅ API key working
- **Endpoints:** `/api/v1x/youtube/*`
- **Pros:** Dynamic, auto-fetches latest videos
- **Cons:** Uses API quota (10,000 units/day free)

---

## 🔧 Available YouTube Endpoints

### 1. Health Check
```bash
GET http://127.0.0.1:8001/api/v1x/youtube/health

Response:
{
  "ok": true,
  "has_key": true  # ✅ Your API key is working!
}
```

### 2. Preview Videos (Search Without Saving)
```bash
POST http://127.0.0.1:8001/api/v1x/youtube/preview

Body:
{
  "course_id": 1,
  "query": "python programming",
  "max_results": 10
}

Response:
{
  "ok": true,
  "count": 3,
  "items": [
    {
      "youtube_id": "_uQrJ0TkZlc",
      "title": "Python Full Course for Beginners",
      "duration_sec": 22447,
      "channel": "Programming with Mosh",
      "thumbnail": "https://i.ytimg.com/vi/_uQrJ0TkZlc/hqdefault.jpg"
    }
  ]
}
```

### 3. Sync Videos to Database
```bash
POST http://127.0.0.1:8001/api/v1x/youtube/sync

Body:
{
  "course_id": 1,
  "query": "python machine learning",
  "max_results": 25
}

Response:
{
  "ok": true,
  "inserted": 25,
  "skipped": 0
}
```

---

## 🚀 How to Use YouTube API

### Option 1: Use the Sync Script (Recommended)

I created a script for you: `backend/sync_youtube_courses.py`

**Run it:**
```powershell
cd backend
python sync_youtube_courses.py
```

**What it does:**
- Searches YouTube for videos on each learning path
- Previews videos before saving (safe mode)
- Syncs videos to database (when you confirm)
- Automatically categorizes by path (python-ai, fullstack, etc.)

**Example output:**
```
🎬 YouTube Course Sync Tool
✅ YouTube API key detected

Choose mode:
  1. Preview (see videos without saving)
  2. Sync (save to database)
Choice: 1

📺 PREVIEW MODE

🔹 Path: python-ai
  Search: 'python programming tutorial' (max 10)
  Found: 10 videos
    1. Python Full Course for Beginners
       Duration: 22447s | Channel: Programming with Mosh
    2. Learn Python - Full Course
       Duration: 15000s | Channel: freeCodeCamp
    ... and 8 more
```

---

### Option 2: Test Manually in PowerShell

**Preview videos:**
```powershell
$body = @{
    course_id = 1
    query = "python tutorial"
    max_results = 5
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://127.0.0.1:8001/api/v1x/youtube/preview" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | 
  Select-Object -ExpandProperty Content | 
  ConvertFrom-Json
```

**Sync to database:**
```powershell
$body = @{
    course_id = 1
    query = "python machine learning"
    max_results = 10
} | ConvertTo-Json

Invoke-WebRequest `
  -Uri "http://127.0.0.1:8001/api/v1x/youtube/sync" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | 
  Select-Object -ExpandProperty Content | 
  ConvertFrom-Json
```

---

### Option 3: Create Admin UI Page

Create `src/pages/admin/youtube.tsx`:

```tsx
import { useState } from 'react'
import Layout from '@/components/Layout'

export default function YouTubeSyncPage() {
  const [query, setQuery] = useState('')
  const [maxResults, setMaxResults] = useState(10)
  const [results, setResults] = useState<any[]>([])

  const preview = async () => {
    const response = await fetch('/api/v1x/youtube/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        course_id: 1,
        query,
        max_results: maxResults
      })
    })
    const data = await response.json()
    setResults(data.items || [])
  }

  const sync = async () => {
    const response = await fetch('/api/v1x/youtube/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        course_id: 1,
        query,
        max_results: maxResults
      })
    })
    const data = await response.json()
    alert(`Synced ${data.inserted} videos!`)
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto p-8">
        <h1 className="text-2xl font-bold mb-6">YouTube Video Sync</h1>
        
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Search query (e.g., python tutorial)"
            className="w-full p-3 border rounded"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          
          <input
            type="number"
            placeholder="Max results"
            className="w-full p-3 border rounded"
            value={maxResults}
            onChange={(e) => setMaxResults(Number(e.target.value))}
          />
          
          <div className="flex gap-3">
            <button onClick={preview} className="px-6 py-3 bg-blue-500 text-white rounded">
              Preview
            </button>
            <button onClick={sync} className="px-6 py-3 bg-green-500 text-white rounded">
              Sync to Database
            </button>
          </div>
        </div>

        <div className="mt-8 space-y-4">
          {results.map((video) => (
            <div key={video.youtube_id} className="border p-4 rounded">
              <img src={video.thumbnail} alt={video.title} className="w-full h-40 object-cover rounded mb-2" />
              <h3 className="font-semibold">{video.title}</h3>
              <p className="text-sm text-gray-600">
                {video.channel} · {Math.floor(video.duration_sec / 60)} mins
              </p>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
```

---

## 📈 YouTube API Quota

**Free Tier:** 10,000 units/day

**Cost per operation:**
- Search: 100 units
- Video details: 1 unit

**Example:**
- 1 search (10 videos) = 100 + 10 = 110 units
- You can do ~90 searches per day (900 videos)

---

## 🔄 Migration Strategy

### Phase 1: Keep Static JSON (Current)
- ✅ Fast and reliable
- ✅ No API quota usage
- ❌ Manual updates required

### Phase 2: Hybrid Approach
- Use YouTube API to populate `courses.json`
- Run sync script weekly/monthly
- Best of both worlds

### Phase 3: Fully Dynamic
- Switch to database-backed courses (`v1x`)
- Fetch from YouTube in real-time
- Auto-update course catalog

---

## 🛠️ Code Changes Needed for Full YouTube Integration

### 1. Switch to Database-Backed Courses

**Current:** `GET /api/v1/courses` (JSON file)  
**Switch to:** `GET /api/v1x/courses-db/{path}/videos` (Database)

Update `src/pages/paths/[slug].tsx`:
```tsx
// Change from:
fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/v1/courses?path=${slug}`)

// To:
fetch(`/api/v1x/courses-db/${slug}/videos`)
```

### 2. Add Auto-Sync Background Job

Create `backend/app/tasks/auto_sync.py`:
```python
# Sync YouTube videos daily
import schedule
from app.services.yt_sync import search_videos, save_videos

def sync_all_paths():
    paths = ['python-ai', 'fullstack', 'aws-devops', 'cybersec', 'flutter']
    for path in paths:
        videos = search_videos(f"{path} tutorial", max_results=20)
        save_videos(db, course_id, videos)

schedule.every().day.at("02:00").do(sync_all_paths)
```

---

## ✅ Summary

| Feature | Status | Notes |
|---------|--------|-------|
| YouTube API Key | ✅ Configured | Working, tested |
| Static JSON courses | ✅ Active | Current data source |
| YouTube Sync Service | ✅ Ready | Available but not used |
| Sync Script | ✅ Created | Run `backend/sync_youtube_courses.py` |
| Database Integration | ⚠️ Optional | Switch to `v1x/courses-db` |

---

## 🎯 Recommendation

**For now, keep using static JSON** because:
1. It's fast and reliable
2. You control the quality of videos
3. No API quota concerns
4. Your current 170 videos are well-curated

**Use YouTube API for:**
1. Expanding course catalog
2. Finding new trending videos
3. Auto-refreshing outdated content
4. A/B testing different video sources

**Run the sync script** to populate more videos:
```powershell
cd backend
python sync_youtube_courses.py
```

Choose "Preview" mode first to see what videos it finds!

---

## 🔗 Next Steps

1. **Test the sync script:**
   ```powershell
   cd backend
   python sync_youtube_courses.py
   ```

2. **Review previewed videos** - Make sure quality is good

3. **Decide on strategy:**
   - Keep static JSON + manually curate
   - Use YouTube API to find videos, then manually approve
   - Fully automate with YouTube API

Let me know which approach you prefer!
