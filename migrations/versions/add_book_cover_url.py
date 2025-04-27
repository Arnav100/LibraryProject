"""add book cover url

Revision ID: add_book_cover_url
Revises: initial_migration
Create Date: 2024-03-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_book_cover_url'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Add the cover_url column to the books table
    op.add_column('books', 
        sa.Column('cover_url', sa.String(255), nullable=True)
    )
    op.add_column('books', 
        sa.Column('description', sa.String(255), nullable=True)
    )

def downgrade():
    # Remove the cover_url column
    op.drop_column('books', 'cover_url') 