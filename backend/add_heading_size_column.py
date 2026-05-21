"""
Add heading_size column to resumes table
"""
from sqlalchemy import text
from app.core.db import engine

try:
    with engine.connect() as conn:
        # Try to add the column
        conn.execute(text("ALTER TABLE resumes ADD COLUMN heading_size INTEGER DEFAULT 14"))
        conn.commit()
        print("✅ Successfully added heading_size column to resumes table")
except Exception as e:
    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
        print("ℹ️  heading_size column already exists")
    else:
        print(f"❌ Error: {e}")
