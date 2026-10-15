from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9d55426cc9bd'
down_revision: Union[str, Sequence[str], None] = 'b16f452f9923'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.String(),
            nullable=False,
            server_default='user'
        )
    )


def downgrade() -> None:
    op.drop_column('users', 'role')