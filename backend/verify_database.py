#!/usr/bin/env python
"""Database verification and audit script"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime

def verify_database():
    """Verify database integrity and structure"""
    # Find database file
    db_files = list(Path('.').glob('*.db')) + list(Path('.').glob('*.sqlite*')) + list(Path('app/data').glob('*.db'))
    if not db_files:
        print('❌ ERROR: No database file found')
        return False
    
    db_path = str(db_files[0])
    file_size = os.path.getsize(db_path) / 1024
    
    print('=' * 60)
    print('DATABASE VERIFICATION REPORT')
    print('=' * 60)
    print(f'Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Database: {db_path}')
    print(f'Size: {file_size:.2f} KB')
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [row[0] for row in cursor.fetchall()]
        print(f'✓ Total Tables: {len(all_tables)}')
        print()
        
        # Check key tables
        key_tables = {
            'users': ['id', 'email', 'password_hash', 'name', 'bio', 'avatar_url', 'role'],
            'courses': ['id', 'title', 'slug', 'description'],
            'mentors': ['id', 'user_id', 'bio', 'specialties'],
            'sessions': ['id', 'mentor_id', 'student_id', 'status'],
            'payments': ['id', 'user_id', 'amount', 'status'],
            'quizzes': ['id', 'course_id', 'title', 'questions']
        }
        
        print('KEY TABLES STATUS:')
        print('-' * 60)
        for table_name, expected_cols in key_tables.items():
            if table_name not in all_tables:
                print(f'✗ {table_name}: NOT FOUND')
                continue
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            
            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Check for expected columns
            missing = [col for col in expected_cols if col not in columns]
            status = '✓' if not missing else '⚠'
            
            print(f'{status} {table_name}: {row_count} rows, {len(columns)} columns')
            if missing:
                print(f'   Missing columns: {missing}')
            if row_count == 0:
                print(f'   Sample columns: {list(columns.keys())[:5]}')
        
        print()
        print('USER TABLE DETAILED CHECK:')
        print('-' * 60)
        cursor.execute("PRAGMA table_info(users)")
        user_cols = cursor.fetchall()
        print(f'Columns ({len(user_cols)}):')
        for col in user_cols:
            col_name, col_type, notnull, default, pk = col
            nullable = 'NULL' if not notnull else 'NOT NULL'
            print(f'  - {col_name}: {col_type} ({nullable})')
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f'\nTotal users: {user_count}')
        
        if user_count > 0:
            cursor.execute("SELECT id, email, name, role FROM users LIMIT 3")
            users = cursor.fetchall()
            print('\nSample users:')
            for user in users:
                print(f'  - ID {user[0]}: {user[1]} ({user[3]})')
        
        conn.close()
        print()
        print('=' * 60)
        print('✓ Database verification completed successfully')
        print('=' * 60)
        return True
        
    except Exception as e:
        print(f'❌ Database verification failed: {e}')
        return False

if __name__ == '__main__':
    verify_database()
