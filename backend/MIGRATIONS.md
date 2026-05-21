# Database Migrations with Alembic

This document explains how to use Alembic for database schema migrations in SkillForge Global.

## Quick Start

### Create a new migration

After modifying models in `app/models` or `app/modelsx`:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations

```powershell
# Upgrade to latest
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1
```

### Check migration status

```powershell
# Show current revision
alembic current

# Show migration history
alembic history --verbose
```

## Important Notes

### Model Imports

The `alembic/env.py` file imports all models to ensure they're registered with SQLAlchemy's metadata. When adding new models:

1. Add the model file to `app/models` or `app/modelsx`
2. Update `alembic/env.py` to import the new model
3. Run `alembic revision --autogenerate`

### Database URL

Alembic reads the database URL from:
1. `DATABASE_URL` environment variable (via `app.core.config.settings`)
2. Falls back to `alembic.ini` if not set

### Migration Workflow

1. **Make model changes** in code
2. **Generate migration**: `alembic revision --autogenerate -m "message"`
3. **Review the migration** file in `alembic/versions/`
4. **Edit if needed** (Alembic doesn't catch everything)
5. **Test the migration**: `alembic upgrade head`
6. **Test the downgrade**: `alembic downgrade -1`
7. **Commit** the migration file to git

## Recent Changes

### Initial Migration (4fef0e1df469)

Created baseline migration capturing current schema state including:
- All user, auth, and learning models
- Mentor system (sessions, payouts, reviews)
- Subscription and payment models
- Resume builder with ATS scoring
- Job application tracker (`job_application_tracker` table)
- Hiring platform (`job_applications` table for HiringJobApplication)

Note: We renamed the hiring model class from `JobApplication` to `HiringJobApplication` to avoid conflicts, but kept the table name as `job_applications` for backwards compatibility.

## Common Issues

### "Target database is not up to date"

Run `alembic upgrade head` to apply pending migrations.

### "Can't locate revision"

Your database's `alembic_version` table may be out of sync. Use `alembic stamp head` to mark the current schema as up-to-date (be careful with this).

### Migration generates too many changes

This happens when models aren't imported in `env.py`. Ensure all models are explicitly imported.

### SQLite limitations

SQLite doesn't support many ALTER TABLE operations. Alembic will create new tables and copy data for complex changes. Test migrations carefully in SQLite dev environments.

## Production Deployment

1. **Backup database** before running migrations
2. Run migrations during maintenance window: `alembic upgrade head`
3. If migration fails, rollback: `alembic downgrade -1`
4. Keep migration files in version control
5. Test migrations on staging environment first

## References

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto-generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [SQLAlchemy Metadata](https://docs.sqlalchemy.org/en/20/core/metadata.html)
