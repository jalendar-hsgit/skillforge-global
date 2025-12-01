#!/usr/bin/env python3
"""
Initialize default platform settings in the database.
Run this after creating the platform_settings table.
"""
from app.core.db import SessionLocal
from app.modelsx.platform_settings import PlatformSetting
import json


def init_default_settings():
    """Create default platform settings if they don't exist"""
    db = SessionLocal()
    
    try:
        default_settings = [
            {
                "key": "platform_name",
                "value": "SkillForge Global",
                "value_type": "string",
                "description": "Platform display name"
            },
            {
                "key": "support_email",
                "value": "support@skillforge.com",
                "value_type": "string",
                "description": "Support contact email"
            },
            {
                "key": "allow_new_registrations",
                "value": "true",
                "value_type": "boolean",
                "description": "Allow new user signups"
            },
            {
                "key": "mentor_approval_required",
                "value": "true",
                "value_type": "boolean",
                "description": "Require admin approval for mentors"
            },
            {
                "key": "maintenance_mode",
                "value": "false",
                "value_type": "boolean",
                "description": "Platform maintenance mode"
            },
            {
                "key": "featured_courses",
                "value": json.dumps([]),
                "value_type": "json",
                "description": "List of featured course slugs"
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for setting_data in default_settings:
            existing = db.query(PlatformSetting).filter(
                PlatformSetting.key == setting_data["key"]
            ).first()
            
            if existing:
                print(f"⏭️  Setting '{setting_data['key']}' already exists, skipping")
                updated_count += 1
            else:
                setting = PlatformSetting(**setting_data)
                db.add(setting)
                print(f"✅ Created setting: {setting_data['key']} = {setting_data['value']}")
                created_count += 1
        
        db.commit()
        
        print(f"\n{'='*60}")
        print(f"Default Settings Initialization Complete")
        print(f"{'='*60}")
        print(f"Created: {created_count} new settings")
        print(f"Skipped: {updated_count} existing settings")
        print(f"\nYou can now use the admin settings page to configure these values.")
        
    except Exception as e:
        print(f"\n❌ Error initializing settings: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("Initializing Default Platform Settings")
    print("="*60)
    print()
    init_default_settings()
