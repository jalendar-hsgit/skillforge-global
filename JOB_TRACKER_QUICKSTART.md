# Job Application Tracker - Quick Start Guide

## ⚡ 30-Second Setup

### 1. Start Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 2. Start Frontend
```bash
npm run dev
```

### 3. Access Application
```
http://localhost:3001/job-tracker
```

---

## 🎬 First Steps (2 minutes)

### Add Your First Job Application
1. Click **"Add Application"** button
2. Fill in:
   - Company Name: `Google`
   - Position: `Senior Software Engineer`
   - Status: `Applied`
   - Priority: `5` (Critical)
   - Salary: `$150k - $200k`
3. Click **"Create Application"**

### Update Status
1. Click on the application
2. Click **"Edit"**
3. Change status to `Screening`
4. Click **"Update Application"**

### View Statistics
1. Click **"Analytics"** in dashboard
2. See your response rate, salary insights, timeline

---

## 🗂️ File Structure

```
Backend:
├── app/modelsx/job_application.py       ← Database model
├── app/schemas/job_application.py        ← API validation
├── app/api/v1x/job_applications.py       ← Endpoints

Frontend:
├── src/pages/job-tracker/index.tsx       ← Dashboard
├── src/pages/job-tracker/add.tsx         ← Add/Edit form
├── src/pages/job-tracker/[id].tsx        ← Detail view
└── src/pages/job-tracker/analytics.tsx   ← Analytics
```

---

## 📋 API Quick Reference

### Create App
```bash
curl -X POST http://localhost:8001/api/v1x/job-applications \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Google",
    "position_title": "Engineer",
    "status": "applied",
    "priority": 5
  }'
```

### List Apps
```bash
curl http://localhost:8001/api/v1x/job-applications
```

### Get Stats
```bash
curl http://localhost:8001/api/v1x/job-applications/stats
```

### Update Status
```bash
curl -X PATCH http://localhost:8001/api/v1x/job-applications/{id} \
  -H "Content-Type: application/json" \
  -d '{"status": "interview"}'
```

---

## 💡 Pro Tips

1. **Priority 5** = Dream job (focus these)
2. **Follow-up Date** = 7 days after applying
3. **Add Skills** = Helps you track fit
4. **Add Contacts** = Don't lose recruiter info
5. **Schedule Interviews** = Track all details in one place

---

## ❓ FAQ

**Q: Where's my data stored?**  
A: SQLite database at `backend/app/data/skillforge.db`

**Q: Can I export my data?**  
A: Yes! Click application → Click "Export" button → Get CSV

**Q: How do I track follow-ups?**  
A: Set a follow-up date, and you'll see "⚠️ Overdue Follow-up" alert

**Q: Can I see analytics?**  
A: Yes! Navigate to `/job-tracker/analytics` for charts and insights

**Q: How many applications can I track?**  
A: Unlimited! The system handles hundreds of applications

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| 404 on API calls | Start backend: `uvicorn app.main:app --reload` |
| Can't create app | Check user is logged in |
| Data not showing | Refresh page or restart servers |
| Database error | Delete `skillforge.db` to reset (lose data!) |

---

## 📚 Learn More

- Full docs: See `JOB_TRACKER_GUIDE.md`
- API docs: Check endpoint descriptions in `job_applications.py`
- Schema: Review `job_application.py` for field details

---

**Ready to track your job search? 🚀**
