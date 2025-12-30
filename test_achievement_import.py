#!/usr/bin/env python
"""Test if models import correctly"""
import sys
sys.path.insert(0, 'backend')

try:
    from app.modelsx.resume import ResumeAchievement
    print("✓ ResumeAchievement imported successfully")
    print(f"  Table name: {ResumeAchievement.__tablename__}")
except Exception as e:
    print(f"✗ Error importing Achievement: {e}")
    import traceback
    traceback.print_exc()

# Check Base metadata
try:
    from app.core.db import Base
    if 'resume_achievements' in Base.metadata.tables:
        print("✓ resume_achievements in Base.metadata")
    else:
        print("✗ resume_achievements NOT in Base.metadata")
        print(f"  Total tables: {len(Base.metadata.tables)}")
except Exception as e:
    print(f"✗ Error checking metadata: {e}")
