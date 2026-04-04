"""add_agentic_form_fields

Revision ID: 38c208b7772f
Revises: 816e439b8f0f
Create Date: 2026-02-14 22:42:11.893117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38c208b7772f'
down_revision: Union[str, None] = '816e439b8f0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add agentic form columns
    op.add_column('forms', sa.Column('system_prompt', sa.Text(), server_default='', nullable=False))
    op.add_column('forms', sa.Column('fields_schema', sa.JSON(), server_default='[]', nullable=False))
    # Make form_version_id nullable (batch mode for SQLite compat)
    with op.batch_alter_table('respondent_sessions') as batch_op:
        batch_op.alter_column('form_version_id',
                   existing_type=sa.VARCHAR(length=36),
                   nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('respondent_sessions') as batch_op:
        batch_op.alter_column('form_version_id',
                   existing_type=sa.VARCHAR(length=36),
                   nullable=False)
    op.drop_column('forms', 'fields_schema')
    op.drop_column('forms', 'system_prompt')
