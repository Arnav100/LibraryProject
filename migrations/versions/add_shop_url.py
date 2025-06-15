"""add book cover url

Revision ID: shop_url
Revises: new_system
Create Date: 2025-06-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_shop_url'
down_revision = 'new_system'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('wishlist', sa.Column('shop_url', sa.String(255), nullable=False))
    op.add_column('wishlist', sa.Column('price_cents', sa.Integer(), nullable=False))
    op.add_column('wishlist', sa.Column('requested_at', sa.DateTime(), nullable=False, default=sa.func.now()))
    op.add_column('wishlist', sa.Column('note', sa.String(255), nullable=True))
    
    op.drop_column('wishlist', 'created_at')
    op.drop_column('wishlist', 'author')
    op.drop_column('wishlist', 'isbn')

def downgrade():
    op.drop_column('wishlist', 'shop_url')
    op.drop_column('wishlist', 'price_cents')
    op.drop_column('wishlist', 'requested_at')
    op.drop_column('wishlist', 'note')
    
    op.add_column('wishlist', sa.Column('created_at', sa.DateTime(), nullable=True, default=sa.func.now()))
    op.add_column('wishlist', sa.Column('author', sa.String(255), nullable=True))
    op.add_column('wishlist', sa.Column('isbn', sa.String(255), nullable=True))