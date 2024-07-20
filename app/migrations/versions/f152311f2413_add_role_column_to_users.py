"""add role column to users.

Revision ID: f152311f2413
Revises: 041bfa17e700
Create Date: 2024-07-18 20:38:19.160246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f152311f2413'
down_revision: Union[str, None] = '041bfa17e700'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Создаем ENUM тип
    userrole_enum = postgresql.ENUM('user', 'moder', 'admin', name='userrole')
    userrole_enum.create(op.get_bind())

    # Добавляем новый столбец с типом ENUM
    op.add_column('users', sa.Column('role', userrole_enum, nullable=False, server_default='user'))

    # Удаляем значение по умолчанию
    op.alter_column('users', 'role', server_default=None)

def downgrade():
    # Удаляем столбец
    op.drop_column('users', 'role')
