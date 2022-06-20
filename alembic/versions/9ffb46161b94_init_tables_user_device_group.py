"""Init tables user, device, group

Revision ID: 9ffb46161b94
Revises: 
Create Date: 2022-06-20 17:13:09.385257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ffb46161b94'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('grupa',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('p1', sa.String(), nullable=True),
    sa.Column('p2', sa.String(), nullable=True),
    sa.Column('p3', sa.String(), nullable=True),
    sa.Column('p4', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('urzadzenie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('ob', sa.String(), nullable=False),
    sa.Column('localization', sa.String(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('ip', sa.String(), nullable=False),
    sa.Column('mask', sa.String(), nullable=False),
    sa.Column('mac', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('group_name', sa.String(), nullable=False),
    sa.Column('p1', sa.String(), nullable=True),
    sa.Column('p2', sa.String(), nullable=True),
    sa.Column('p3', sa.String(), nullable=True),
    sa.Column('p4', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ip'),
    sa.UniqueConstraint('mac'),
    sa.UniqueConstraint('name')
    )
    op.create_table('urzytkownik',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin', sa.Boolean(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('forename', sa.String(), nullable=False),
    sa.Column('department', sa.String(), nullable=False),
    sa.Column('login', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_by', sa.String(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('urzytkownik')
    op.drop_table('urzadzenie')
    op.drop_table('grupa')
    # ### end Alembic commands ###
