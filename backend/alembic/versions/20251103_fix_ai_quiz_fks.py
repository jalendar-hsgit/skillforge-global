"""
Fix ForeignKey targets for AI quiz tables to reference 'user.id'.
Recreate tables and copy data if present.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, select

revision = '20251103_fix_ai_quiz_fks'
down_revision = '20251103_merge_heads'
branch_labels = None
depends_on = None

def upgrade():
    # Drop old tables (if exist)
    op.drop_table('quiz_sessions')
    op.drop_table('generated_quizzes')

    # Recreate with correct FKs
    op.create_table(
        'generated_quizzes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, index=True),
        sa.Column('topic', sa.String(length=255), nullable=False, index=True),
        sa.Column('difficulty', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('questions', sa.JSON(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('adaptive_context', sa.JSON(), nullable=True),
        sa.Column('times_taken', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('best_score', sa.Integer(), nullable=True),
        sa.Column('best_score_total', sa.Integer(), nullable=True),
        sa.Column('last_taken_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'quiz_sessions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False, index=True),
        sa.Column('quiz_id', sa.Integer(), sa.ForeignKey('generated_quizzes.id'), nullable=True, index=True),
        sa.Column('quiz_path', sa.String(length=255), nullable=True, index=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_questions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('passed', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('answers', sa.JSON(), nullable=True),
        sa.Column('difficulty_progression', sa.JSON(), nullable=True),
        sa.Column('avg_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    )

def downgrade():
    op.drop_table('quiz_sessions')
    op.drop_table('generated_quizzes')
