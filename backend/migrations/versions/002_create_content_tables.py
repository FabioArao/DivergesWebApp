"""create content tables

Revision ID: 002
Revises: 001
Create Date: 2023-12-20 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum type for content types
    op.execute("CREATE TYPE content_type AS ENUM ('video', 'document', 'ebook')")
    
    # Create content categories table
    op.create_table(
        'content_categories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create educational content table
    op.create_table(
        'educational_content',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type', postgresql.ENUM('video', 'document', 'ebook', name='content_type'), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),  # For videos (in seconds)
        sa.Column('category_id', sa.String(), nullable=False),
        sa.Column('uploaded_by', sa.String(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('download_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['category_id'], ['content_categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create content access table (for tracking student access)
    op.create_table(
        'content_access',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('last_accessed', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('progress', sa.Float(), nullable=False, server_default='0'),  # For tracking video/ebook progress
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['content_id'], ['educational_content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create content comments table
    op.create_table(
        'content_comments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('content_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['content_id'], ['educational_content.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_educational_content_category', 'educational_content', ['category_id'])
    op.create_index('idx_educational_content_uploaded_by', 'educational_content', ['uploaded_by'])
    op.create_index('idx_educational_content_type', 'educational_content', ['content_type'])
    op.create_index('idx_content_access_user', 'content_access', ['user_id'])
    op.create_index('idx_content_access_content', 'content_access', ['content_id'])
    op.create_index('idx_content_comments_content', 'content_comments', ['content_id'])
    op.create_index('idx_content_comments_user', 'content_comments', ['user_id'])

def downgrade():
    # Drop indexes first
    op.drop_index('idx_content_comments_user')
    op.drop_index('idx_content_comments_content')
    op.drop_index('idx_content_access_content')
    op.drop_index('idx_content_access_user')
    op.drop_index('idx_educational_content_type')
    op.drop_index('idx_educational_content_uploaded_by')
    op.drop_index('idx_educational_content_category')
    
    # Drop tables
    op.drop_table('content_comments')
    op.drop_table('content_access')
    op.drop_table('educational_content')
    op.drop_table('content_categories')
    
    # Drop enum type
    op.execute('DROP TYPE content_type')
