"""empty message

Revision ID: 7164ec107ff0
Revises: 73ffa4dd8300
Create Date: 2022-01-24 19:38:15.479467

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7164ec107ff0'
down_revision = '73ffa4dd8300'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('start_msg', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'messages', ['link'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'messages', type_='unique')
    op.drop_column('messages', 'start_msg')
    # ### end Alembic commands ###