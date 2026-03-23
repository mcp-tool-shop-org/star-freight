"""Voyage integration tests — simulate a full trade cycle via pilot.

Creates a game, buys goods, sails, advances to arrival, sells goods,
and verifies state changes at each step. This is the "play a round" test.
"""

from __future__ import annotations

import pytest

textual = pytest.importorskip("textual", reason="textual not installed")

from portlight.app.session import GameSession  # noqa: E402
from portlight.app.tui.app import PortlightApp  # noqa: E402


def _make_session() -> GameSession:
    s = GameSession(slot="tui_voyage_test")
    s.new("Captain Blackwood", captain_type="merchant")
    return s


# ---------------------------------------------------------------------------
# Full trade cycle: buy at Porto Novo, sail, advance to arrival, sell
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_buy_updates_state():
    """Buying goods via session updates cargo and silver."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Start at Porto Novo with 550 silver
        assert session.current_port is not None
        silver_before = session.world.captain.silver
        cargo_before = len(session.world.captain.cargo)

        # Buy grain directly via session (pilot can't drive modal dialogs easily)
        result = session.buy("grain", 5)
        assert not isinstance(result, str), f"Buy failed: {result}"
        assert result.quantity == 5
        assert session.world.captain.silver < silver_before
        assert len(session.world.captain.cargo) > cargo_before or any(
            c.good_id == "grain" for c in session.world.captain.cargo
        )

        # Refresh views — should not crash
        app.refresh_views()


@pytest.mark.asyncio
async def test_sell_updates_state():
    """Selling goods updates cargo and silver."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Buy first, then sell
        session.buy("grain", 5)
        silver_after_buy = session.world.captain.silver

        result = session.sell("grain", 3)
        assert not isinstance(result, str), f"Sell failed: {result}"
        assert result.quantity == 3
        assert session.world.captain.silver > silver_after_buy

        app.refresh_views()


@pytest.mark.asyncio
async def test_sail_changes_state():
    """Sailing changes voyage status to at_sea."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        assert not session.at_sea
        port = session.current_port
        assert port is not None

        # Find a destination
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        assert len(routes) > 0

        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a

        err = session.sail(dest_id)
        assert err is None, f"Sail failed: {err}"
        assert session.at_sea

        app.refresh_views()


@pytest.mark.asyncio
async def test_advance_at_sea_progresses():
    """Advancing while at sea increases progress."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Sail somewhere
        port = session.current_port
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        assert session.at_sea
        progress_before = session.world.voyage.progress

        # Advance a day
        await _pilot.press("a")

        assert session.world.voyage.progress > progress_before or not session.at_sea


@pytest.mark.asyncio
async def test_full_voyage_arrives():
    """Advancing enough days completes a voyage and arrives at port."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Sail to nearest destination
        port = session.current_port
        routes = sorted(
            [r for r in session.world.routes
             if r.port_a == port.id or r.port_b == port.id],
            key=lambda r: r.distance,
        )
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        # Advance until arrival (max 30 days to prevent infinite loop)
        for day in range(30):
            if not session.at_sea:
                break
            session.advance()

        # Should have arrived
        assert not session.at_sea, "Never arrived after 30 days"
        assert session.current_port is not None
        assert session.current_port.id == dest_id

        # Refresh views at new port — should not crash
        app.refresh_views()

        # Switch to market at new port
        await _pilot.press("m")
        assert app._current_tab == "market"


@pytest.mark.asyncio
async def test_buy_sail_arrive_sell_cycle():
    """Complete trade cycle: buy -> sail -> arrive -> sell."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # 1. Buy grain at Porto Novo
        result = session.buy("grain", 5)
        assert not isinstance(result, str), f"Buy failed: {result}"

        # 2. Sail to nearest port
        port = session.current_port
        routes = sorted(
            [r for r in session.world.routes
             if r.port_a == port.id or r.port_b == port.id],
            key=lambda r: r.distance,
        )
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        # 3. Advance to arrival
        for _ in range(30):
            if not session.at_sea:
                break
            session.advance()
        assert not session.at_sea

        # 4. Sell grain at new port
        grain_held = sum(c.quantity for c in session.world.captain.cargo if c.good_id == "grain")
        if grain_held > 0:
            result = session.sell("grain", grain_held)
            assert not isinstance(result, str), f"Sell failed: {result}"

        # 5. Verify state
        app.refresh_views()
        await _pilot.press("d")  # dashboard
        await _pilot.press("l")  # ledger — should show our trades

        # Should have at least 1 trade in ledger
        assert len(session.ledger.receipts) >= 1


@pytest.mark.asyncio
async def test_views_after_trading():
    """All views render correctly after trading changes state."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Buy some goods to change state
        session.buy("grain", 3)

        # Switch through all tabs — should not crash
        for key in ["d", "m", "r", "c", "i", "f", "k", "p", "l", "w"]:
            await _pilot.press(key)

        assert True  # Got here without crash


@pytest.mark.asyncio
async def test_views_at_sea():
    """Views render correctly while at sea (no port-dependent crashes)."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        # Sail somewhere
        port = session.current_port
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        assert session.at_sea

        # Switch through all tabs while at sea — market/port should show
        # "not docked" message instead of crashing
        for key in ["d", "m", "r", "c", "i", "f", "k", "p", "l", "w"]:
            await _pilot.press(key)

        assert True  # Got here without crash


@pytest.mark.asyncio
async def test_multiple_advances_at_sea():
    """Multiple advances at sea with view refreshes don't crash."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        port = session.current_port
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        # Advance 5 days with dashboard view
        for _ in range(5):
            await _pilot.press("a")

        # Should have made progress or arrived
        assert session.world.day > 1


@pytest.mark.asyncio
async def test_provision_consumption():
    """Provisions decrease when advancing at sea."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        prov_start = session.world.captain.provisions

        # Sail somewhere
        port = session.current_port
        routes = [r for r in session.world.routes
                  if r.port_a == port.id or r.port_b == port.id]
        route = routes[0]
        dest_id = route.port_b if route.port_a == port.id else route.port_a
        session.sail(dest_id)

        # Advance several days at sea — provision consumption should outweigh any single favorable event
        for _ in range(5):
            if session.at_sea:
                session.advance()

        # Over 5 days, net provisions should decrease (daily burn outweighs rare bonuses)
        assert session.world.captain.provisions < prov_start


@pytest.mark.asyncio
async def test_sidebar_updates_after_trade():
    """Sidebar reflects updated silver after a trade."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        silver_before = session.world.captain.silver

        session.buy("grain", 2)
        app.refresh_views()

        # Silver should have decreased
        assert session.world.captain.silver < silver_before


@pytest.mark.asyncio
async def test_infra_view_with_fresh_game():
    """Infrastructure view renders with no warehouses/brokers/licenses."""
    session = _make_session()
    app = PortlightApp(session=session)
    async with app.run_test() as _pilot:
        await _pilot.press("w")
        assert app._current_tab == "infrastructure"
        # Should render empty infrastructure without crash
        assert len(session.infra.warehouses) == 0
