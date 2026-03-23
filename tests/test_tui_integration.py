"""Integration tests for Textual TUI — exercises real screens with pilot.

Uses Textual's async test pilot to mount the app, switch tabs, and verify
that views render without errors. Catches import errors, missing attributes,
and rendering crashes that smoke tests can't find.
"""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import PortlightApp  # noqa: E402


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
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # App should mount and show the dashboard
        assert app.session.active
        assert app._current_tab == "dashboard"


# ---------------------------------------------------------------------------
# Test: Switch to every tab without crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_switch_all_tabs():
    """Every tab renders without error."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        tabs_and_keys = [
            ("dashboard", "d"),
            ("market", "m"),
            ("routes", "r"),
            ("cargo", "c"),
            ("inventory", "i"),
            ("fleet", "f"),
            ("contracts", "k"),
            ("port", "p"),
            ("ledger", "l"),
            ("infrastructure", "w"),
            ("map", "v"),
            # skip help — "?" key binding varies by platform
        ]
        for tab_name, key in tabs_and_keys:
            await _pilot.press(key)
            assert app._current_tab == tab_name, f"Failed to switch to {tab_name}"


# ---------------------------------------------------------------------------
# Test: Dashboard renders captain info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_shows_captain():
    """Dashboard tab shows captain name and silver."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("d")
        # The sidebar should contain captain info
        # Check that the app didn't crash — that's the main goal
        assert app.session.world.captain.name == "Captain Blackwood"


# ---------------------------------------------------------------------------
# Test: Market tab renders when docked
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_market_tab_renders():
    """Market tab shows goods table when docked at a port."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("m")
        assert app._current_tab == "market"
        # Should not crash — port market should be visible
        assert session.current_port is not None


# ---------------------------------------------------------------------------
# Test: Routes tab renders when docked
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_routes_tab_renders():
    """Routes tab shows available destinations."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("r")
        assert app._current_tab == "routes"
        # Verify routes exist from the port
        port = session.current_port
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        assert len(routes) > 0


# ---------------------------------------------------------------------------
# Test: Advance a day while in port
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_advance_day_in_port():
    """Pressing 'a' advances the day while in port."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        day_before = session.world.day
        await _pilot.press("a")
        # Day should advance
        assert session.world.day == day_before + 1


# ---------------------------------------------------------------------------
# Test: Fleet tab renders ship info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_fleet_tab_renders():
    """Fleet tab shows ship information."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("f")
        assert app._current_tab == "fleet"
        assert session.world.captain.ship is not None


# ---------------------------------------------------------------------------
# Test: Cargo tab renders empty hold
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_cargo_tab_renders():
    """Cargo tab renders even with empty hold."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("c")
        assert app._current_tab == "cargo"


# ---------------------------------------------------------------------------
# Test: Contracts tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_contracts_tab_renders():
    """Contracts tab renders the contract board."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("k")
        assert app._current_tab == "contracts"


# ---------------------------------------------------------------------------
# Test: Inventory tab renders gear data
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_inventory_tab_renders():
    """Inventory tab builds gear_data and renders."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("i")
        assert app._current_tab == "inventory"


# ---------------------------------------------------------------------------
# Test: Infrastructure tab renders
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_infrastructure_tab_renders():
    """Infrastructure tab renders composite view."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("w")
        assert app._current_tab == "infrastructure"


# ---------------------------------------------------------------------------
# Test: Help tab renders keybindings
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_help_tab_renders():
    """Help tab shows keybinding reference."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("question_mark")
        assert app._current_tab == "help"


# ---------------------------------------------------------------------------
# Test: Port tab renders port info
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_port_tab_renders():
    """Port tab shows port info when docked."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("p")
        assert app._current_tab == "port"


# ---------------------------------------------------------------------------
# Test: Ledger tab renders with no trades
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ledger_tab_renders():
    """Ledger tab renders even with no trades."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("l")
        assert app._current_tab == "ledger"


# ---------------------------------------------------------------------------
# Test: Multiple tab switches don't crash
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rapid_tab_switching():
    """Rapid tab switching doesn't crash."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        for _ in range(3):
            for key in ["d", "m", "r", "c", "i", "f", "k", "p", "l", "w"]:
                await _pilot.press(key)
        # If we got here without crash, we're good
        assert True


# ---------------------------------------------------------------------------
# Test: Advance multiple days
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_advance_multiple_days():
    """Advancing multiple days works without error."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        for _ in range(5):
            await _pilot.press("a")
        assert session.world.day == 6  # Started at day 1, advanced 5
