"""Add level for improvements.

Revision ID: fc38a7e45b69
Revises: d7415e91f986
Create Date: 2024-07-17 17:03:29.008982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc38a7e45b69'
down_revision: Union[str, None] = 'd7415e91f986'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('improvements', sa.Column('level', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('improvements', 'level')
    # ### end Alembic commands ###