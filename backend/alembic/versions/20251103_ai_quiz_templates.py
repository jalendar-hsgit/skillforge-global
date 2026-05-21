"""Add quiz templates and sessions

Revision ID: 20251103_ai_quiz_templates
Revises: 4fef0e1df469
Create Date: 2025-11-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '20251103_ai_quiz_templates'
down_revision = '4fef0e1df469'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'generated_quizzes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
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
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
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


def downgrade() -> None:
    op.drop_table('quiz_sessions')
    op.drop_table('generated_quizzes')
