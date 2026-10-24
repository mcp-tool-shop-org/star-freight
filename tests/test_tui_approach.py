"""Approach overlay (C2) — stakes-first encounter surface.

Every interdiction opens an approach: Negotiate / Flee / Fight. The grid is only
reached on Fight. A Veshan honor challenge cannot skip the grid. These tests
cover the engine resolutions and the ApproachScreen key routing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402
from portlight.app.tui.screens.approach import ApproachScreen  # noqa: E402
from portlight.app.tui.screens.combat import CombatScreen  # noqa: E402
from portlight.content.star_freight import SLICE_LANES  # noqa: E402
from portlight.engine.sf_campaign import (  # noqa: E402
    approach_encounter,
    negotiate_encounter,
    flee_encounter,
    travel_to,
)


def _session(tmp_path: Path) -> GameSession:
    s = GameSession(tmp_path, slot="tui_approach")
    s.new("Kael", seed=1)
    return s


def _reach_enc(can_negotiate: bool = False) -> dict:
    opts = {"knowledge_level": 1 if can_negotiate else 0, "can_negotiate": can_negotiate}
    return {"archetype": "reach_pirate", "civilization": "reach", "cultural_options": opts}


def _compact_enc() -> dict:
    return {
        "archetype": "compact_patrol",
        "civilization": "compact",
        "cultural_options": {"knowledge_level": 1, "can_negotiate": True},
    }


def _veshan_enc() -> dict:
    return {
        "archetype": "veshan_challenge",
        "civilization": "veshan",
        "cultural_options": {"knowledge_level": 1, "can_negotiate": True},
    }


# --------------------------------------------------------------------- engine


def test_approach_reach_defaults(tmp_path: Path):
    s = _session(tmp_path)
    info = approach_encounter(s.sf_campaign, _reach_enc())
    assert info["must_fight"] is False
    assert info["can_flee"] is True
    assert info["can_negotiate"] is False  # no standing without knowledge
    assert info["enemy_hull"] > 0 and info["player_hull"] == s.sf_campaign.ship_hull


def test_approach_veshan_must_fight(tmp_path: Path):
    s = _session(tmp_path)
    info = approach_encounter(s.sf_campaign, _veshan_enc())
    assert info["must_fight"] is True
    # Honor closes both social approaches even when knowledge would allow them.
    assert info["can_negotiate"] is False
    assert info["can_flee"] is False


def test_negotiate_requires_standing(tmp_path: Path):
    s = _session(tmp_path)
    result = negotiate_encounter(s.sf_campaign, _reach_enc(can_negotiate=False))
    assert result["resolved"] is False
    assert "standing" in result["error"].lower()


def test_negotiate_reach_pays_a_toll(tmp_path: Path):
    s = _session(tmp_path)
    credits_before = s.sf_campaign.credits
    result = negotiate_encounter(s.sf_campaign, _reach_enc(can_negotiate=True))
    assert result["resolved"] is True
    assert result["outcome"] == "negotiated"
    assert s.sf_campaign.credits < credits_before
    assert result["credits_spent"] > 0


def test_negotiate_veshan_blocked(tmp_path: Path):
    s = _session(tmp_path)
    result = negotiate_encounter(s.sf_campaign, _veshan_enc())
    assert result["resolved"] is False


def test_flee_veshan_blocked(tmp_path: Path):
    s = _session(tmp_path)
    result = flee_encounter(s.sf_campaign, _veshan_enc())
    assert result["resolved"] is False


def test_flee_reach_drops_cargo_and_aborts(tmp_path: Path):
    s = _session(tmp_path)
    state = s.sf_campaign
    state.ship_cargo = ["medical_supplies", "ration_grain"]
    state.in_transit = True
    state.pending_destination = "communion_relay"
    result = flee_encounter(state, _reach_enc())
    assert result["resolved"] is True
    assert result["outcome"] == "fled"
    assert len(result["cargo_lost"]) == 1
    assert len(state.ship_cargo) == 1
    # Fleeing aborts the run — no longer in transit, stays at the origin.
    assert state.in_transit is False
    assert state.pending_destination is None


def test_flee_compact_flags_wanted(tmp_path: Path):
    s = _session(tmp_path)
    state = s.sf_campaign
    before = state.reputation["compact"]
    result = flee_encounter(state, _compact_enc())
    assert result["resolved"] is True
    assert state.reputation["compact"] == before - 10
    assert "wanted_compact" in state.consequence_tags


def test_travel_encounter_then_negotiate_arrives(tmp_path: Path):
    s = _session(tmp_path)
    state = s.sf_campaign
    # Guarantee an interdiction so we exercise the transit → approach → arrive path.
    state.danger_multiplier = 100.0
    dest = None
    for lane in SLICE_LANES.values():
        if lane.station_a == state.current_station:
            dest = lane.station_b
            break
        if lane.station_b == state.current_station:
            dest = lane.station_a
            break
    assert dest is not None
    result = travel_to(state, dest)
    assert result["encounter"] is not None
    assert state.in_transit is True
    enc = result["encounter"]
    # Make the interdiction negotiable regardless of the rolled archetype's civ.
    enc["cultural_options"] = {"knowledge_level": 2, "can_negotiate": True}
    if enc["archetype"] == "veshan_challenge":
        pytest.skip("honor challenge cannot be negotiated; rerun draws another lane")
    outcome = negotiate_encounter(state, enc)
    assert outcome["resolved"] is True
    assert state.in_transit is False
    assert state.current_station == dest


# --------------------------------------------------------------------- screen


def test_approach_screen_constructs(tmp_path: Path):
    s = _session(tmp_path)
    screen = ApproachScreen(s, _reach_enc())
    assert screen.info["archetype"] == "reach_pirate"
    assert screen._resolved is False


@pytest.mark.asyncio
async def test_fight_opens_the_grid(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ApproachScreen(s, _reach_enc()))
        await pilot.pause()
        assert isinstance(app.screen, ApproachScreen)
        await pilot.press("g")
        await pilot.pause()
        assert isinstance(app.screen, CombatScreen)


@pytest.mark.asyncio
async def test_flee_resolves_and_leaves_approach(tmp_path: Path):
    s = _session(tmp_path)
    s.sf_campaign.in_transit = True
    s.sf_campaign.pending_destination = "communion_relay"
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ApproachScreen(s, _reach_enc()))
        await pilot.pause()
        await pilot.press("f")
        await pilot.pause()
        assert not isinstance(app.screen, ApproachScreen)
        assert s.sf_campaign.in_transit is False


@pytest.mark.asyncio
async def test_negotiate_resolves_when_available(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ApproachScreen(s, _reach_enc(can_negotiate=True)))
        await pilot.pause()
        await pilot.press("n")
        await pilot.pause()
        assert not isinstance(app.screen, ApproachScreen)


@pytest.mark.asyncio
async def test_veshan_cannot_flee_or_negotiate_only_fight(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ApproachScreen(s, _veshan_enc()))
        await pilot.pause()
        # Flee and negotiate are closed — the screen stays up.
        await pilot.press("f")
        await pilot.pause()
        assert isinstance(app.screen, ApproachScreen)
        await pilot.press("n")
        await pilot.pause()
        assert isinstance(app.screen, ApproachScreen)
        # Only the grid resolves an honor challenge.
        await pilot.press("g")
        await pilot.pause()
        assert isinstance(app.screen, CombatScreen)


@pytest.mark.asyncio
async def test_tab_keys_do_not_leave_approach(tmp_path: Path):
    s = _session(tmp_path)
    app = StarFreightApp(session=s)
    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ApproachScreen(s, _reach_enc()))
        await pilot.pause()
        for key in ("d", "c", "r", "m", "t", "j"):
            await pilot.press(key)
            await pilot.pause()
            assert isinstance(app.screen, ApproachScreen), f"{key} left approach"
