#!/usr/bin/env python
"""
DATABASE BACKUP AND VERSIONING SYSTEM
=====================================
Implements automated backups and tracking of database states
"""
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
import json

class DatabaseManager:
    """Manage database backups, versioning, and integrity checks"""
    
    def __init__(self, db_path="app/data/skillforge.db"):
        self.db_path = Path(db_path)
        self.backup_dir = self.db_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        self.log_file = self.db_path.parent / "database_log.json"
    
    def create_backup(self, description=""):
        """Create timestamped backup of database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"skillforge_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(self.db_path, backup_path)
            
            # Log the backup
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "backup_file": backup_name,
                "original_size_kb": self.db_path.stat().st_size / 1024,
                "description": description,
                "type": "backup"
            }
            self._log_event(log_entry)
            
            print(f"✓ Backup created: {backup_name}")
            return backup_path
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def get_schema_info(self):
        """Get complete database schema information"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        schema_info = {}
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = []
            for col in cursor.fetchall():
                col_info = col[:5]  # Get first 5 elements
                col_name, col_type, notnull, default, pk = col_info
                columns.append({
                    "name": col_name,
                    "type": col_type,
                    "nullable": not notnull,
                    "primary_key": bool(pk)
                })
            
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            
            schema_info[table] = {
                "columns": columns,
                "row_count": row_count
            }
        
        conn.close()
        return schema_info
    
    def verify_integrity(self):
        """Verify database integrity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Run PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            conn.close()
            
            if result == "ok":
                print("✓ Database integrity check passed")
                return True
            else:
                print(f"❌ Database integrity issue: {result}")
                return False
        except Exception as e:
            print(f"❌ Integrity check failed: {e}")
            return False
    
    def get_table_stats(self):
        """Get statistics for all tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0
        
        conn.close()
        return stats
    
    def _log_event(self, event):
        """Log database events to JSON file"""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(event)
            
            # Keep only last 100 logs
            logs = logs[-100:]
            
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not log event: {e}")
    
    def print_status(self):
        """Print comprehensive database status"""
        print("=" * 80)
        print("DATABASE STATUS REPORT")
        print("=" * 80)
        print(f"Database: {self.db_path}")
        print(f"Size: {self.db_path.stat().st_size / 1024:.2f} KB")
        print(f"Last Modified: {datetime.fromtimestamp(self.db_path.stat().st_mtime)}")
        print()
        
        # Schema info
        schema = self.get_schema_info()
        print(f"Tables: {len(schema)}")
        
        # Count tables with data
        tables_with_data = [t for t, info in schema.items() if info['row_count'] > 0]
        print(f"Tables with data: {len(tables_with_data)}")
        print()
        
        # Key tables
        print("KEY TABLES STATUS:")
        print("-" * 80)
        key_tables = ['users', 'mentors', 'courses', 'quizzes', 'mentor_sessions']
        for table in key_tables:
            if table in schema:
                count = schema[table]['row_count']
                cols = len(schema[table]['columns'])
                status = "✓" if count > 0 else "○"
                print(f"{status} {table:<30} {count:>6} rows  {cols:>3} columns")
            else:
                print(f"✗ {table:<30} NOT FOUND")
        
        # Tables with data
        print("\nTABLES WITH DATA:")
        print("-" * 80)
        for table in sorted(tables_with_data):
            count = schema[table]['row_count']
            print(f"  • {table:<40} {count:>6} rows")
        
        print()
        print("=" * 80)

if __name__ == "__main__":
    mgr = DatabaseManager()
    
    # Verify integrity
    mgr.verify_integrity()
    print()
    
    # Print status
    mgr.print_status()
    print()
    
    # Create backup
    mgr.create_backup("Pre-development snapshot")
