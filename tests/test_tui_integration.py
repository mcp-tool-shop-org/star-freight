"""Integration tests for Star Freight TUI — exercises real screens with pilot.

Uses Textual's async test pilot to mount the app, switch tabs, and verify
that views render without errors. Catches import errors, missing attributes,
and rendering crashes that smoke tests can't find.
"""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import StarFreightApp  # noqa: E402


def _make_session() -> GameSession:
    """Create a fresh game session for testing."""
    s = GameSession(slot="tui_integration_test")
    s.new("Captain Blackwood", captain_type="merchant")
    return s


# ---------------------------------------------------------------------------
# Test: App mounts and shows dashboard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_app_mounts():
    """App mounts without errors and shows dashboard."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        assert app.session.active
        assert app._current_tab == "dashboard"


# ---------------------------------------------------------------------------
# Test: Switch to every Star Freight tab without crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_switch_all_tabs():
    """Every Star Freight tab renders without error."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        tabs_and_keys = [
            ("dashboard", "d"),
            ("crew", "c"),
            ("routes", "r"),
            ("market", "m"),
            ("station", "t"),
            ("journal", "j"),
            ("faction", "f"),
        ]
        for tab_name, key in tabs_and_keys:
            await _pilot.press(key)
            assert app._current_tab == tab_name, f"Failed to switch to {tab_name}"


# ---------------------------------------------------------------------------
# Test: Dashboard renders captain info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_shows_captain():
    """Dashboard tab renders Star Freight campaign state."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("d")
        # The captain bar should render SF campaign state
        assert session.sf_campaign.credits > 0


# ---------------------------------------------------------------------------
# Test: Market tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_market_tab_renders():
    """Market tab renders Star Freight goods."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("m")
        assert app._current_tab == "market"


# ---------------------------------------------------------------------------
# Test: Routes tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_routes_tab_renders():
    """Routes tab shows available lanes."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("r")
        assert app._current_tab == "routes"


# ---------------------------------------------------------------------------
# Test: Crew tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crew_tab_renders():
    """Crew tab shows crew roster."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("c")
        assert app._current_tab == "crew"


# ---------------------------------------------------------------------------
# Test: Station tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_station_tab_renders():
    """Station tab shows current station info."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("t")
        assert app._current_tab == "station"


# ---------------------------------------------------------------------------
# Test: Journal tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_journal_tab_renders():
    """Journal tab shows investigation fragments."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("j")
        assert app._current_tab == "journal"


# ---------------------------------------------------------------------------
# Test: Faction tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_faction_tab_renders():
    """Faction tab shows reputation standings."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("f")
        assert app._current_tab == "faction"


# ---------------------------------------------------------------------------
# Test: Help tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_help_tab_renders():
    """Help tab shows Star Freight keybinding reference."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("question_mark")
        assert app._current_tab == "help"


# ---------------------------------------------------------------------------
# Test: Multiple tab switches don't crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rapid_tab_switching():
    """Rapid tab switching doesn't crash."""
    session = _make_session()
    app = StarFreightApp(session=session)
    async with app.run_test() as _pilot:
        for _ in range(3):
            for key in ["d", "c", "r", "m", "t", "j", "f"]:
                await _pilot.press(key)
        assert True
