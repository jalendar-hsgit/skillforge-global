#!/usr/bin/env python3
"""
Command-line utility to manage platform settings.
Usage:
    python manage_settings.py list                    # List all settings
    python manage_settings.py get <key>               # Get a specific setting
    python manage_settings.py set <key> <value>       # Set a setting value
    python manage_settings.py delete <key>            # Delete a setting
"""
import sys
import json
from app.core.db import SessionLocal
from app.modelsx.platform_settings import PlatformSetting


def list_settings():
    """List all settings"""
    db = SessionLocal()
    try:
        settings = db.query(PlatformSetting).order_by(PlatformSetting.key).all()
        
        if not settings:
            print("No settings found.")
            return
        
        print(f"\n{'='*80}")
        print("Platform Settings")
        print(f"{'='*80}")
        print(f"{'Key':<30} {'Type':<12} {'Value':<30}")
        print(f"{'-'*80}")
        
        for setting in settings:
            value = setting.get_value()
            if setting.value_type == "json":
                value_str = json.dumps(value)[:27] + "..." if len(json.dumps(value)) > 30 else json.dumps(value)
            else:
                value_str = str(value)[:30]
            
            print(f"{setting.key:<30} {setting.value_type:<12} {value_str:<30}")
        
        print(f"{'='*80}\n")
        
    finally:
        db.close()


def get_setting(key: str):
    """Get a specific setting"""
    db = SessionLocal()
    try:
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        
        if not setting:
            print(f"❌ Setting '{key}' not found.")
            return
        
        value = setting.get_value()
        
        print(f"\n{'='*60}")
        print(f"Setting: {key}")
        print(f"{'='*60}")
        print(f"Type:        {setting.value_type}")
        print(f"Value:       {value}")
        print(f"Description: {setting.description or 'N/A'}")
        print(f"Updated:     {setting.updated_at}")
        print(f"{'='*60}\n")
        
    finally:
        db.close()


def set_setting(key: str, value: str):
    """Set a setting value"""
    db = SessionLocal()
    try:
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        
        if not setting:
            print(f"❌ Setting '{key}' not found. Available settings:")
            list_settings()
            return
        
        # Convert value based on type
        if setting.value_type == "boolean":
            encoded = "true" if value.lower() in ["true", "1", "yes", "on"] else "false"
        elif setting.value_type == "json":
            try:
                # Validate JSON
                json.loads(value)
                encoded = value
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON value: {value}")
                return
        else:
            encoded = value
        
        old_value = setting.get_value()
        setting.value = encoded
        db.commit()
        
        print(f"\n✅ Updated setting '{key}'")
        print(f"   Old value: {old_value}")
        print(f"   New value: {setting.get_value()}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def delete_setting(key: str):
    """Delete a setting"""
    db = SessionLocal()
    try:
        setting = db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        
        if not setting:
            print(f"❌ Setting '{key}' not found.")
            return
        
        confirm = input(f"⚠️  Delete setting '{key}' (value: {setting.get_value()})? [y/N]: ")
        
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
        
        db.delete(setting)
        db.commit()
        
        print(f"✅ Deleted setting '{key}'\n")
        
    finally:
        db.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_settings()
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python manage_settings.py get <key>")
            sys.exit(1)
        get_setting(sys.argv[2])
    
    elif command == "set":
        if len(sys.argv) < 4:
            print("Usage: python manage_settings.py set <key> <value>")
            sys.exit(1)
        set_setting(sys.argv[2], sys.argv[3])
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Usage: python manage_settings.py delete <key>")
            sys.exit(1)
        delete_setting(sys.argv[2])
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
