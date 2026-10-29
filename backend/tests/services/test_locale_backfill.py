"""The fork's one-shot Finnish backfill for a previously saved ``enabledLocales``."""

from __future__ import annotations

from sqlalchemy import select

from app.models.app_settings import AppSettings
from app.services.locale_backfill import MARKER_KEY, ensure_finnish_enabled


async def _settings(db) -> dict:
    db.expire_all()
    row = (
        await db.execute(select(AppSettings).where(AppSettings.id == "default"))
    ).scalar_one_or_none()
    return row.general_settings if row else None


async def _save(db, general: dict) -> None:
    db.add(AppSettings(id="default", general_settings=general))
    await db.commit()


async def test_no_settings_row_is_marked_without_pinning_locales(db) -> None:
    assert await ensure_finnish_enabled(db) is False
    general = await _settings(db)
    assert general == {MARKER_KEY: {"fi": True}}


async def test_unset_enabled_locales_keeps_the_all_locales_default(db) -> None:
    await _save(db, {"currency": "EUR"})
    assert await ensure_finnish_enabled(db) is False
    general = await _settings(db)
    assert "enabledLocales" not in general
    assert general["currency"] == "EUR"
    assert general[MARKER_KEY] == {"fi": True}


async def test_saved_locales_without_finnish_gain_it(db) -> None:
    await _save(db, {"enabledLocales": ["en", "de"], "currency": "EUR"})
    assert await ensure_finnish_enabled(db) is True
    general = await _settings(db)
    assert general["enabledLocales"] == ["en", "de", "fi"]
    assert general["currency"] == "EUR"
    assert general[MARKER_KEY] == {"fi": True}


async def test_saved_locales_with_finnish_are_left_alone(db) -> None:
    await _save(db, {"enabledLocales": ["fi", "en"]})
    assert await ensure_finnish_enabled(db) is False
    assert (await _settings(db))["enabledLocales"] == ["fi", "en"]


async def test_admin_disabling_finnish_after_the_backfill_sticks(db) -> None:
    await _save(db, {"enabledLocales": ["en"], MARKER_KEY: {"fi": True, "xx": True}})
    assert await ensure_finnish_enabled(db) is False
    general = await _settings(db)
    assert general["enabledLocales"] == ["en"]
    assert general[MARKER_KEY] == {"fi": True, "xx": True}


async def test_second_run_is_a_no_op(db) -> None:
    await _save(db, {"enabledLocales": ["en"]})
    assert await ensure_finnish_enabled(db) is True
    assert await ensure_finnish_enabled(db) is False
    assert (await _settings(db))["enabledLocales"] == ["en", "fi"]
