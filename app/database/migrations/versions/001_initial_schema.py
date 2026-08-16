"""initial_schema

Revision ID: 001
Revises: 
Create Date: 2026-08-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'banned', name='userstatus'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])

    op.create_table('telegram_accounts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('phone_masked', sa.String(length=20), nullable=True),
        sa.Column('session_encrypted', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('active', 'expired', 'invalid', 'banned', name='telegramaccountstatus'), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('last_connected', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_telegram_accounts_telegram_user_id', 'telegram_accounts', ['telegram_user_id'])
    op.create_index('ix_telegram_accounts_user_id', 'telegram_accounts', ['user_id'])

    op.create_table('telegram_sources',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('owner_user_id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_chat_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('type', sa.Enum('group', 'supergroup', 'channel', 'user', name='sourcetype'), nullable=True),
        sa.Column('access_status', sa.Enum('accessible', 'joinable', 'request_required', 'private', 'restricted', 'read_not_allowed', 'not_found', 'unknown', 'invalid', name='accessstatus'), nullable=True),
        sa.Column('can_read_messages', sa.Boolean(), nullable=True),
        sa.Column('invite_hash', sa.String(length=255), nullable=True),
        sa.Column('last_scanned', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_telegram_sources_owner_user_id', 'telegram_sources', ['owner_user_id'])
    op.create_index('ix_telegram_sources_telegram_chat_id', 'telegram_sources', ['telegram_chat_id'])
    op.create_index('ix_telegram_sources_username', 'telegram_sources', ['username'])

    op.create_table('whatsapp_accounts',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('direct_url', sa.Text(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_whatsapp_accounts_user_id', 'whatsapp_accounts', ['user_id'])

    op.create_table('whatsapp_links',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('normalized_url', sa.Text(), nullable=False),
        sa.Column('display_url', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('direct_join', 'request_join', 'invalid', 'revoked_or_changed', 'temporary_error', 'unknown', 'discovered', 'pending_analysis', 'analyzing', name='linkstatus'), nullable=True),
        sa.Column('confidence', sa.Enum('high', 'medium', 'low', name='confidencelevel'), nullable=True),
        sa.Column('first_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('check_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('normalized_url')
    )
    op.create_index('ix_whatsapp_links_normalized_url', 'whatsapp_links', ['normalized_url'])

    op.create_table('scan_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('type', sa.Enum('source_scan', 'link_analysis', 'export', 'cleanup', 'rescan', name='jobtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'paused', 'completed', 'failed', 'cancelled', name='jobstatus'), nullable=True),
        sa.Column('total_messages', sa.BigInteger(), nullable=True),
        sa.Column('processed_messages', sa.BigInteger(), nullable=True),
        sa.Column('total_urls', sa.BigInteger(), nullable=True),
        sa.Column('whatsapp_urls', sa.BigInteger(), nullable=True),
        sa.Column('unique_urls', sa.BigInteger(), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=True),
        sa.Column('scope', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['source_id'], ['telegram_sources.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scan_jobs_source_id', 'scan_jobs', ['source_id'])
    op.create_index('ix_scan_jobs_user_id', 'scan_jobs', ['user_id'])

    op.create_table('exports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('format', sa.Enum('txt', 'csv', 'json', 'xlsx', name='exportformat'), nullable=False),
        sa.Column('category', sa.Enum('direct_join', 'request_join', name='walletcategory'), nullable=True),
        sa.Column('file_path', sa.Text(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('total_links', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_exports_user_id', 'exports', ['user_id'])

    op.create_table('job_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.Enum('info', 'success', 'warning', 'error', 'access', name='notificationlevel'), nullable=False),
        sa.Column('event', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['scan_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_logs_job_id', 'job_logs', ['job_id'])

    op.create_table('link_analysis_runs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('link_id', sa.BigInteger(), nullable=False),
        sa.Column('status', sa.Enum('direct_join', 'request_join', 'invalid', 'revoked_or_changed', 'temporary_error', 'unknown', 'discovered', 'pending_analysis', 'analyzing', name='linkstatus'), nullable=False),
        sa.Column('confidence', sa.Enum('high', 'medium', 'low', name='confidencelevel'), nullable=True),
        sa.Column('response_data', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('checked_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['link_id'], ['whatsapp_links.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_link_analysis_runs_link_id', 'link_analysis_runs', ['link_id'])

    op.create_table('link_sources',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('link_id', sa.BigInteger(), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=False),
        sa.Column('message_id', sa.BigInteger(), nullable=True),
        sa.Column('first_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_seen', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['link_id'], ['whatsapp_links.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_id'], ['telegram_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_link_sources_link_id', 'link_sources', ['link_id'])
    op.create_index('ix_link_sources_source_id', 'link_sources', ['source_id'])

    op.create_table('wallet_links',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('link_id', sa.BigInteger(), nullable=False),
        sa.Column('category', sa.Enum('direct_join', 'request_join', name='walletcategory'), nullable=False),
        sa.Column('saved_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['link_id'], ['whatsapp_links.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'link_id', name='uq_wallet_user_link')
    )
    op.create_index('ix_wallet_links_link_id', 'wallet_links', ['link_id'])
    op.create_index('ix_wallet_links_user_id', 'wallet_links', ['user_id'])

def downgrade() -> None:
    op.drop_table('wallet_links')
    op.drop_table('link_sources')
    op.drop_table('link_analysis_runs')
    op.drop_table('job_logs')
    op.drop_table('exports')
    op.drop_table('scan_jobs')
    op.drop_table('whatsapp_links')
    op.drop_table('whatsapp_accounts')
    op.drop_table('telegram_sources')
    op.drop_table('telegram_accounts')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS userstatus')
    op.execute('DROP TYPE IF EXISTS telegramaccountstatus')
    op.execute('DROP TYPE IF EXISTS sourcetype')
    op.execute('DROP TYPE IF EXISTS accessstatus')
    op.execute('DROP TYPE IF EXISTS linkstatus')
    op.execute('DROP TYPE IF EXISTS confidencelevel')
    op.execute('DROP TYPE IF EXISTS jobtype')
    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS notificationlevel')
    op.execute('DROP TYPE IF EXISTS exportformat')
    op.execute('DROP TYPE IF EXISTS walletcategory')