"""Economy engine - price computation, stock mutation, trade execution.

Contract:
  - recalculate_prices(port) -> updates all MarketSlot buy/sell prices in place
  - tick_markets(ports, days=1) -> drift all stocks toward target, apply shocks
  - execute_buy(captain, port, good_id, qty) -> TradeReceipt | error string
  - execute_sell(captain, port, good_id, qty) -> TradeReceipt | error string

Price formula (Option 1.5 - lightweight scarcity):
  scarcity_ratio = stock_target / max(stock_current, 1)
  raw_price = base_price * scarcity_ratio / local_affinity
  buy_price  = round(raw_price * (1 + spread / 2))
  sell_price = round(raw_price * (1 - spread / 2) * (1 - flood_penalty))

Anti-dominance:
  - flood_penalty rises when player sells large quantities (diminishing margins)
  - flood_penalty decays over time (market absorbs goods)
  - Stronger restock pulls stock toward target faster
  - Regional shocks occasionally disrupt supply chains
"""

from __future__ import annotations

import hashlib
import random
from typing import TYPE_CHECKING

from portlight.engine.models import CargoItem, GoodCategory, Port, PortFeature
from portlight.receipts.models import TradeAction, TradeReceipt

if TYPE_CHECKING:
    from portlight.engine.captain_identity import PricingModifiers
    from portlight.engine.models import Captain


def recalculate_prices(
    port: Port,
    goods_table: dict[str, object],
    pricing: "PricingModifiers | None" = None,
) -> None:
    """Recompute buy/sell prices for every market slot in a port.

    If pricing modifiers are provided (from captain identity), they affect
    the final buy/sell prices the player sees.
    """
    for slot in port.market:
        good = goods_table.get(slot.good_id)
        if good is None:
            continue
        base = good.base_price  # type: ignore[union-attr]
        scarcity = slot.stock_target / max(slot.stock_current, 1)
        raw = base * scarcity / max(slot.local_affinity, 0.1)

        buy_mult = 1.0
        sell_mult_cap = 1.0
        if pricing:
            buy_mult = pricing.buy_price_mult
            sell_mult_cap = pricing.sell_price_mult
            # Luxury sell bonus for luxury goods
            if pricing.luxury_sell_bonus > 0:
                category = good.category if hasattr(good, "category") else None  # type: ignore[union-attr]
                if category == GoodCategory.LUXURY:
                    sell_mult_cap += pricing.luxury_sell_bonus

        slot.buy_price = max(1, round(raw * (1 + slot.spread / 2) * buy_mult))
        # Flood penalty reduces sell price - dumping the same port tanks your margins
        flood_mult = 1 - slot.flood_penalty * 0.5  # up to 50% sell price reduction
        slot.sell_price = max(1, round(raw * (1 - slot.spread / 2) * flood_mult * sell_mult_cap))


def tick_markets(
    ports: dict[str, Port], days: int = 1, rng: random.Random | None = None,
    current_day: int = 0,
) -> list[str]:
    """Advance all port markets by `days`. Returns list of shock messages (if any).

    If current_day is provided, seasonal demand modifiers are applied.
    """
    rng = rng or random.Random()
    messages: list[str] = []
    for port in ports.values():
        # Get seasonal profile for this port's region
        _seasonal = None
        if current_day > 0:
            from portlight.content.seasons import get_seasonal_profile
            _seasonal = get_seasonal_profile(port.region, current_day)

        for slot in port.market:
            for _ in range(days):
                # Drift toward target (stronger pull when far from target)
                diff = slot.stock_target - slot.stock_current
                if abs(diff) <= 0:
                    pass
                elif abs(diff) > slot.restock_rate:
                    # Proportional restock: faster recovery when further from target
                    pull = slot.restock_rate * (1 + abs(diff) / max(slot.stock_target, 1) * 0.5)
                    pull = pull if diff > 0 else -pull * 0.5
                    slot.stock_current += int(round(pull))
                else:
                    slot.stock_current += diff

                # Flood penalty decay (markets absorb goods over time)
                if slot.flood_penalty > 0:
                    slot.flood_penalty = max(0.0, slot.flood_penalty - 0.05)

                # Random shock (8% chance per day)
                if rng.random() < 0.08:
                    shock = rng.randint(-4, 4)
                    slot.stock_current = max(0, slot.stock_current + shock)

                # Seasonal demand pull (shifts stock target temporarily)
                if _seasonal and slot.good_id in _seasonal.market_effects:
                    demand_mult = _seasonal.market_effects[slot.good_id]
                    if demand_mult > 1.0:
                        # High demand: drain stock faster (consumers buy more)
                        drain = int((demand_mult - 1.0) * slot.restock_rate * 0.5)
                        slot.stock_current = max(0, slot.stock_current - drain)
                    elif demand_mult < 1.0:
                        # Low demand / abundance: stock accumulates
                        surplus = int((1.0 - demand_mult) * slot.restock_rate * 0.5)
                        slot.stock_current += surplus

        # Regional supply shock (3% chance per port per day tick)
        if rng.random() < 0.03 * days:
            shock_slot = rng.choice(port.market) if port.market else None
            if shock_slot:
                direction = rng.choice([-1, 1])
                magnitude = rng.randint(5, 12)
                shock_slot.stock_current = max(0, shock_slot.stock_current + direction * magnitude)
                good_name = shock_slot.good_id
                if direction > 0:
                    messages.append(f"Supply glut: {good_name} floods {port.name}")
                else:
                    messages.append(f"Shortage: {good_name} scarce at {port.name}")

    return messages


def _cargo_slot(captain: Captain, good_id: str) -> CargoItem | None:
    for item in captain.cargo:
        if item.good_id == good_id:
            return item
    return None


def _cargo_weight(captain: Captain) -> float:
    return sum(item.quantity for item in captain.cargo)


def _make_receipt_id(captain_name: str, port_id: str, good_id: str, day: int, seq: int) -> str:
    raw = f"{captain_name}:{port_id}:{good_id}:{day}:{seq}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def execute_buy(
    captain: Captain, port: Port, good_id: str, qty: int,
    goods_table: dict[str, object], seq: int = 0,
) -> TradeReceipt | str:
    """Buy goods from port. Returns TradeReceipt on success, error string on failure."""
    slot = next((s for s in port.market if s.good_id == good_id), None)
    if slot is None:
        # Try matching by display name (case-insensitive) and suggest the correct ID
        for s in port.market:
            g = goods_table.get(s.good_id)
            if g and getattr(g, "name", "").lower().replace(" ", "_") == good_id.lower():
                return f"{good_id} not available at {port.name} -- did you mean: {s.good_id}"
        return f"{good_id} not available at {port.name}"
    if qty <= 0:
        return "Quantity must be positive"
    if qty > slot.stock_current:
        return f"Only {slot.stock_current} units available -- try: buy {good_id} {slot.stock_current}"

    total = slot.buy_price * qty
    if total > captain.silver:
        return f"Need {total} silver, have {captain.silver}"

    # Check cargo capacity (with upgrade bonuses)
    ship = captain.ship
    if ship is None:
        return "No ship"
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolve_cargo_capacity
    effective_capacity = resolve_cargo_capacity(ship, UPGRADES)
    current_weight = _cargo_weight(captain)
    good = goods_table.get(good_id)
    weight_per = good.weight_per_unit if good else 1.0  # type: ignore[union-attr]
    if current_weight + qty * weight_per > effective_capacity:
        return "Not enough cargo space"

    # Execute
    stock_before = slot.stock_current
    captain.silver -= total
    slot.stock_current -= qty

    existing = _cargo_slot(captain, good_id)
    if existing and existing.acquired_port == port.id:
        # Same good from same port — merge into existing stack
        existing.cost_basis += total
        existing.quantity += qty
    else:
        # New provenance lot (different port or first purchase)
        captain.cargo.append(CargoItem(
            good_id=good_id, quantity=qty, cost_basis=total,
            acquired_port=port.id, acquired_region=port.region,
            acquired_day=captain.day,
        ))

    return TradeReceipt(
        receipt_id=_make_receipt_id(captain.name, port.id, good_id, captain.day, seq),
        captain_name=captain.name,
        port_id=port.id,
        good_id=good_id,
        action=TradeAction.BUY,
        quantity=qty,
        unit_price=slot.buy_price,
        total_price=total,
        day=captain.day,
        stock_before=stock_before,
        stock_after=slot.stock_current,
    )


def execute_sell(
    captain: Captain, port: Port, good_id: str, qty: int,
    seq: int = 0,
    goods_table: dict[str, object] | None = None,
) -> TradeReceipt | str:
    """Sell goods to port. Returns TradeReceipt on success, error string on failure."""
    # Contraband sell restriction — BLACK_MARKET ports only
    if goods_table:
        good = goods_table.get(good_id)
        if good and hasattr(good, "category") and good.category == GoodCategory.CONTRABAND:  # type: ignore[union-attr]
            if PortFeature.BLACK_MARKET not in port.features:
                return f"The harbormaster won't touch {good_id}. Try somewhere less official."

    slot = next((s for s in port.market if s.good_id == good_id), None)
    if slot is None:
        return f"{port.name} doesn't trade {good_id}"
    if qty <= 0:
        return "Quantity must be positive"

    existing = _cargo_slot(captain, good_id)
    if existing is None or existing.quantity < qty:
        have = existing.quantity if existing else 0
        return f"Only have {have} units of {good_id}"

    # Anti-exploit: when selling goods back to the SAME port within 3 days of
    # buying, cap the sell price at purchase cost. This prevents buy-drain-sell
    # loops that exploit self-created scarcity (buy all stock at normal price,
    # wait 1 day for anti-exploit to expire, sell back at inflated price).
    same_port_sellback = (
        existing.acquired_port == port.id
        and hasattr(existing, 'acquired_day')
        and (captain.day - existing.acquired_day) <= 3
    )

    # Execute
    stock_before = slot.stock_current
    unit_price = slot.sell_price
    if same_port_sellback and existing.quantity > 0:
        cost_per_unit = existing.cost_basis / existing.quantity
        # Cap: never profit from instant same-port round-trip
        if unit_price > cost_per_unit:
            unit_price = max(1, round(cost_per_unit))
    total = unit_price * qty
    captain.silver += total
    slot.stock_current += qty

    # Increase flood penalty proportional to dump size vs target
    flood_increase = qty / max(slot.stock_target, 1) * 0.3
    slot.flood_penalty = min(1.0, slot.flood_penalty + flood_increase)

    # Update cargo — adjust cost_basis proportionally on partial sell
    if existing.quantity > qty:
        cost_per_unit = existing.cost_basis / existing.quantity
        existing.quantity -= qty
        existing.cost_basis = round(cost_per_unit * existing.quantity)
    else:
        captain.cargo.remove(existing)

    return TradeReceipt(
        receipt_id=_make_receipt_id(captain.name, port.id, good_id, captain.day, seq),
        captain_name=captain.name,
        port_id=port.id,
        good_id=good_id,
        action=TradeAction.SELL,
        quantity=qty,
        unit_price=unit_price,
        total_price=total,
        day=captain.day,
        stock_before=stock_before,
        stock_after=slot.stock_current,
    )


# ---------------------------------------------------------------------------
# Anti-soft-lock: dock work and gear sell-back
# ---------------------------------------------------------------------------

def work_docks(captain: "Captain", rng: random.Random) -> int:
    """Work the docks for a day. Returns silver earned (3-5).

    This is a safety valve for players stranded with no silver and no
    tradeable cargo at the current port.
    """
    earned = rng.randint(3, 5)
    captain.silver += earned
    captain.day += 1
    return earned


def sell_gear_value(item_id: str, weapon_tables: dict[str, object]) -> int | None:
    """Get sell-back price for a weapon/armor item (50% of buy price).

    Returns None if item not found in tables.
    """
    weapon = weapon_tables.get(item_id)
    if weapon is None:
        return None
    price = getattr(weapon, "silver_cost", None) or getattr(weapon, "cost", 0)
    return max(1, price // 2)
