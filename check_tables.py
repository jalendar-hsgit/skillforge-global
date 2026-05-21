#!/usr/bin/env python
"""Check if all models are registered in Base.metadata"""

# Import all models to register them
from app.core.db import Base, engine
from app.modelsx.resume import ResumeAchievement, Resume

# Now check
tables = sorted(Base.metadata.tables.keys())
print(f"Total tables registered: {len(tables)}")
print(f"resume_achievements exists: {'resume_achievements' in Base.metadata.tables}")
print(f"resumes exists: {'resumes' in Base.metadata.tables}")
print("\nAll tables:")
for table in tables:
    print(f"  - {table}")
