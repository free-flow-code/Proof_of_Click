"""add ondelete cascade.

Revision ID: 3a853d952127
Revises: 02a5d7034dab
Create Date: 2024-07-19 19:49:48.274900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a853d952127'
down_revision: Union[str, None] = '02a5d7034dab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('game_items_user_id_fkey', 'game_items', type_='foreignkey')
    op.create_foreign_key(None, 'game_items', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('improvements_user_id_fkey', 'improvements', type_='foreignkey')
    op.create_foreign_key(None, 'improvements', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('lots_game_item_id_fkey', 'lots', type_='foreignkey')
    op.drop_constraint('lots_user_id_fkey', 'lots', type_='foreignkey')
    op.create_foreign_key(None, 'lots', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'lots', 'game_items', ['game_item_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
    op.create_foreign_key(None, 'notifications', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'notifications', type_='foreignkey')
    op.create_foreign_key('notifications_user_id_fkey', 'notifications', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'lots', type_='foreignkey')
    op.drop_constraint(None, 'lots', type_='foreignkey')
    op.create_foreign_key('lots_user_id_fkey', 'lots', 'users', ['user_id'], ['id'])
    op.create_foreign_key('lots_game_item_id_fkey', 'lots', 'game_items', ['game_item_id'], ['id'])
    op.drop_constraint(None, 'improvements', type_='foreignkey')
    op.create_foreign_key('improvements_user_id_fkey', 'improvements', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'game_items', type_='foreignkey')
    op.create_foreign_key('game_items_user_id_fkey', 'game_items', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###