"""empty message

Revision ID: e7ddc22f4a50
Revises: 6117b0ed37ea
Create Date: 2022-04-07 12:47:39.572910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7ddc22f4a50'
down_revision = '6117b0ed37ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('purchases', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.create_foreign_key(None, 'purchases', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'purchases', type_='foreignkey')
    op.alter_column('purchases', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
