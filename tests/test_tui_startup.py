"""Save-slot picker + new-captain entry (Item 4b)."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession, list_star_freight_saves  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402
from portlight.app.tui.screens.startup import (  # noqa: E402
    SlotPickerScreen,
    NewGameDialog,
)


def _seed_slot(tmp_path: Path, slot: str, name: str) -> None:
    s = GameSession(tmp_path, slot=slot)
    s.new(name, seed=1)


def test_list_star_freight_saves(tmp_path: Path):
    _seed_slot(tmp_path, "alpha", "Alpha")
    _seed_slot(tmp_path, "beta", "Beta")
    saves = {x["slot"]: x for x in list_star_freight_saves(tmp_path)}
    assert "alpha" in saves and saves["alpha"]["captain_name"] == "Alpha"
    assert "beta" in saves and saves["beta"]["captain_name"] == "Beta"


@pytest.mark.asyncio
async def test_picker_shows_when_no_save(tmp_path: Path):
    s = GameSession(tmp_path, slot="does_not_exist")
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, SlotPickerScreen)


@pytest.mark.asyncio
async def test_existing_slot_autoloads_without_picker(tmp_path: Path):
    _seed_slot(tmp_path, "auto", "AutoCap")
    s = GameSession(tmp_path, slot="auto")
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert not isinstance(app.screen, SlotPickerScreen)
        assert s.active and s.sf_campaign.captain_name == "AutoCap"


@pytest.mark.asyncio
async def test_picker_loads_selected_slot(tmp_path: Path):
    _seed_slot(tmp_path, "alpha", "Alpha")
    s = GameSession(tmp_path, slot="fresh")
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, SlotPickerScreen)
        await pilot.press("a", "l", "p", "h", "a")
        await pilot.press("enter")
        await pilot.pause()
        assert not isinstance(app.screen, SlotPickerScreen)
        assert s.active and s.sf_campaign.captain_name == "Alpha"


@pytest.mark.asyncio
async def test_picker_new_game_creates_captain(tmp_path: Path):
    s = GameSession(tmp_path, slot="fresh")
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        assert isinstance(app.screen, SlotPickerScreen)
        await pilot.press("n")
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, NewGameDialog)
        await pilot.press("z", "a", "r", "a")
        await pilot.press("enter")
        await pilot.pause()
        assert s.active and s.sf_campaign.captain_name == "zara"
        assert s.slot == "zara"
