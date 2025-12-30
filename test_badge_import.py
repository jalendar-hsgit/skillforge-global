#!/usr/bin/env python
"""Check if Badge is properly imported"""
import sys
sys.path.insert(0, 'backend')

# Try importing in the same order as main.py
from app.core.db import Base, engine
print(f"Base.metadata tables after init: {len(Base.metadata.tables)}")

# Import models in order
from app.modelsx.badges import Badge
print(f"After importing Badge: {len(Base.metadata.tables)}")
print(f"'badges' in tables: {'badges' in Base.metadata.tables}")

from app.modelsx.contests import Contest
print(f"After importing Contest: {len(Base.metadata.tables)}")

# Check contests model for foreign keys
print("\nForeign keys in contests models:")
for table_name, table in Base.metadata.tables.items():
    if 'contest' in table_name.lower():
        for fk in table.foreign_keys:
            print(f"  {table_name}.{fk.parent.name} -> {fk.target_fullname}")
