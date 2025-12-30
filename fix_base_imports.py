#!/usr/bin/env python
"""Fix all modelsx files that use declarative_base()"""
import re
import os

files_to_fix = [
    'backend/app/modelsx/search.py',
    'backend/app/modelsx/activity.py',
    'backend/app/modelsx/teams.py',
    'backend/app/modelsx/resume_analytics.py',
    'backend/app/modelsx/referral.py',
    'backend/app/modelsx/recommendations.py',
    'backend/app/modelsx/marketplace.py',
    'backend/app/modelsx/interview.py',
    'backend/app/modelsx/forums.py',
]

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        continue
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if it has the problem
    if 'declarative_base()' in content and 'from app.core.db import Base' not in content:
        print(f"Fixing {filepath}...")
        
        # Replace the import section
        new_content = re.sub(
            r'from sqlalchemy\.ext\.declarative import declarative_base\n\nBase = declarative_base\(\)',
            'from app.core.db import Base',
            content
        )
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        print(f"  ✓ Fixed")
    else:
        print(f"✓ Already fixed or not applicable: {filepath}")

print("\nAll files processed!")
