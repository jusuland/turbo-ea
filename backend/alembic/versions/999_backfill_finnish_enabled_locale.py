"""Backfill: add Finnish (``fi``) to existing ``enabledLocales`` settings."""

import json
from typing import Sequence, Union

from alembic import op
from sqlalchemy.sql import text

revision: str = "fi_enabled_locale_1"
down_revision: Union[str, None] = "148"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_LOCALE = "fi"


def _apply(add: bool) -> None:
    conn = op.get_bind()
    rows = conn.execute(text("SELECT id, general_settings FROM app_settings")).fetchall()
    for row in rows:
        settings = row.general_settings or {}
        if not isinstance(settings, dict):
            continue
        locales = settings.get("enabledLocales")
        if not isinstance(locales, list):
            continue
        if add and NEW_LOCALE not in locales:
            locales = [*locales, NEW_LOCALE]
        elif not add and NEW_LOCALE in locales:
            locales = [locale for locale in locales if locale != NEW_LOCALE]
        else:
            continue
        conn.execute(
            text("UPDATE app_settings SET general_settings = CAST(:s AS jsonb) WHERE id = :id"),
            {"s": json.dumps({**settings, "enabledLocales": locales}), "id": row.id},
        )


def upgrade() -> None:
    _apply(add=True)


def downgrade() -> None:
    _apply(add=False)