# ISSUE 0002 — Resume Export (PDF / DOCX)

Priority: High

Goal:
Add a server-side export endpoint for resumes allowing users to download a PDF or DOCX representation of their resume based on available templates.

Endpoints:
- `POST /api/v1x/resumes/{resume_id}/export?format=pdf|docx`
  - Auth required
  - Returns 200 with `{"url": "/downloads/resume-<id>-<ts>.pdf"}` or 202 (processing) for async.

Implementation notes:
- Add `backend/app/services/export_service.py` to render HTML or use `wkhtmltopdf`, `WeasyPrint`, or `python-docx`.
- Consider async background task + storage (local / S3) for large exports.
- Add small UX on frontend: an "Export" button that triggers the endpoint and downloads the file.

Acceptance Criteria:
- Authenticated user can request export for their resume
- Export file contains resume fields and uses selected template
- Download works in browser and respects access control
