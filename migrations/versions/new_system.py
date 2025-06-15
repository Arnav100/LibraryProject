"""add book cover url

Revision ID: new_system
Revises: add_book_cover_url
Create Date: 2025-06-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'new_system'
down_revision = 'add_book_cover_url'
branch_labels = None
depends_on = None

def upgrade():
    # Update the books table
    op.drop_column('books', "total_copies")
    op.drop_column('books', "available_copies")
    op.add_column('books', sa.Column('price', sa.Integer(), nullable=False))
    op.add_column("books", sa.Column("purchased_at", sa.DateTime(), nullable=True))
    
    # Update the users table
    op.add_column("users", sa.Column("email", sa.String(255), nullable=False))
    
    # Delete checkouts and holds tables
    op.drop_table("checkouts")
    op.drop_table("holds")

    # Create new Gifts table
    op.create_table("gifts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("purchased_by", sa.String(255), nullable=False, default="Arnav"),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
    )
    
    # Create new wishlist table
    op.create_table("wishlist",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("isbn", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column("fulfilled", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )

def downgrade():
    # Undo all changes
    op.drop_table("gifts")
    op.drop_table("wishlist")
    op.add_column('books', sa.Column('total_copies', sa.Integer(), nullable=False))
    op.add_column('books', sa.Column('available_copies', sa.Integer(), nullable=False))
    op.drop_column('books', 'price')
    op.drop_column("books", "purchased_at")
    op.drop_column("users", "email")
    
    # Re-create checkouts and holds tables
    op.create_table("checkouts",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("returned", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
    )
    op.create_table("holds",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("book_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("hold_date", sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["book_id"], ["books.id"]),
        sa.UniqueConstraint("book_id", "user_id"),
        sa.UniqueConstraint("book_id", "position"),
    )