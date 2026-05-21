"""
Quick migration script to add missing Resume model columns to existing SQLite DB.
Run once to fix schema mismatch: python migrate_resume_schema.py
"""
import sqlite3
from pathlib import Path

# Columns that need to be added (from Resume model)
COLUMNS_TO_ADD = [
    ("photo_url", "TEXT"),
    ("font_family", "TEXT DEFAULT 'Roboto'"),
    ("color_theme", "TEXT DEFAULT 'blue'"),
    ("background_type", "TEXT DEFAULT 'none'"),
    ("picture_style", "TEXT DEFAULT 'circle'"),
    ("rating_style", "TEXT DEFAULT 'bars'"),
    ("layout", "TEXT DEFAULT 'single-column'"),
    ("accent_color", "TEXT DEFAULT '#2563eb'"),
    ("text_color", "TEXT DEFAULT '#000000'"),
    ("heading_color", "TEXT DEFAULT '#1f2937'"),
    ("line_spacing", "REAL DEFAULT 1.2"),
    ("font_size", "INTEGER DEFAULT 11"),
    ("show_icons", "INTEGER DEFAULT 1"),  # Boolean as INTEGER in SQLite
    ("sections_order", "TEXT"),  # JSON
    ("enabled_sections", "TEXT"),  # JSON
    ("custom_sections", "TEXT"),  # JSON
    ("max_pages", "INTEGER DEFAULT 10"),
    ("page_margins", "TEXT"),  # JSON
    ("page_size", "TEXT DEFAULT 'A4'"),
    ("ats_score", "REAL DEFAULT 0.0"),
    ("keywords", "TEXT"),  # JSON
    ("views", "INTEGER DEFAULT 0"),
    ("downloads", "INTEGER DEFAULT 0"),
    ("shares", "INTEGER DEFAULT 0"),
    ("is_public", "INTEGER DEFAULT 0"),  # Boolean
    ("version", "INTEGER DEFAULT 1"),
]

def migrate():
    db_path = Path(__file__).parent / "app" / "data" / "skillforge.db"
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    print(f"📦 Connecting to {db_path}")
    conn = sqlite3.connect(str(db_path), timeout=10)
    try:
        c = conn.cursor()
        
        # Get existing columns
        c.execute("PRAGMA table_info(resumes)")
        existing_cols = {row[1] for row in c.fetchall()}
        print(f"✅ Found {len(existing_cols)} existing columns")
        
        # Add missing columns
        added = 0
        for col_name, col_type in COLUMNS_TO_ADD:
            if col_name not in existing_cols:
                try:
                    sql = f"ALTER TABLE resumes ADD COLUMN {col_name} {col_type}"
                    print(f"  Adding {col_name} ({col_type})...", end=" ")
                    c.execute(sql)
                    print("✓")
                    added += 1
                except Exception as e:
                    print(f"✗ Error: {e}")
            else:
                print(f"  {col_name} already exists, skipping")
        
        conn.commit()
        print(f"\n✅ Migration complete! Added {added} columns.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
