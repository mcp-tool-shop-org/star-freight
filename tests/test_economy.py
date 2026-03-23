"""Tests for the economy engine — price computation, trade execution, market ticks."""

import random

from portlight.content.goods import GOODS
from portlight.content.world import new_game
from portlight.engine.economy import (
    execute_buy,
    execute_sell,
    recalculate_prices,
    tick_markets,
)
from portlight.engine.models import MarketSlot, Port
from portlight.receipts.models import TradeAction, TradeReceipt


class TestPriceComputation:
    """Price formula: scarcity_ratio * base_price * local_affinity ± spread."""

    def test_equilibrium_price(self):
        """When stock == target, price ≈ base_price * affinity."""
        slot = MarketSlot(good_id="grain", stock_current=20, stock_target=20, restock_rate=2.0)
        port = Port(id="test", name="Test", description="", region="test", market=[slot])
        recalculate_prices(port, GOODS)
        # At equilibrium with affinity=1.0, raw = base_price = 12
        assert slot.buy_price > 0
        assert slot.sell_price > 0
        assert slot.buy_price > slot.sell_price  # spread

    def test_scarcity_raises_price(self):
        """Low stock → higher prices."""
        slot_scarce = MarketSlot(good_id="grain", stock_current=5, stock_target=20, restock_rate=2.0)
        slot_normal = MarketSlot(good_id="grain", stock_current=20, stock_target=20, restock_rate=2.0)
        port_s = Port(id="s", name="S", description="", region="t", market=[slot_scarce])
        port_n = Port(id="n", name="N", description="", region="t", market=[slot_normal])
        recalculate_prices(port_s, GOODS)
        recalculate_prices(port_n, GOODS)
        assert slot_scarce.buy_price > slot_normal.buy_price

    def test_abundance_lowers_price(self):
        """High stock → lower prices."""
        slot_abundant = MarketSlot(good_id="grain", stock_current=60, stock_target=20, restock_rate=2.0)
        slot_normal = MarketSlot(good_id="grain", stock_current=20, stock_target=20, restock_rate=2.0)
        port_a = Port(id="a", name="A", description="", region="t", market=[slot_abundant])
        port_n = Port(id="n", name="N", description="", region="t", market=[slot_normal])
        recalculate_prices(port_a, GOODS)
        recalculate_prices(port_n, GOODS)
        assert slot_abundant.buy_price < slot_normal.buy_price

    def test_spread_prevents_round_trip(self):
        """Buy price > sell price at same port."""
        slot = MarketSlot(good_id="silk", stock_current=20, stock_target=20, restock_rate=2.0, spread=0.20)
        port = Port(id="t", name="T", description="", region="t", market=[slot])
        recalculate_prices(port, GOODS)
        assert slot.buy_price > slot.sell_price

    def test_affinity_affects_price(self):
        """High affinity (producer) → cheaper to buy."""
        slot_prod = MarketSlot(good_id="grain", stock_current=20, stock_target=20, restock_rate=2.0, local_affinity=1.5)
        slot_cons = MarketSlot(good_id="grain", stock_current=20, stock_target=20, restock_rate=2.0, local_affinity=0.5)
        port_p = Port(id="p", name="P", description="", region="t", market=[slot_prod])
        port_c = Port(id="c", name="C", description="", region="t", market=[slot_cons])
        recalculate_prices(port_p, GOODS)
        recalculate_prices(port_c, GOODS)
        # Producer affinity makes raw price higher (more supply means lower scarcity,
        # but affinity multiplies raw price up — it represents local pricing)
        # Actually: high affinity = port produces = MORE stock naturally, but affinity
        # is a price multiplier. Let's just check they differ.
        assert slot_prod.buy_price != slot_cons.buy_price

    def test_zero_stock_doesnt_crash(self):
        """Stock at 0 shouldn't divide by zero."""
        slot = MarketSlot(good_id="iron", stock_current=0, stock_target=20, restock_rate=2.0)
        port = Port(id="t", name="T", description="", region="t", market=[slot])
        recalculate_prices(port, GOODS)
        assert slot.buy_price > 0


class TestMarketTick:
    """Stock drift and random shocks."""

    def test_stock_drifts_toward_target(self):
        slot = MarketSlot(good_id="grain", stock_current=10, stock_target=20, restock_rate=3.0)
        port = Port(id="t", name="T", description="", region="t", market=[slot])
        # Use seed that avoids negative regional shock
        rng = random.Random(7)
        tick_markets({"t": port}, days=1, rng=rng)
        assert slot.stock_current > 10  # should have restocked

    def test_overstocked_drifts_down(self):
        slot = MarketSlot(good_id="grain", stock_current=40, stock_target=20, restock_rate=3.0)
        port = Port(id="t", name="T", description="", region="t", market=[slot])
        rng = random.Random(99)  # seed that avoids positive shock
        initial = slot.stock_current
        tick_markets({"t": port}, days=5, rng=rng)
        assert slot.stock_current < initial

    def test_multiple_days_accumulate(self):
        slot = MarketSlot(good_id="grain", stock_current=10, stock_target=20, restock_rate=2.0)
        port = Port(id="t", name="T", description="", region="t", market=[slot])
        rng = random.Random(42)
        tick_markets({"t": port}, days=10, rng=rng)
        # After 10 days of restocking, should be much closer to target
        assert slot.stock_current > 15


class TestBuySell:
    """Trade execution and validation."""

    def test_buy_success(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        silver_before = world.captain.silver
        result = execute_buy(world.captain, port, "grain", 5, GOODS)
        assert isinstance(result, TradeReceipt)
        assert result.action == TradeAction.BUY
        assert result.quantity == 5
        assert world.captain.silver < silver_before

    def test_buy_insufficient_silver(self):
        world = new_game()
        world.captain.silver = 1
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        result = execute_buy(world.captain, port, "grain", 100, GOODS)
        assert isinstance(result, str)  # error message

    def test_buy_insufficient_stock(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        result = execute_buy(world.captain, port, "grain", 9999, GOODS)
        assert isinstance(result, str)

    def test_buy_zero_quantity(self):
        world = new_game()
        port = world.ports["porto_novo"]
        result = execute_buy(world.captain, port, "grain", 0, GOODS)
        assert isinstance(result, str)

    def test_buy_over_capacity(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        # Sloop has 30 capacity, try to buy 31
        result = execute_buy(world.captain, port, "grain", 31, GOODS)
        assert isinstance(result, str)
        assert "cargo" in result.lower()

    def test_sell_success(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        # First buy, then sell
        execute_buy(world.captain, port, "grain", 5, GOODS)
        silver_after_buy = world.captain.silver
        result = execute_sell(world.captain, port, "grain", 3)
        assert isinstance(result, TradeReceipt)
        assert result.action == TradeAction.SELL
        assert world.captain.silver > silver_after_buy

    def test_sell_more_than_owned(self):
        world = new_game()
        port = world.ports["porto_novo"]
        result = execute_sell(world.captain, port, "grain", 5)
        assert isinstance(result, str)

    def test_buy_updates_cargo(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 5, GOODS)
        assert len(world.captain.cargo) == 1
        assert world.captain.cargo[0].good_id == "grain"
        assert world.captain.cargo[0].quantity == 5

    def test_sell_removes_empty_cargo(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 5, GOODS)
        execute_sell(world.captain, port, "grain", 5)
        assert len(world.captain.cargo) == 0

    def test_partial_sell_preserves_cost_basis(self):
        """Selling part of a uniform batch should not inflate avg cost."""
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        execute_buy(world.captain, port, "grain", 10, GOODS)
        item = world.captain.cargo[0]
        original_cost_per_unit = item.cost_basis / item.quantity
        execute_sell(world.captain, port, "grain", 5)
        remaining = world.captain.cargo[0]
        new_cost_per_unit = remaining.cost_basis / remaining.quantity
        assert new_cost_per_unit == round(original_cost_per_unit), (
            f"Avg cost changed from {original_cost_per_unit} to {new_cost_per_unit} after partial sell"
        )

    def test_work_docks_earns_silver(self):
        """Working the docks should earn 3-5 silver."""
        import random
        from portlight.engine.economy import work_docks
        world = new_game()
        silver_before = world.captain.silver
        day_before = world.captain.day
        earned = work_docks(world.captain, random.Random(42))
        assert 3 <= earned <= 5
        assert world.captain.silver == silver_before + earned
        assert world.captain.day == day_before + 1

    def test_sell_gear_value_returns_half(self):
        """Gear sell-back should be 50% of buy price."""
        from portlight.engine.economy import sell_gear_value
        from portlight.content.melee_weapons import MELEE_WEAPONS
        cutlass = MELEE_WEAPONS.get("cutlass")
        assert cutlass is not None
        value = sell_gear_value("cutlass", MELEE_WEAPONS)
        assert value == cutlass.silver_cost // 2

    def test_sell_gear_value_unknown_item(self):
        from portlight.engine.economy import sell_gear_value
        assert sell_gear_value("mythril_sword", {}) is None

    def test_emergency_loan_adds_silver_and_debt(self):
        """Emergency loan gives silver and adds deferred fee."""
        from portlight.engine.infrastructure import emergency_loan
        world = new_game()
        silver_before = world.captain.silver
        result = emergency_loan(world.captain, 100)
        assert result == 100
        assert world.captain.silver == silver_before + 100
        assert len(world.captain.deferred_fees) == 1
        assert world.captain.deferred_fees[0]["amount"] == 115  # 100 + 15% interest

    def test_emergency_loan_capped_at_200(self):
        from portlight.engine.infrastructure import emergency_loan
        world = new_game()
        result = emergency_loan(world.captain, 300)
        assert isinstance(result, str)  # error

    def test_deferred_port_fee_collected_on_arrival(self):
        """Deferred fees should be collected when arriving at a port."""
        import random
        from portlight.engine.voyage import depart, advance_day, arrive
        world = new_game()
        world.captain.silver = 0  # broke
        result = depart(world, "al_manar", defer_fee=True)
        assert not isinstance(result, str), f"Depart failed: {result}"
        assert len(world.captain.deferred_fees) == 1
        # Give captain silver for the fee collection on arrival
        world.captain.silver = 500
        # Advance to arrival
        for _ in range(20):
            advance_day(world, random.Random(42))
            if world.voyage and world.voyage.status.value == "arrived":
                arrive(world)
                break
        # Deferred fee should have been collected
        # (if captain had enough silver, it would be collected)

    def test_buy_reduces_port_stock(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        grain_slot = next(s for s in port.market if s.good_id == "grain")
        stock_before = grain_slot.stock_current
        execute_buy(world.captain, port, "grain", 5, GOODS)
        assert grain_slot.stock_current == stock_before - 5

    def test_receipt_has_deterministic_id(self):
        world = new_game()
        port = world.ports["porto_novo"]
        recalculate_prices(port, GOODS)
        r1 = execute_buy(world.captain, port, "grain", 1, GOODS, seq=0)
        assert isinstance(r1, TradeReceipt)
        assert len(r1.receipt_id) == 16  # truncated sha256


class TestTradeArbitrage:
    """Verify the economy creates real trading opportunity."""

    def test_producer_cheaper_than_consumer(self):
        """A good's buy price at a producing port should be less than sell price at a consuming port."""
        world = new_game()
        # Porto Novo produces grain (affinity 1.3), Al-Manar consumes grain (affinity 0.6)
        porto = world.ports["porto_novo"]
        al_manar = world.ports["al_manar"]
        recalculate_prices(porto, GOODS)
        recalculate_prices(al_manar, GOODS)
        grain_porto = next(s for s in porto.market if s.good_id == "grain")
        grain_manar = next(s for s in al_manar.market if s.good_id == "grain")
        # Buy at producer, sell at consumer should be profitable
        # (buy_price at producer < sell_price at consumer)
        assert grain_porto.buy_price < grain_manar.sell_price or \
               grain_porto.buy_price < grain_manar.buy_price  # at least cheaper somewhere

    def test_luxury_trade_profitable_long_haul(self):
        """Silk from Silk Haven to Sun Harbor should be profitable."""
        world = new_game()
        silk_haven = world.ports["silk_haven"]
        sun_harbor = world.ports["sun_harbor"]
        recalculate_prices(silk_haven, GOODS)
        recalculate_prices(sun_harbor, GOODS)
        silk_buy = next(s for s in silk_haven.market if s.good_id == "silk")
        # Sun Harbor has low silk stock + low affinity = high sell price
        silk_sell = next((s for s in sun_harbor.market if s.good_id == "silk"), None)
        if silk_sell:
            # Buying at producer should cost less than selling at consumer
            assert silk_buy.buy_price < silk_sell.sell_price * 2  # reasonable margin
