"""add recommendation snapshot uniqueness

Revision ID: de2feafa1eb9
Revises: 
Create Date: 2026-11-07 20:01:55.518568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de2feafa1eb9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "uq_replenishment_recommendations_snapshot_id",
        "replenishment_recommendations",
        ["snapshot_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_replenishment_recommendations_snapshot_id",
        table_name="replenishment_recommendations",
    )