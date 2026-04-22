"""add missing schema columns and tables

Revision ID: c3f1a2b9d4e7
Revises: 38c208b7772f
Create Date: 2026-04-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f1a2b9d4e7'
down_revision: Union[str, None] = '38c208b7772f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- organizations: add missing columns ---
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('plan', sa.String(length=32), server_default='free', nullable=False))
        batch_op.add_column(sa.Column('plan_responses_limit', sa.Integer(), server_default='50', nullable=False))
        batch_op.add_column(sa.Column('plan_forms_limit', sa.Integer(), server_default='3', nullable=False))
        batch_op.add_column(sa.Column('plan_voice_minutes_limit', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('plan_seats_limit', sa.Integer(), server_default='1', nullable=False))
        batch_op.add_column(sa.Column('custom_domain', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('whitelabel_enabled', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('whitelabel_brand_name', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('whitelabel_logo_url', sa.String(length=2048), nullable=True))
        batch_op.add_column(sa.Column('email_sender_domain', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('sso_enabled', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('sso_provider', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('sso_config', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('license_key', sa.String(length=512), nullable=True))
        batch_op.create_index('ix_organizations_slug', ['slug'], unique=True)
        batch_op.create_index('ix_organizations_custom_domain', ['custom_domain'], unique=True)

    # --- admin_users: add missing columns ---
    with op.batch_alter_table('admin_users') as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('oauth_provider', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider_id', sa.String(length=255), nullable=True))

    # --- forms: add missing columns ---
    with op.batch_alter_table('forms') as batch_op:
        batch_op.add_column(sa.Column('branding', sa.JSON(), server_default='{}', nullable=False))
        batch_op.add_column(sa.Column('locale', sa.String(length=16), server_default='en', nullable=False))
        batch_op.add_column(sa.Column('close_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('response_limit', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('closed_message', sa.Text(), server_default='This form is no longer accepting responses.', nullable=False))
        batch_op.add_column(sa.Column('welcome_message', sa.Text(), server_default='', nullable=False))
        batch_op.add_column(sa.Column('completion_message', sa.Text(), server_default='Thank you for your response!', nullable=False))

    # --- New tables ---

    op.create_table('invitations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('org_id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('invited_by', sa.String(length=36), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['invited_by'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_invitations_org_id', 'invitations', ['org_id'], unique=False)
    op.create_index('ix_invitations_token', 'invitations', ['token'], unique=True)

    op.create_table('password_reset_tokens',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('admin_user_id', sa.String(length=36), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('ix_password_reset_tokens_admin_user_id', 'password_reset_tokens', ['admin_user_id'], unique=False)
    op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)

    op.create_table('subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('org_id', sa.String(length=36), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('plan', sa.String(length=32), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('org_id'),
    )
    op.create_index('ix_subscriptions_org_id', 'subscriptions', ['org_id'], unique=True)

    op.create_table('usage_records',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('org_id', sa.String(length=36), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('responses_count', sa.Integer(), nullable=False),
        sa.Column('voice_minutes', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_usage_records_org_id', 'usage_records', ['org_id'], unique=False)

    op.create_table('form_webhooks',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('form_id', sa.String(length=36), nullable=False),
        sa.Column('url', sa.String(length=2048), nullable=False),
        sa.Column('events', sa.JSON(), nullable=False),
        sa.Column('secret', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_form_webhooks_form_id', 'form_webhooks', ['form_id'], unique=False)

    op.create_table('webhook_deliveries',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('webhook_id', sa.String(length=36), nullable=False),
        sa.Column('event', sa.String(length=128), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['webhook_id'], ['form_webhooks.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_webhook_deliveries_webhook_id', 'webhook_deliveries', ['webhook_id'], unique=False)

    op.create_table('file_uploads',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('session_id', sa.String(length=36), nullable=True),
        sa.Column('form_id', sa.String(length=36), nullable=True),
        sa.Column('field_key', sa.String(length=128), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=128), nullable=False),
        sa.Column('storage_path', sa.String(length=2048), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.ForeignKeyConstraint(['session_id'], ['respondent_sessions.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_file_uploads_form_id', 'file_uploads', ['form_id'], unique=False)
    op.create_index('ix_file_uploads_session_id', 'file_uploads', ['session_id'], unique=False)

    op.create_table('api_keys',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('org_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('prefix', sa.String(length=16), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash'),
    )
    op.create_index('ix_api_keys_org_id', 'api_keys', ['org_id'], unique=False)


def downgrade() -> None:
    op.drop_table('api_keys')
    op.drop_table('file_uploads')
    op.drop_table('webhook_deliveries')
    op.drop_table('form_webhooks')
    op.drop_table('usage_records')
    op.drop_table('subscriptions')
    op.drop_table('password_reset_tokens')
    op.drop_table('invitations')

    with op.batch_alter_table('forms') as batch_op:
        batch_op.drop_column('completion_message')
        batch_op.drop_column('welcome_message')
        batch_op.drop_column('closed_message')
        batch_op.drop_column('response_limit')
        batch_op.drop_column('close_date')
        batch_op.drop_column('locale')
        batch_op.drop_column('branding')

    with op.batch_alter_table('admin_users') as batch_op:
        batch_op.drop_column('oauth_provider_id')
        batch_op.drop_column('oauth_provider')
        batch_op.drop_column('email_verified')

    with op.batch_alter_table('organizations') as batch_op:
        batch_op.drop_index('ix_organizations_custom_domain')
        batch_op.drop_index('ix_organizations_slug')
        batch_op.drop_column('license_key')
        batch_op.drop_column('sso_config')
        batch_op.drop_column('sso_provider')
        batch_op.drop_column('sso_enabled')
        batch_op.drop_column('email_sender_domain')
        batch_op.drop_column('whitelabel_logo_url')
        batch_op.drop_column('whitelabel_brand_name')
        batch_op.drop_column('whitelabel_enabled')
        batch_op.drop_column('custom_domain')
        batch_op.drop_column('plan_seats_limit')
        batch_op.drop_column('plan_voice_minutes_limit')
        batch_op.drop_column('plan_forms_limit')
        batch_op.drop_column('plan_responses_limit')
        batch_op.drop_column('plan')
        batch_op.drop_column('stripe_customer_id')
        batch_op.drop_column('slug')
