"""empty message

Revision ID: 8010aea24e1a
Revises: c445fd089691
Create Date: 2020-09-24 10:24:20.939414

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8010aea24e1a'
down_revision = 'c445fd089691'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('howmanytimes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('how_key', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('how_value', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('howmanytimes')
    # ### end Alembic commands ###
