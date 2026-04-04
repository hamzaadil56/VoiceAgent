"""initial schema

Revision ID: 816e439b8f0f
Revises: 
Create Date: 2026-02-14 21:26:17.266864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '816e439b8f0f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables ordered by dependency graph to avoid FK issues on PostgreSQL.
    # Circular dep between forms <-> form_versions resolved by deferring the FK.

    # --- Independent tables ---
    op.create_table('organizations',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('admin_users',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_email'), 'admin_users', ['email'], unique=True)

    # --- forms first (without published_version_id FK, added after form_versions) ---
    op.create_table('forms',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('org_id', sa.String(length=36), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('slug', sa.String(length=255), nullable=False),
    sa.Column('mode', sa.String(length=32), nullable=False),
    sa.Column('persona', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('published_version_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forms_org_id'), 'forms', ['org_id'], unique=False)
    op.create_index(op.f('ix_forms_slug'), 'forms', ['slug'], unique=True)

    # --- form_versions (depends on forms) ---
    op.create_table('form_versions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_id', sa.String(length=36), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('start_node_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('form_id', 'version_number', name='uq_form_version_number')
    )
    op.create_index(op.f('ix_form_versions_form_id'), 'form_versions', ['form_id'], unique=False)

    # Now add the deferred FK from forms -> form_versions
    op.create_foreign_key('fk_forms_published_version', 'forms', 'form_versions',
                          ['published_version_id'], ['id'])

    # --- Tables depending on organizations + admin_users ---
    op.create_table('memberships',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('org_id', sa.String(length=36), nullable=False),
    sa.Column('admin_user_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id', 'admin_user_id', name='uq_membership_org_user')
    )
    op.create_index(op.f('ix_memberships_admin_user_id'), 'memberships', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_memberships_org_id'), 'memberships', ['org_id'], unique=False)
    op.create_table('audit_logs',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('org_id', sa.String(length=36), nullable=True),
    sa.Column('actor_admin_user_id', sa.String(length=36), nullable=True),
    sa.Column('action', sa.String(length=128), nullable=False),
    sa.Column('resource_type', sa.String(length=64), nullable=False),
    sa.Column('resource_id', sa.String(length=36), nullable=False),
    sa.Column('details_json', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['actor_admin_user_id'], ['admin_users.id'], ),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # --- Tables depending on forms ---
    op.create_table('exports',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('file_path', sa.String(length=512), nullable=True),
    sa.Column('row_count', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exports_form_id'), 'exports', ['form_id'], unique=False)

    # --- Tables depending on form_versions ---
    op.create_table('form_graph_nodes',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_version_id', sa.String(length=36), nullable=False),
    sa.Column('key', sa.String(length=128), nullable=False),
    sa.Column('prompt', sa.Text(), nullable=False),
    sa.Column('node_type', sa.String(length=32), nullable=False),
    sa.Column('required', sa.Boolean(), nullable=False),
    sa.Column('validation_json', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_version_id'], ['form_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_form_graph_nodes_form_version_id'), 'form_graph_nodes', ['form_version_id'], unique=False)
    op.create_index(op.f('ix_form_graph_nodes_key'), 'form_graph_nodes', ['key'], unique=False)

    # --- respondent_sessions (depends on forms + form_versions) ---
    op.create_table('respondent_sessions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_id', sa.String(length=36), nullable=False),
    sa.Column('form_version_id', sa.String(length=36), nullable=False),
    sa.Column('channel', sa.String(length=32), nullable=False),
    sa.Column('locale', sa.String(length=16), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('current_node_id', sa.String(length=36), nullable=True),
    sa.Column('metadata_json', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.ForeignKeyConstraint(['form_version_id'], ['form_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_respondent_sessions_form_id'), 'respondent_sessions', ['form_id'], unique=False)
    op.create_index(op.f('ix_respondent_sessions_form_version_id'), 'respondent_sessions', ['form_version_id'], unique=False)

    # --- Leaf tables ---
    op.create_table('answers',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('session_id', sa.String(length=36), nullable=False),
    sa.Column('form_id', sa.String(length=36), nullable=False),
    sa.Column('field_key', sa.String(length=128), nullable=False),
    sa.Column('value_text', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['respondent_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answers_field_key'), 'answers', ['field_key'], unique=False)
    op.create_index(op.f('ix_answers_form_id'), 'answers', ['form_id'], unique=False)
    op.create_index(op.f('ix_answers_session_id'), 'answers', ['session_id'], unique=False)
    op.create_table('form_graph_edges',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_version_id', sa.String(length=36), nullable=False),
    sa.Column('from_node_id', sa.String(length=36), nullable=False),
    sa.Column('to_node_id', sa.String(length=36), nullable=True),
    sa.Column('condition_json', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_version_id'], ['form_versions.id'], ),
    sa.ForeignKeyConstraint(['from_node_id'], ['form_graph_nodes.id'], ),
    sa.ForeignKeyConstraint(['to_node_id'], ['form_graph_nodes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_form_graph_edges_form_version_id'), 'form_graph_edges', ['form_version_id'], unique=False)
    op.create_index(op.f('ix_form_graph_edges_from_node_id'), 'form_graph_edges', ['from_node_id'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('session_id', sa.String(length=36), nullable=False),
    sa.Column('role', sa.String(length=16), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['respondent_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_session_id'), 'messages', ['session_id'], unique=False)
    op.create_table('submissions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('form_id', sa.String(length=36), nullable=False),
    sa.Column('session_id', sa.String(length=36), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('completed_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    sa.ForeignKeyConstraint(['session_id'], ['respondent_sessions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_submissions_form_id'), 'submissions', ['form_id'], unique=False)
    op.create_index(op.f('ix_submissions_session_id'), 'submissions', ['session_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_submissions_session_id'), table_name='submissions')
    op.drop_index(op.f('ix_submissions_form_id'), table_name='submissions')
    op.drop_table('submissions')
    op.drop_index(op.f('ix_messages_session_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_form_graph_edges_from_node_id'), table_name='form_graph_edges')
    op.drop_index(op.f('ix_form_graph_edges_form_version_id'), table_name='form_graph_edges')
    op.drop_table('form_graph_edges')
    op.drop_index(op.f('ix_answers_session_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_form_id'), table_name='answers')
    op.drop_index(op.f('ix_answers_field_key'), table_name='answers')
    op.drop_table('answers')
    op.drop_index(op.f('ix_respondent_sessions_form_version_id'), table_name='respondent_sessions')
    op.drop_index(op.f('ix_respondent_sessions_form_id'), table_name='respondent_sessions')
    op.drop_table('respondent_sessions')
    op.drop_index(op.f('ix_memberships_org_id'), table_name='memberships')
    op.drop_index(op.f('ix_memberships_admin_user_id'), table_name='memberships')
    op.drop_table('memberships')
    op.drop_index(op.f('ix_form_graph_nodes_key'), table_name='form_graph_nodes')
    op.drop_index(op.f('ix_form_graph_nodes_form_version_id'), table_name='form_graph_nodes')
    op.drop_table('form_graph_nodes')
    op.drop_index(op.f('ix_exports_form_id'), table_name='exports')
    op.drop_table('exports')
    op.drop_table('audit_logs')
    op.drop_table('organizations')
    op.drop_index(op.f('ix_forms_slug'), table_name='forms')
    op.drop_index(op.f('ix_forms_org_id'), table_name='forms')
    op.drop_table('forms')
    op.drop_index(op.f('ix_form_versions_form_id'), table_name='form_versions')
    op.drop_table('form_versions')
    op.drop_index(op.f('ix_admin_users_email'), table_name='admin_users')
    op.drop_table('admin_users')
    # ### end Alembic commands ###
