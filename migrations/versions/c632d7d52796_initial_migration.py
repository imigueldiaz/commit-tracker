"""initial migration

Revision ID: c632d7d52796
Revises: 
Create Date: 2024-11-15 11:21:32.533714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c632d7d52796'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('branch',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('color', sa.String(length=7), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('is_independent', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('branch_dependencies',
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('depends_on_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['branch_id'], ['branch.id'], ),
    sa.ForeignKeyConstraint(['depends_on_id'], ['branch.id'], ),
    sa.PrimaryKeyConstraint('branch_id', 'depends_on_id')
    )
    op.create_table('commit',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('commit_number', sa.Integer(), nullable=False),
    sa.Column('jira_ticket', sa.String(length=20), nullable=True),
    sa.Column('branch_id', sa.Integer(), nullable=False),
    sa.Column('commit_message', sa.String(length=200), nullable=False),
    sa.Column('long_comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], ['branch.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('attachment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=100), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=True),
    sa.Column('commit_id', sa.Integer(), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['commit_id'], ['commit.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('branch_transition',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('from_branch_id', sa.Integer(), nullable=False),
    sa.Column('to_branch_id', sa.Integer(), nullable=False),
    sa.Column('commit_id', sa.Integer(), nullable=False),
    sa.Column('transitioned_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['commit_id'], ['commit.id'], ),
    sa.ForeignKeyConstraint(['from_branch_id'], ['branch.id'], ),
    sa.ForeignKeyConstraint(['to_branch_id'], ['branch.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('branch_transition')
    op.drop_table('attachment')
    op.drop_table('commit')
    op.drop_table('branch_dependencies')
    op.drop_table('branch')
    # ### end Alembic commands ###