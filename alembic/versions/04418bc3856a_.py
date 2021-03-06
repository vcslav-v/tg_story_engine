"""empty message

Revision ID: 04418bc3856a
Revises: 3305ddd4c403
Create Date: 2021-06-09 10:45:44.777996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04418bc3856a'
down_revision = '3305ddd4c403'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wait_reactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('uid', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('reactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('wait_reaction_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['wait_reaction_id'], ['wait_reactions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reactions')
    op.drop_table('wait_reactions')
    # ### end Alembic commands ###
