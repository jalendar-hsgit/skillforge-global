"""merge heads

Revision ID: 20251103_merge_heads
Revises: 20251103_ai_quiz_templates, class_rename_note
Create Date: 2025-11-03 10:45:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251103_merge_heads'
down_revision = ('20251103_ai_quiz_templates', 'class_rename_note')
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
