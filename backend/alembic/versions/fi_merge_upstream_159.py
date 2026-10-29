"""Merge Finnish locale branch with upstream head 159."""

from collections.abc import Sequence
from typing import Union

revision: str = "fi_merge_159"
down_revision: Union[str, tuple[str, str], None] = (
    "159",
    "fi_enabled_locale_1",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass