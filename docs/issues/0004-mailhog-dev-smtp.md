# ISSUE 0004 — Enable Mailhog / Local SMTP for Dev

Priority: Quick Win

Goal:
Allow local development to capture outgoing emails using Mailhog (or similar) without external SMTP credentials.

Implementation:
- Allow SMTP config with no auth when `SMTP_HOST` is `localhost` (default port 1025).
- Add `DEVELOPMENT_EMAIL_BACKEND=mailhog` or detect `SMTP_PORT==1025`.
- Document how to run Mailhog locally (download or Docker):
  - Docker: `docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog`
  - Visit http://127.0.0.1:8025 to see captured emails

Acceptance Criteria:
- When dev env points to Mailhog, welcome emails appear in Mailhog web UI
- No credentials needed in dev mode
- Dev docs updated with Mailhog instructions
