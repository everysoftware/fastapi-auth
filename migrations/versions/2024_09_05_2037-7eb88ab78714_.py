"""empty message

Revision ID: 7eb88ab78714
Revises: 5ee810fadd8e
Create Date: 2024-09-05 20:37:32.723760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7eb88ab78714"
down_revision: Union[str, None] = "5ee810fadd8e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "oidc_accounts", sa.Column("account_id", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("oidc_accounts", "account_id")
    # ### end Alembic commands ###
