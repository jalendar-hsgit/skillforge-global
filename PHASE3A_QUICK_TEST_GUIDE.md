# Phase 3A: Quick Testing Reference

**Status:** ✅ All code written and deployed  
**Servers:** Backend on 8001, Frontend on 3001  
**Ready:** Yes - Manual testing can begin immediately

---

## 🚀 Start Services

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn app.main:app --reload --port 8001

# Terminal 2: Frontend  
npm run dev
# (Will start on 3001 if 3000 is taken)
```

**Verify:**
- Backend: http://localhost:8001/docs (Swagger UI)
- Frontend: http://localhost:3001 (should load home page)

---

## 👥 Test Accounts

### Mentors
- **Email:** `mentor.sarah@skillforge.com`
- **Password:** `mentor123`
- **Role:** MENTOR

Other mentors (also work):
- `mentor.david@skillforge.com` / `mentor123`
- `mentor.emily@skillforge.com` / `mentor123`
- `mentor.james@skillforge.com` / `mentor123`

### Admins
- **Email:** `admin@skillforge.com`
- **Password:** `admin123`
- **Role:** ADMIN

Superadmin:
- `superadmin@skillforge.com` / `admin123`

### Regular Users (Can upgrade to mentor)
- `john.doe@example.com` / `password123`
- `jane.smith@example.com` / `password123`
- etc.

---

## 📝 Test Scenario 1: Basic Upload

1. **Login as Mentor**
   ```
   Go to: http://localhost:3001/login
   Email: mentor.sarah@skillforge.com
   Pass: mentor123
   ```

2. **Navigate to Verification**
   ```
   Click: Mentor → Verification
   Or: http://localhost:3001/mentor/verification
   ```

3. **Upload Document**
   ```
   - Document Type: "Certification"
   - File: Create test PDF or JPG
   - Click: Upload Document
   ```

4. **Verify**
   ```
   ✅ Toast shows "Document uploaded successfully"
   ✅ Document appears in list with PENDING badge
   ✅ Stats show 1 pending
   ✅ File in: backend/app/data/mentor_documents/
   ```

---

## 📋 Test Scenario 2: Admin Approval

1. **Login as Admin**
   ```
   Go to: http://localhost:3001/login
   Email: admin@skillforge.com
   Pass: admin123
   ```

2. **Navigate to Verification**
   ```
   Click: Admin → Mentor Verification
   Or: http://localhost:3001/admin/mentor-verification
   ```

3. **View Pending**
   ```
   ✅ Should see mentor "Sarah Chen" with 1 pending document
   ✅ Document shows: filename, type, size, date
   ```

4. **Approve**
   ```
   - Click: "Approve" button
   - Modal appears
   - Type: "Excellent certifications!"
   - Click: "Approve Document"
   ```

5. **Verify**
   ```
   ✅ Toast shows "Document approved successfully"
   ✅ Document disappears from pending list
   ✅ Dashboard now shows "All Clear!"
   ```

6. **Mentor Verification**
   ```
   - Logout admin, login as mentor again
   - Go to verification page
   - Document now shows "APPROVED" badge
   ```

---

## ❌ Test Scenario 3: Admin Rejection

1. **Upload Another Document** (as mentor)
   ```
   - Go to /mentor/verification
   - Upload another file (e.g., degree, ID, license)
   ```

2. **Reject as Admin**
   ```
   - Logout, login as admin
   - Go to /admin/mentor-verification
   - Click: "Reject" on the document
   ```

3. **Provide Feedback**
   ```
   - Modal appears
   - Enter reason: "Image too blurry, please resubmit a clearer copy"
   - Click: "Reject Document"
   ```

4. **Verify**
   ```
   ✅ Toast shows "Document rejected successfully"
   ✅ Document removed from admin pending list
   ✅ Mentor logs in, sees REJECTED badge
   ✅ Rejection reason displayed below document
   ✅ Can delete and reupload
   ```

---

## 🔧 Test Scenario 4: File Validation

### Test 1: File Too Large
```
1. Try uploading file > 10MB
2. Expected: Error toast "File size must be less than 10MB"
3. File NOT added to list
```

### Test 2: Invalid File Type
```
1. Try uploading .exe, .zip, or .txt file
2. Expected: Error toast about invalid file type
3. File NOT added to list
```

### Test 3: Correct File Types
```
✅ PDF: Works
✅ JPG: Works
✅ PNG: Works
✅ DOC: Works
✅ DOCX: Works
```

### Test 4: Delete Pending Document
```
1. Upload a document (PENDING status)
2. Click trash icon on document
3. Confirm in modal
4. Document deleted immediately
5. File removed from disk
```

---

## 📊 Test Scenario 5: Stats & Counts

1. **Upload 3 Documents**
   ```
   1. First: PENDING (will approve)
   2. Second: PENDING (will reject)
   3. Third: PENDING (will leave)
   ```

2. **Check Mentor Stats**
   ```
   ✅ Total: 3
   ✅ Pending: 3
   ✅ Approved: 0
   ✅ Rejected: 0
   ```

3. **Admin Approves #1**
   ```
   ✅ Total: 3
   ✅ Pending: 2 (now shows)
   ✅ Approved: 1 (now shows)
   ✅ Rejected: 0
   ```

4. **Admin Rejects #2**
   ```
   ✅ Total: 3
   ✅ Pending: 1 (now shows)
   ✅ Approved: 1
   ✅ Rejected: 1 (now shows)
   ```

---

## 🔐 Test Scenario 6: Permissions

### Mentor Can't See Other Mentors' Docs
```
1. Mentor Sarah uploads document
2. Mentor David tries to delete Sarah's document
3. Expected: 404 Not Found or permission error
4. Access denied
```

### Admin Can See All
```
1. Multiple mentors upload documents
2. Admin sees ALL in /admin/mentor-verification
3. Can approve/reject any document
4. No restrictions
```

### Only Pending Can Be Deleted
```
1. Upload document (PENDING)
2. Can delete - trash icon available
3. Admin approves it
4. Trash icon disappears
5. Can't delete approved/rejected docs
```

---

## 🔍 Debugging Tips

### Backend Issues?
```bash
# Check logs
cd backend
python -m uvicorn app.main:app --reload

# Look for: "Mounted v1x router: ['mentor-documents']"

# Test endpoint directly
curl http://localhost:8001/api/v1x/mentor-documents/my-documents

# Check database tables
sqlite3 backend/app/data/skillforge.db ".tables" | grep mentor
```

### Frontend Issues?
```bash
# Check browser console: F12 → Console tab
# Look for any red errors

# Check network tab: F12 → Network tab
# Verify API calls are going to 8001

# Verify pages exist
http://localhost:3001/mentor/verification
http://localhost:3001/admin/mentor-verification

# Check Next.js build: npm run build
cd root && npm run build
```

### File Storage?
```bash
# Check uploaded files
ls backend/app/data/mentor_documents/

# Should see files like:
# 1705849200_certification.pdf
# 1705849300_id_scan.jpg
```

---

## 📈 Performance Tests (Optional)

### Single File Upload
- Expected: < 2 seconds
- Actual: _____ seconds

### List Documents  
- Expected: < 1 second
- Actual: _____ seconds

### Admin Pending List
- Expected: < 2 seconds
- Actual: _____ seconds

### Approve/Reject
- Expected: < 1 second
- Actual: _____ seconds

---

## ✅ Full Test Checklist

**Backend:**
- [ ] Models registered (214 tables)
- [ ] Router mounted ("Mounted v1x router: ['mentor-documents']")
- [ ] File upload endpoint accessible
- [ ] List documents endpoint accessible
- [ ] Admin pending endpoint accessible

**Frontend:**
- [ ] Mentor page loads
- [ ] Admin page loads
- [ ] File upload form visible
- [ ] Document type selector visible
- [ ] Drag-drop area visible

**Upload Flow:**
- [ ] Can select document type
- [ ] Can choose file
- [ ] Can upload file
- [ ] File appears in list
- [ ] Status is PENDING
- [ ] File stored on disk

**Admin Flow:**
- [ ] Can login as admin
- [ ] Can see pending mentors
- [ ] Can see pending documents
- [ ] Can approve with note
- [ ] Can reject with reason
- [ ] Status updates immediately

**Error Handling:**
- [ ] Large file rejected
- [ ] Invalid file type rejected
- [ ] Upload error shows toast
- [ ] Network error handled
- [ ] Permission error shown

**Permissions:**
- [ ] Mentor sees own documents
- [ ] Mentor can't delete approved
- [ ] Mentor can delete pending
- [ ] Admin sees all
- [ ] Mentor can't see other mentors

**Responsiveness:**
- [ ] Looks good on desktop
- [ ] Looks good on tablet
- [ ] Looks good on mobile
- [ ] Touch events work

---

## 🎯 Success Criteria

✅ **Implementation is successful if:**

1. Mentors can upload documents with validation
2. Files are stored securely on disk
3. Admins can see all pending verifications
4. Admins can approve with optional notes
5. Admins can reject with required reasons
6. Mentors see rejection feedback
7. All stats update in real-time
8. Permission checks prevent unauthorized access
9. Error messages are helpful
10. UI is responsive and intuitive

---

## 📞 Troubleshooting

**"404 Not Found" on API calls?**
- Check backend is running on 8001
- Check "Mounted v1x router: ['mentor-documents']" in logs
- Restart backend

**"Network Error" when uploading?**
- Check file size < 10MB
- Check file type is allowed
- Check backend is running
- Check CORS settings

**File upload hangs?**
- Check browser console for errors
- Check backend logs
- Try smaller file
- Restart frontend

**Permissions denied?**
- Check you're logged in
- Check user role (MENTOR or ADMIN)
- Check you own the document (mentor)
- Clear cookies and re-login

**Stats not updating?**
- Refresh page (Ctrl+R)
- Check API response
- Check browser console for errors

---

## 📚 Additional Resources

- API Documentation: `PHASE3A_MENTOR_VERIFICATION_COMPLETE.md`
- Implementation Details: `PHASE3A_IMPLEMENTATION_SUMMARY.md`
- Backend Code: `backend/app/api/v1x/mentor_documents.py`
- Frontend Code: `src/pages/mentor/verification.tsx` & `src/pages/admin/mentor-verification.tsx`
- API Integration: `src/lib/api/mentorVerificationApi.ts`

---

**Ready to Test? Start the servers and begin with Test Scenario 1! 🚀**
