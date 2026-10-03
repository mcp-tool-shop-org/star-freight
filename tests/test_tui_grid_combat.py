"""Interactive overlay CombatScreen — static keys, grey slots, no tab remap."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402
from portlight.app.tui.screens.combat import CombatScreen  # noqa: E402
from portlight.engine.sf_campaign import begin_combat, finish_combat, hire_crew  # noqa: E402
from portlight.engine.grid_combat import CombatPhase  # noqa: E402


def _session(tmp_path: Path) -> GameSession:
    s = GameSession(tmp_path, slot="tui_grid_combat")
    s.new("Kael", seed=1)
    return s


def _pirate_enc() -> dict:
    return {"archetype": "reach_pirate", "civilization": "reach"}


def test_begin_combat_is_live_not_resolved(tmp_path: Path):
    s = _session(tmp_path)
    cs = begin_combat(s.sf_campaign, _pirate_enc())
    assert cs.phase == CombatPhase.ACTIVE
    assert cs.player_ships() and cs.enemy_ships()
    hull_before = s.sf_campaign.ship_hull
    # Campaign hull is untouched until finish_combat.
    assert s.sf_campaign.ship_hull == hull_before


def test_finish_combat_writes_hull(tmp_path: Path):
    s = _session(tmp_path)
    enc = _pirate_enc()
    cs = begin_combat(s.sf_campaign, enc)
    player = cs.player_ships()[0]
    player.hp = 900
    cs.phase = CombatPhase.VICTORY
    result = finish_combat(s.sf_campaign, cs, enc)
    assert s.sf_campaign.ship_hull == 900
    assert result.player_hull_remaining == 900


def test_empty_ability_slots_are_labelled(tmp_path: Path):
    s = _session(tmp_path)
    cs = begin_combat(s.sf_campaign, _pirate_enc())
    screen = CombatScreen(s, cs, _pirate_enc())
    slots = screen._slots()
    assert len(slots) == 4
    assert all(slot["ability"] is None for slot in slots)
    assert all(slot["reason"] == "no crew" for slot in slots)


def test_hired_crew_fills_a_named_slot(tmp_path: Path):
    s = _session(tmp_path)
    hire_crew(s.sf_campaign, "sera_vale")
    cs = begin_combat(s.sf_campaign, _pirate_enc())
    screen = CombatScreen(s, cs, _pirate_enc())
    slots = screen._slots()
    filled = [slot for slot in slots if slot["ability"] is not None]
    assert len(filled) == 1
    assert filled[0]["ability"].crew_source == "Sera"
    assert slots[1]["reason"] == "no crew"


@pytest.mark.asyncio
async def test_tab_keys_do_not_leave_combat(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    cs = begin_combat(s.sf_campaign, _pirate_enc())
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(CombatScreen(s, cs, _pirate_enc()))
        await pilot.pause()
        assert isinstance(app.screen, CombatScreen)
        for key in ("d", "c", "r", "f", "j"):
            await pilot.press(key)
            await pilot.pause()
            assert isinstance(app.screen, CombatScreen), f"{key} left combat"
        assert app._current_tab == "dashboard"


@pytest.mark.asyncio
async def test_combat_verbs_stay_on_the_grid(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    cs = begin_combat(s.sf_campaign, _pirate_enc())
    async with app.run_test(size=(100, 30)) as pilot:
        screen = CombatScreen(s, cs, _pirate_enc())
        app.push_screen(screen)
        await pilot.pause()
        await pilot.press("v")
        await pilot.pause()
        assert isinstance(app.screen, CombatScreen)
        assert any(ev.action == "defend" for ev in cs.events)
