"""changed users model.

Revision ID: 2b91caa7612a
Revises: 67edbf23910c
Create Date: 2024-11-24 21:27:29.095118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b91caa7612a'
down_revision: Union[str, None] = '67edbf23910c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'users',
        'last_update_time',
        existing_type=sa.Date(),
        type_=sa.Integer(),
        postgresql_using="EXTRACT(EPOCH FROM last_update_time)::integer / 86400"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'last_update_time',
               existing_type=sa.Integer(),
               type_=sa.DATE(),
               existing_nullable=True)
    # ### end Alembic commands ###