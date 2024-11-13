"""create cn_crop_prices table

Revision ID: d24b3fe6968a
Revises: 
Create Date: 2024-11-12 17:02:26.457863

"""

# pylint:disable=no-member,missing-function-docstring

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d24b3fe6968a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cn_crop_prices",
        sa.Column("source_url", sa.String(), nullable=False),
        sa.Column("ts", sa.Date(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("district", sa.String(), nullable=False),
        sa.Column("crop_prices", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("source_url", "ts", "region", "district"),
    )


def downgrade() -> None:
    op.drop_table("cn_crop_prices")
