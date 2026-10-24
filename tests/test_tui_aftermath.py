"""Aftermath (C3) — one contrastive toast + writeback overlay, never a reset."""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402
from portlight.app.tui.screens.aftermath import AftermathScreen  # noqa: E402
from portlight.app.tui.screens.combat import CombatScreen  # noqa: E402
from portlight.app.sf_views import contrastive_aftermath_line  # noqa: E402
from portlight.engine.sf_campaign import begin_combat  # noqa: E402
from portlight.engine.grid_combat import CombatPhase, CombatResult  # noqa: E402
from portlight.content.star_freight import create_thal  # noqa: E402


def _session(tmp_path: Path) -> GameSession:
    s = GameSession(tmp_path, slot="tui_aftermath")
    s.new("Kael", seed=1)
    return s


def _result(**kw) -> CombatResult:
    base = dict(
        outcome=CombatPhase.VICTORY,
        turns_taken=5,
        player_hull_remaining=1500,
        player_hull_max=2000,
        player_shield_remaining=100,
        enemy_destroyed=True,
        hull_damage_taken=0,
        shield_damage_taken=0,
        crew_injuries=[],
        cargo_lost=[],
        reputation_delta={},
        credits_gained=0,
        consequence_tags=[],
    )
    base.update(kw)
    return CombatResult(**base)


# --------------------------------------------------------------- contrastive line


def test_line_victory_keeps_cargo(tmp_path: Path):
    s = _session(tmp_path)
    s.sf_campaign.ship_cargo = ["medical_supplies"]
    line = contrastive_aftermath_line(
        _result(outcome=CombatPhase.VICTORY, hull_damage_taken=400, credits_gained=200),
        s.sf_campaign,
    )
    assert "Held the field" in line
    assert "kept cargo rather than dumping it" in line
    assert "\u2212400" in line  # hull −400
    assert "200" in line


def test_line_retreat_dumps_cargo(tmp_path: Path):
    s = _session(tmp_path)
    line = contrastive_aftermath_line(
        _result(outcome=CombatPhase.RETREAT, cargo_lost=["medical_supplies"]),
        s.sf_campaign,
    )
    assert "Ran rather than lose the ship" in line
    assert "dumped Medical Supplies" in line


def test_line_names_injured_crew_and_civ_pressure(tmp_path: Path):
    s = _session(tmp_path)
    s.sf_campaign.crew.members.append(create_thal())  # Keth engineer
    line = contrastive_aftermath_line(
        _result(crew_injuries=["Thal"]),
        s.sf_campaign,
    )
    assert "Thal injured" in line
    assert "Communion docking will hurt" in line  # Keth -> Communion


# --------------------------------------------------------------- overlay screen


@pytest.mark.asyncio
async def test_aftermath_dismisses_on_escape(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(AftermathScreen(s, _result()))
        await pilot.pause()
        assert isinstance(app.screen, AftermathScreen)
        await pilot.press("escape")
        await pilot.pause()
        assert not isinstance(app.screen, AftermathScreen)


@pytest.mark.asyncio
async def test_aftermath_dismisses_on_any_mapped_key(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(AftermathScreen(s, _result()))
        await pilot.pause()
        await pilot.press("d")  # a navigation key should also continue
        await pilot.pause()
        assert not isinstance(app.screen, AftermathScreen)


@pytest.mark.asyncio
async def test_finished_combat_shows_aftermath(tmp_path: Path):
    s = _session(tmp_path)
    enc = {"archetype": "reach_pirate", "civilization": "reach"}
    cs = begin_combat(s.sf_campaign, enc)
    cs.player_ships()[0].hp = 1400
    cs.phase = CombatPhase.VICTORY  # resolved before mount
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(CombatScreen(s, cs, enc))
        await pilot.pause()
        # on_mount runs the loop, sees a non-active phase, finishes -> aftermath.
        assert isinstance(app.screen, AftermathScreen)
