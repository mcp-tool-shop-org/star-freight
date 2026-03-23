"""Tests for bug fixes discovered during playtesting session.

Bug #1: No contracts at starting port on new game
Bug #2: No port fee warning when buying cargo
Bug #3: Sail command rejects display names
Bug #4: Buy-drain-sell exploit via scarcity pricing
Bug #5: Repeated atmospheric text on consecutive days
Bug #7: hire/fire asymmetric argument order
Bug #8: buy grain -5 typer crash
Bug #9: Guide command misleading syntax
Bug #10: Same arrival weather for all Med ports
Bug #11: No hint where to sell pelts
Hunting expansion: silver, dangers, consequences
"""

from __future__ import annotations

import random
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Bug #4: Same-day same-port sell should not profit from self-created scarcity
# ---------------------------------------------------------------------------

class TestBuyDrainSellExploit:
    def _make_world(self):
        from portlight.content.world import new_game
        from portlight.engine.captain_identity import CaptainType
        return new_game("Tester", captain_type=CaptainType.MERCHANT)

    def test_same_day_sellback_capped_at_cost(self):
        """Buying stock then selling back same day should not profit."""
        from portlight.content.goods import GOODS
        from portlight.engine.economy import execute_buy, execute_sell, recalculate_prices

        world = self._make_world()
        captain = world.captain
        captain.silver = 5000  # enough to buy plenty
        port = next(iter(world.ports.values()))
        recalculate_prices(port, GOODS)

        # Find a cheap good and buy a reasonable amount
        slot = port.market[0]
        good_id = slot.good_id
        qty = min(slot.stock_current, 10)  # don't exceed cargo

        # Buy
        result = execute_buy(captain, port, good_id, qty, GOODS)
        assert not isinstance(result, str), f"Buy failed: {result}"
        spent = result.total_price

        # Recalculate prices (scarcity should spike)
        recalculate_prices(port, GOODS)

        # Sell back same day
        result = execute_sell(captain, port, good_id, qty, goods_table=GOODS)
        assert not isinstance(result, str), f"Sell failed: {result}"
        earned = result.total_price

        # Should NOT profit from the round trip
        assert earned <= spent, (
            f"Same-day sellback profited: spent {spent}, earned {earned}"
        )

    def test_next_day_sellback_still_capped(self):
        """Buying stock then selling back 1 day later should not profit.

        Regression: the original same-day check could be bypassed by using
        'work' or 'advance' to tick 1 day before selling back.
        """
        from portlight.content.goods import GOODS
        from portlight.engine.economy import execute_buy, execute_sell, recalculate_prices

        world = self._make_world()
        captain = world.captain
        captain.silver = 5000
        port = next(iter(world.ports.values()))
        recalculate_prices(port, GOODS)

        slot = port.market[0]
        good_id = slot.good_id
        qty = min(slot.stock_current, 10)

        # Buy on day 1
        result = execute_buy(captain, port, good_id, qty, GOODS)
        assert not isinstance(result, str), f"Buy failed: {result}"
        spent = result.total_price

        # Advance 1 day (simulating 'work' or 'advance')
        captain.day += 1
        recalculate_prices(port, GOODS)

        # Sell back next day — should still be capped
        result = execute_sell(captain, port, good_id, qty, goods_table=GOODS)
        assert not isinstance(result, str), f"Sell failed: {result}"
        earned = result.total_price

        assert earned <= spent, (
            f"Next-day sellback profited: spent {spent}, earned {earned}"
        )

    def test_sellback_expires_after_window(self):
        """After 4+ days, same-port sellback cap no longer applies."""
        from portlight.content.goods import GOODS
        from portlight.engine.economy import execute_buy, execute_sell, recalculate_prices

        world = self._make_world()
        captain = world.captain
        captain.silver = 5000
        port = next(iter(world.ports.values()))
        recalculate_prices(port, GOODS)

        slot = port.market[0]
        good_id = slot.good_id
        qty = min(slot.stock_current, 10)

        # Buy on day 1
        result = execute_buy(captain, port, good_id, qty, GOODS)
        assert not isinstance(result, str), f"Buy failed: {result}"

        # Advance 4 days — outside the 3-day window
        captain.day += 4
        recalculate_prices(port, GOODS)

        # Sell back — should use market price, not capped
        result = execute_sell(captain, port, good_id, qty, goods_table=GOODS)
        assert not isinstance(result, str), f"Sell failed: {result}"
        assert result.unit_price == slot.sell_price, (
            f"Expected market price {slot.sell_price}, got {result.unit_price}"
        )

    def test_cross_port_sell_not_affected(self):
        """Selling at a different port should use normal market price."""
        from portlight.content.goods import GOODS
        from portlight.engine.economy import execute_buy, execute_sell, recalculate_prices

        world = self._make_world()
        captain = world.captain
        ports = list(world.ports.values())
        port_a = ports[0]
        port_b = ports[1]
        recalculate_prices(port_a, GOODS)
        recalculate_prices(port_b, GOODS)

        # Buy at port A
        slot_a = port_a.market[0]
        good_id = slot_a.good_id
        result = execute_buy(captain, port_a, good_id, 3, GOODS)
        assert not isinstance(result, str)

        # Sell at port B (different port — no cap)
        slot_b = next((s for s in port_b.market if s.good_id == good_id), None)
        if slot_b is None:
            pytest.skip(f"Port B doesn't trade {good_id}")
        recalculate_prices(port_b, GOODS)
        result = execute_sell(captain, port_b, good_id, 3, goods_table=GOODS)
        assert not isinstance(result, str)
        # Unit price should be the market sell price, not capped
        assert result.unit_price == slot_b.sell_price


# ---------------------------------------------------------------------------
# Bug #3: Sail command should accept display names
# ---------------------------------------------------------------------------

class TestSailFuzzyMatch:
    def test_sail_accepts_display_name(self):
        """sail 'Jade Port' should work, not just 'jade_port'."""
        from portlight.app.session import GameSession

        with tempfile.TemporaryDirectory() as tmp:
            s = GameSession(Path(tmp))
            s.new("Tester", captain_type="merchant")
            s.captain.silver = 1000

            # Find a reachable port via routes
            current = s.world.voyage.destination_id
            target = None
            for route in s.world.routes:
                if route.port_a == current:
                    target = route.port_b
                    break
                elif route.port_b == current:
                    target = route.port_a
                    break
            if target is None:
                pytest.skip("No reachable port found")

            display_name = s.world.ports[target].name
            err = s.sail(display_name)
            # May fail due to ship class restrictions, that's ok — but
            # should NOT fail with "No route" if fuzzy matching works
            if err:
                assert "No route" not in err, f"Fuzzy match failed: {err}"

    def test_sail_accepts_partial_name(self):
        """sail 'monsoon' should match 'Monsoon Reach' if unique."""
        from portlight.app.session import GameSession

        with tempfile.TemporaryDirectory() as tmp:
            s = GameSession(Path(tmp))
            s.new("Tester", captain_type="merchant")
            s.captain.silver = 1000

            current = s.world.voyage.destination_id
            for route in s.world.routes:
                pid = route.port_b if route.port_a == current else (
                    route.port_a if route.port_b == current else None
                )
                if pid is None:
                    continue
                port = s.world.ports[pid]
                # Use first word of display name as partial
                partial = port.name.split()[0].lower()
                # Check uniqueness among ALL ports
                matches = [
                    p for p in s.world.ports.values()
                    if partial in p.name.lower()
                ]
                if len(matches) == 1:
                    err = s.sail(partial)
                    if err:
                        assert "No route" not in err, f"Partial match failed: {err}"
                    return
            pytest.skip("No unique partial match found")


# ---------------------------------------------------------------------------
# Bug #5: Repeated atmospheric text dedup
# ---------------------------------------------------------------------------

class TestSeaCultureDedup:
    def test_is_recent_catches_duplicates(self):
        from portlight.engine.sea_culture_engine import _is_recent

        recent = [
            "The light in the East Indies is different from anywhere else."
        ]
        assert _is_recent(
            "The light in the East Indies is different from anywhere else.",
            recent,
        )

    def test_is_recent_allows_new_text(self):
        from portlight.engine.sea_culture_engine import _is_recent

        recent = ["Some other weather text about storms."]
        assert not _is_recent(
            "The light in the East Indies is different from anywhere else.",
            recent,
        )


# ---------------------------------------------------------------------------
# Bug #1: Contracts at starting port
# ---------------------------------------------------------------------------

class TestStartingPortContracts:
    def test_new_game_has_contracts(self):
        """New game should have contract offers at starting port on first access."""
        from portlight.app.session import GameSession

        with tempfile.TemporaryDirectory() as tmp:
            s = GameSession(Path(tmp))
            s.new("Tester", captain_type="merchant")
            # Board uses lazy refresh — trigger it
            port = s.current_port
            assert port is not None
            s._refresh_board(port)
            assert s.board.last_refresh_day == 1
            assert len(s.board.offers) > 0, "Starting port must generate at least one contract offer"

    def test_all_captain_types_get_contracts(self):
        """Every captain type should get at least one contract at their start port."""
        from portlight.app.session import GameSession

        captain_types = [
            "merchant", "smuggler", "navigator", "privateer",
            "corsair", "scholar", "merchant_prince", "dockhand",
            "bounty_hunter",
        ]
        for ctype in captain_types:
            with tempfile.TemporaryDirectory() as tmp:
                s = GameSession(Path(tmp))
                s.new("Tester", captain_type=ctype)
                port = s.current_port
                assert port is not None, f"{ctype}: no starting port"
                s._refresh_board(port)
                assert len(s.board.offers) > 0, (
                    f"{ctype} at {port.name}: no contracts generated"
                )


# ---------------------------------------------------------------------------
# Hunting expansion
# ---------------------------------------------------------------------------

class TestHuntingExpansion:
    def test_hunt_result_has_silver_field(self):
        from portlight.engine.hunting import HuntResult
        r = HuntResult(success=True, silver_gained=5)
        assert r.silver_gained == 5

    def test_hunt_result_has_danger_fields(self):
        from portlight.engine.hunting import HuntResult
        r = HuntResult(success=False, crew_lost=1, hull_damage=3, danger_text="Shark!")
        assert r.crew_lost == 1
        assert r.hull_damage == 3
        assert r.danger_text == "Shark!"

    def test_port_hunt_is_safe(self):
        """Port hunting should never cause crew loss or hull damage."""
        from portlight.engine.hunting import hunt
        from portlight.engine.models import Captain

        captain = Captain.__new__(Captain)
        captain.day = 1

        for seed in range(100):
            captain.day = 1
            result = hunt(captain, "port", 5, random.Random(seed))
            assert result.crew_lost == 0
            assert result.hull_damage == 0
            assert result.danger_text == ""

    def test_sea_hunt_can_yield_silver(self):
        """Sea hunting should sometimes yield silver."""
        from portlight.engine.hunting import hunt
        from portlight.engine.models import Captain

        silver_seen = False
        for seed in range(200):
            captain = Captain.__new__(Captain)
            captain.day = 1
            result = hunt(captain, "sea", 5, random.Random(seed))
            if result.silver_gained > 0:
                silver_seen = True
                break

        assert silver_seen, "No silver earned in 200 sea hunts"

    def test_sea_hunt_can_have_dangers(self):
        """Sea hunting should sometimes trigger dangers."""
        from portlight.engine.hunting import hunt
        from portlight.engine.models import Captain

        danger_seen = False
        for seed in range(200):
            captain = Captain.__new__(Captain)
            captain.day = 1
            result = hunt(captain, "sea", 5, random.Random(seed))
            if result.danger_text:
                danger_seen = True
                break

        assert danger_seen, "No danger encountered in 200 sea hunts"


# ---------------------------------------------------------------------------
# Bug #8: buy grain -5 should give friendly error, not typer crash
# ---------------------------------------------------------------------------

class TestNegativeQuantityBuy:
    def test_buy_zero_returns_error(self):
        """Buying with qty=0 should return a friendly error."""
        from portlight.content.goods import GOODS
        from portlight.content.world import new_game
        from portlight.engine.economy import execute_buy

        world = new_game()
        captain = world.captain
        captain.silver = 5000
        port = next(iter(world.ports.values()))
        good_id = port.market[0].good_id
        result = execute_buy(captain, port, good_id, 0, GOODS)
        assert isinstance(result, str)
        assert "positive" in result.lower()

    def test_buy_negative_returns_error(self):
        """Buying with negative qty should return a friendly error."""
        from portlight.content.goods import GOODS
        from portlight.content.world import new_game
        from portlight.engine.economy import execute_buy

        world = new_game()
        captain = world.captain
        captain.silver = 5000
        port = next(iter(world.ports.values()))
        good_id = port.market[0].good_id
        result = execute_buy(captain, port, good_id, -5, GOODS)
        assert isinstance(result, str)
        assert "positive" in result.lower()


# ---------------------------------------------------------------------------
# Bug #10: Arrival weather should include port name
# ---------------------------------------------------------------------------

class TestArrivalWeatherPortName:
    def test_arrival_weather_contains_port_name(self):
        """get_arrival_weather with port_name should inject it into text."""
        from portlight.engine.sea_culture_engine import get_arrival_weather
        # Day 1 = spring; Mediterranean spring starts with "The port appears"
        text = get_arrival_weather("Mediterranean", 1, "Genoa")
        assert text.startswith("Genoa"), f"Expected port name at start: {text[:50]}"
        assert "The port" not in text

    def test_arrival_weather_without_port_name_unchanged(self):
        """get_arrival_weather without port_name should return original text."""
        from portlight.engine.sea_culture_engine import get_arrival_weather
        from portlight.content.sea_culture import get_weather_narrative
        text = get_arrival_weather("Mediterranean", 1)
        narrative = get_weather_narrative("Mediterranean", "spring")
        assert text == narrative.arrival_text

    def test_all_regions_arrival_text_replaceable(self):
        """Every arrival_text should start with a known subject phrase."""
        from portlight.content.sea_culture import WEATHER_NARRATIVES
        subjects = [
            "The northern port", "The island port", "The port",
            "The island", "The harbor", "The lagoon",
        ]
        for key, narrative in WEATHER_NARRATIVES.items():
            matched = any(narrative.arrival_text.startswith(s) for s in subjects)
            assert matched, (
                f"Arrival text for {key} doesn't start with a known subject: "
                f"{narrative.arrival_text[:60]}"
            )
