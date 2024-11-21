"""the type of the improvments field in the users model has been changed.

Revision ID: 02a5d7034dab
Revises: f152311f2413
Create Date: 2024-07-19 17:29:53.175712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '02a5d7034dab'
down_revision: Union[str, None] = 'f152311f2413'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Добавить временный столбец с типом JSON
    op.add_column('users', sa.Column('improvements_temp', postgresql.JSON, nullable=True))

    # Преобразовать данные из boosts в improvements_temp
    op.execute("""
        UPDATE users 
        SET improvements_temp = 
            CASE 
                WHEN boosts IS NULL THEN '[]'::json
                ELSE json_build_array(boosts)
            END
    """)

    # Удалить старый столбец
    op.drop_column('users', 'boosts')

    # Переименовать временный столбец в boosts
    op.alter_column('users', 'improvements_temp', new_column_name='boosts')

def downgrade():
    # Добавить обратно старый столбец с типом Integer (или другим подходящим типом)
    op.add_column('users', sa.Column('improvements_old', sa.Integer, nullable=True))

    # Преобразовать данные обратно из JSON в Integer
    op.execute("""
        UPDATE users 
        SET improvements_old = 
            CASE 
                WHEN boosts IS NULL THEN NULL
                ELSE (boosts->>0)::integer
            END
    """)

    # Удалить столбец boosts
    op.drop_column('users', 'boosts')

    # Переименовать временный столбец обратно в boosts
    op.alter_column('users', 'improvements_old', new_column_name='boosts')
