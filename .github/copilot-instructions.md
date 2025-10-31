## Goal

Help AI contributors get productive quickly in this repository by summarizing the architecture, dev/run commands, project-specific patterns, and concrete file examples to inspect and modify.

## Quick start (what to run locally)

- Frontend (Next.js):
  - npm run dev (from repository root) — uses `package.json` scripts.
  - The frontend reads API base from `NEXT_PUBLIC_API_BASE`; default in code is `http://localhost:8001` (see `src/lib/api.ts`).

- Backend (FastAPI):
  - Install: `pip install -r backend/requirements.txt` (see `backend/requirements.txt`).
  - Run dev server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001` — backend app entrypoint is `backend/app/main.py`.

## High-level architecture

- Monorepo with two main runtimes:
  - Frontend: Next.js app under `src/` (pages, components, hooks, lib). Key file: `src/lib/api.ts` defines API base.
  - Backend: FastAPI app under `backend/app/` (routers in `api/v1`, optional `api/v1x` for DB-backed routes). Entry: `backend/app/main.py`.
- Data flow: frontend calls backend REST endpoints (default base http://localhost:8001). Backend v1 uses JSON files (under `backend/app/data/`) for some resources; `v1x` modules optionally provide DB-backed implementations.

## Important files & patterns (inspect these first)

- `backend/app/main.py` — app bootstrap, CORS config, and router mounting. Note it calls `Base.metadata.create_all(...)` (no migration system present).
- `backend/app/core/config.py` — settings via pydantic settings; includes DATABASE_URL, JWT_SECRET, FRONTEND_ORIGIN.
- `backend/app/api/v1/*.py` — primary HTTP routers (examples: `auth.py`, `courses.py`). `auth.py` sets/reads cookie named `token` for auth; `courses.py` edits `backend/app/data/courses.json` and requires an `ADMIN_KEY` header.
- `backend/app/models/` and `backend/app/modelsx/` — older (models) vs newer DB-backed models (`modelsx` used by `v1x`).
- `backend/app/schemas/` — pydantic shapes for request/response models.
- `src/lib/api.ts` — frontend helper for GET/POST; shows expected API base and simple error throwing.
- `src/pages/` and `src/components/` — where to change UI and routing. Example dynamic page: `src/pages/paths/[slug].tsx`.

## Project-specific conventions / gotchas

- Two API families coexist: `v1` (file-backed, stable) and `v1x` (optional DB-backed). `main.py` attempts to import `v1x` modules and will silently skip them if they fail to import — look for `backend/app/api/v1x` when adding DB features.
- Course content in `v1` is stored as JSON at `backend/app/data/courses.json`. Modifying courses for production-like behaviour may require converting to `v1x` DB-backed routes.
- `courses.py` expects an admin header `X-Admin-Key` checked against `settings.ADMIN_KEY` — `ADMIN_KEY` is not defined in `core/config.py` by default, so set via environment if you plan to use the protected routes.
- Auth uses JWT stored in an HTTP-only cookie named `token`. See `backend/app/api/v1/auth.py` for login/signup/me flows.
- DB handling: the app uses SQLAlchemy and calls `Base.metadata.create_all(...)` at startup — there is no Alembic migrations out-of-the-box.

## How to extend the backend safely

- To add a new endpoint:
  - Create `backend/app/api/v1/<feature>.py` with an `APIRouter(prefix="/<prefix>")` and pydantic models in `backend/app/schemas`.
  - The router will be included by `main.py` if you import it in `backend/app/main.py` (most existing modules are already imported there) or follow the existing pattern used for `auth`, `courses`, etc.
- When introducing DB-backed replacements, add them to `backend/app/api/v1x/` and `main.py` will include them automatically if importable.

## Example quick references

- Frontend API call helper: `src/lib/api.ts` — uses `NEXT_PUBLIC_API_BASE || "http://localhost:8001"`.
- Health check: `GET /healthz` (defined in `backend/app/main.py`).
- Auth routes: `POST /api/v1/auth/login`, `POST /api/v1/auth/signup`, `GET /api/v1/auth/me` (see `backend/app/api/v1/auth.py`).

## What an AI should do first when changing code

1. Run the frontend dev server and the backend dev server locally to exercise the code paths you plan to change.
2. Inspect the corresponding router in `backend/app/api/v1/` and the matching schema in `backend/app/schemas/` before edits.
3. If you touch data files (e.g., `courses.json`), note concurrency caveats — v1 edits are file writes.
4. If adding persistent models, prefer `modelsx` + `api/v1x` pattern so the app can optionally enable DB-backed routes.

## Where to look for more context

- `backend/requirements.txt` — runtime deps for backend.
- `package.json` — frontend scripts (`dev`, `build`, `start`, `lint`).
- `backend/app/data/` — CSV/JSON fixtures used by v1 routers.

If any section above is unclear or you'd like the doc to include command snippets for Windows PowerShell, CI notes, or example PR message templates, tell me which part to expand and I'll update the file.
