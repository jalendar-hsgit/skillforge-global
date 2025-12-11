# ISSUE 0001 — Next.js Dev Server Port Binding Investigation

Priority: High (blocks frontend integration testing)

Summary:
The Next.js dev server starts and prints "Ready" but the process does not appear to bind to the expected port (3003). HTTP requests to `127.0.0.1:3003` return connection refused (WinError 10061).

Reproduction Steps:
1. From project root run:

```powershell
$env:PORT=3003; $env:NEXT_PUBLIC_API_BASE="http://127.0.0.1:8001"; npm run dev
```
2. Observe log output — server prints Ready.
3. Curl `http://127.0.0.1:3003/healthz` or `http://127.0.0.1:3003` and receive connection refused.

Investigation Checklist:
- [ ] Check Next.js startup logs, look for errors before/after "Ready".
- [ ] Confirm node process PID and `netstat -ano | findstr ":3003"`.
- [ ] Check Windows firewall rules and test different ports (3000/3004).
- [ ] Verify `next.config.mjs` patches (watchpack filter) do not alter the server port binding.
- [ ] Try `npm run build` + `npm start` and see if production build binds.
- [ ] Try running inside WSL to see if Windows networking is the issue.
- [ ] Collect `npm --version`, `node --version`, `next --version`.

Acceptance Criteria:
- Root cause identified and documented.
- If code fix needed, implement and add tests.
- Dev server binds to port and proxy smoke tests succeed.
