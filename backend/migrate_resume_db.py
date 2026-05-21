"""
Database Migration Script - Add New Fields to Resume Table
Non-destructive: Only adds columns, doesn't drop or remove data
Idempotent: Safe to run multiple times
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = "backend/app/data/skillforge.db"

def migrate_resume_table():
    """
    Add new columns to resumes table:
    - extra_content (TEXT)
    - style_settings_updated_at (DateTime)
    - style_settings_history (JSON)
    
    Non-destructive: Only adds missing columns
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(resumes)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"📊 Existing columns in resumes table: {len(existing_columns)}")
        print(f"   Columns: {sorted(existing_columns)}\n")
        
        # Track changes
        added_columns = []
        
        # 1. Add extra_content (TEXT)
        if 'extra_content' not in existing_columns:
            print("⏳ Adding column: extra_content...")
            cursor.execute("""
                ALTER TABLE resumes 
                ADD COLUMN extra_content TEXT
            """)
            added_columns.append('extra_content')
            print("   ✅ Added extra_content column\n")
        else:
            print("⏭️  Column 'extra_content' already exists\n")
        
        # 2. Add style_settings_updated_at (DateTime as TEXT for SQLite)
        if 'style_settings_updated_at' not in existing_columns:
            print("⏳ Adding column: style_settings_updated_at...")
            cursor.execute("""
                ALTER TABLE resumes 
                ADD COLUMN style_settings_updated_at DATETIME 
                DEFAULT CURRENT_TIMESTAMP
            """)
            added_columns.append('style_settings_updated_at')
            print("   ✅ Added style_settings_updated_at column\n")
        else:
            print("⏭️  Column 'style_settings_updated_at' already exists\n")
        
        # 3. Add style_settings_history (JSON as TEXT)
        if 'style_settings_history' not in existing_columns:
            print("⏳ Adding column: style_settings_history...")
            cursor.execute("""
                ALTER TABLE resumes 
                ADD COLUMN style_settings_history JSON
            """)
            added_columns.append('style_settings_history')
            print("   ✅ Added style_settings_history column\n")
        else:
            print("⏭️  Column 'style_settings_history' already exists\n")
        
        # Commit changes
        conn.commit()
        
        # Verify changes
        cursor.execute("PRAGMA table_info(resumes)")
        updated_columns = {row[1] for row in cursor.fetchall()}
        
        print(f"✅ Migration complete!")
        print(f"   Total columns now: {len(updated_columns)}")
        print(f"   Columns added: {added_columns if added_columns else 'None (already exist)'}\n")
        
        # Count existing resumes
        cursor.execute("SELECT COUNT(*) FROM resumes")
        resume_count = cursor.fetchone()[0]
        print(f"📊 Database status:")
        print(f"   Existing resumes: {resume_count}")
        print(f"   Data preserved: ✅ Yes (non-destructive migration)\n")
        
        conn.close()
        return True, added_columns
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"⏭️  Columns already exist - migration skipped")
            return True, []
        else:
            print(f"❌ Error during migration: {e}")
            return False, []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, []

def create_resume_audit_table():
    """
    Create audit table for tracking all style setting changes
    Non-destructive: Only creates if doesn't exist
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='resume_style_audit'
        """)
        
        if cursor.fetchone():
            print("⏭️  Audit table 'resume_style_audit' already exists\n")
            conn.close()
            return True
        
        print("⏳ Creating audit table: resume_style_audit...")
        cursor.execute("""
            CREATE TABLE resume_style_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX idx_resume_style_audit_resume 
            ON resume_style_audit(resume_id)
        """)
        
        cursor.execute("""
            CREATE INDEX idx_resume_style_audit_user 
            ON resume_style_audit(user_id)
        """)
        
        conn.commit()
        conn.close()
        
        print("   ✅ Created resume_style_audit table with indexes\n")
        return True
        
    except Exception as e:
        print(f"❌ Error creating audit table: {e}")
        return False

def verify_migration():
    """
    Verify all changes were applied correctly
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check resumes table
        print("🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(resumes)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_columns = {
            'extra_content': 'TEXT',
            'style_settings_updated_at': 'DATETIME',
            'style_settings_history': 'JSON'
        }
        
        all_present = True
        for col, col_type in required_columns.items():
            if col in columns:
                print(f"   ✅ {col} ({columns[col]})")
            else:
                print(f"   ❌ {col} - MISSING")
                all_present = False
        
        # Check audit table
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='resume_style_audit'
        """)
        audit_exists = cursor.fetchone() is not None
        print(f"   {'✅' if audit_exists else '❌'} resume_style_audit table")
        
        conn.close()
        
        if all_present and audit_exists:
            print("\n✅ Migration verification: SUCCESS\n")
            return True
        else:
            print("\n❌ Migration verification: INCOMPLETE\n")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📦 Resume Table Migration - Non-Destructive")
    print("=" * 60)
    print()
    
    # Step 1: Migrate resume table
    success, added = migrate_resume_table()
    
    if not success:
        print("❌ Migration failed!")
        exit(1)
    
    # Step 2: Create audit table
    success = create_resume_audit_table()
    
    if not success:
        print("⚠️  Audit table creation failed (non-critical)")
    
    # Step 3: Verify
    if verify_migration():
        print("🎉 All migrations completed successfully!")
        print("\nNew fields available:")
        print("  • extra_content: For additional resume content")
        print("  • style_settings_updated_at: Tracks when styles were last updated")
        print("  • style_settings_history: JSON history of all style changes")
        print("\nAudit table created for tracking all changes")
    else:
        print("⚠️  Some migrations may not have completed")
