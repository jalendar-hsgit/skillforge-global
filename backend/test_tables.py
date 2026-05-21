from app.core.db import Base
from app.modelsx.resume import ResumeAchievement, Resume

tables = sorted(Base.metadata.tables.keys())
output = f"""Total tables: {len(tables)}
resume_achievements: {'resume_achievements' in Base.metadata.tables}
"""

if 'resume_achievements' not in Base.metadata.tables:
    output += f"ERROR: resume_achievements table not registered!\nFirst 20 tables: {tables[:20]}"
else:
    output += "✓ resume_achievements is registered"

print(output)
with open('test_output.txt', 'w') as f:
    f.write(output)

