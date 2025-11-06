"""Document the class rename without schema change

Revision ID: class_rename_note
Revises: 4fef0e1df469
Create Date: 2025-11-02 19:50:00.000000

Note: This is a documentation-only migration. We renamed the Python class
`JobApplication` in app.modelsx.hiring to `HiringJobApplication` to avoid
a SQLAlchemy registry conflict with the job tracker's JobApplication class.
The database table name remains `job_applications` (no schema change needed).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'class_rename_note'
down_revision: Union[str, Sequence[str], None] = '4fef0e1df469'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No schema changes - class rename only."""
    # No operations needed
    pass


def downgrade() -> None:
    """No schema changes - class rename only."""
    # No operations needed
    pass
