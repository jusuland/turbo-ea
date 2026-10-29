"""Fork-only, one-shot backfill: add Finnish to a previously saved ``enabledLocales``.

Kept out of Alembic so the fork follows upstream's linear migration chain; the
``localeBackfills`` marker makes it run once, so an admin may disable Finnish later.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_settings import AppSettings

MARKER_KEY = "localeBackfills"
FINNISH = "fi"


async def ensure_finnish_enabled(db: AsyncSession) -> bool:
    """Run the Finnish backfill once per install; True when ``enabledLocales`` changed."""
    result = await db.execute(select(AppSettings).where(AppSettings.id == "default"))
    row = result.scalar_one_or_none()
    if row is None:
        row = AppSettings(id="default")
        db.add(row)
    general = dict(row.general_settings or {})
    markers = dict(general.get(MARKER_KEY) or {})
    if markers.get(FINNISH):
        return False

    changed = False
    locales = general.get("enabledLocales")
    if isinstance(locales, list) and FINNISH not in locales:
        general["enabledLocales"] = [*locales, FINNISH]
        changed = True

    markers[FINNISH] = True
    general[MARKER_KEY] = markers
    row.general_settings = general
    await db.commit()
    return changed
