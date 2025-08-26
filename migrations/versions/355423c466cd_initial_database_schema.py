"""Initial database schema

Revision ID: 355423c466cd
Revises: 
Create Date: 2025-08-25 14:38:24.754266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '355423c466cd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create books table
    op.create_table('books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('author', sa.String(), nullable=False),
        sa.Column('isbn', sa.String(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_books_id'), 'books', ['id'], unique=False)
    
    # Create members table
    op.create_table('members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('salt', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_members_id'), 'members', ['id'], unique=False)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('salt', sa.String(), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_unique_constraint('uq_users_username', 'users', ['username'])
    
    # Create loans table
    op.create_table('loans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('loan_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('return_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_loans_id'), 'loans', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_loans_id'), table_name='loans')
    op.drop_table('loans')
    op.drop_constraint('uq_users_username', 'users', type_='unique')
    op.drop_table('users')
    op.drop_index(op.f('ix_members_id'), table_name='members')
    op.drop_table('members')
    op.drop_index(op.f('ix_books_id'), table_name='books')
    op.drop_table('books')


