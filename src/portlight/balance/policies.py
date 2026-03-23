"""Policy bots — deterministic strategy instruments for balance calibration.

These are not AI opponents. They are calibration instruments that generate
comparable commercial behavior across the same world conditions.

Each policy makes decisions using visible game state only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from portlight.balance.types import PolicyId

if TYPE_CHECKING:
    from portlight.app.session import GameSession


# ---------------------------------------------------------------------------
# Action types
# ---------------------------------------------------------------------------

@dataclass
class ActionPlan:
    """What the policy bot wants to do this turn."""
    action: str                     # "buy", "sell", "sail", "provision", "repair",
                                    # "hire", "accept_contract", "lease_warehouse",
                                    # "open_broker", "buy_license", "buy_insurance",
                                    # "open_credit", "draw_credit", "repay_credit",
                                    # "advance", "wait"
    args: dict = None

    def __post_init__(self):
        if self.args is None:
            self.args = {}


# ---------------------------------------------------------------------------
# Policy interface
# ---------------------------------------------------------------------------

def choose_actions(session: "GameSession", policy_id: PolicyId) -> list[ActionPlan]:
    """Return a prioritized list of actions for this turn.

    The runner executes actions in order until one succeeds or all are tried.
    Multiple actions can succeed per turn (e.g., buy then sail).
    """
    dispatch = {
        PolicyId.LAWFUL_CONSERVATIVE: _lawful_conservative,
        PolicyId.OPPORTUNISTIC_TRADER: _opportunistic_trader,
        PolicyId.CONTRACT_FORWARD: _contract_forward,
        PolicyId.INFRASTRUCTURE_FORWARD: _infrastructure_forward,
        PolicyId.LEVERAGE_FORWARD: _leverage_forward,
        PolicyId.SHADOW_RUNNER: _shadow_runner,
        PolicyId.LONG_HAUL_OPTIMIZER: _long_haul_optimizer,
    }
    fn = dispatch[policy_id]
    return fn(session)


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _best_buy(session: "GameSession", max_spend_pct: float = 0.6) -> ActionPlan | None:
    """Find the best good to buy based on margin potential."""
    port = session.current_port
    if not port:
        return None
    captain = session.captain
    ship = captain.ship
    if not ship:
        return None

    cargo_used = sum(c.quantity for c in captain.cargo)
    space = ship.cargo_capacity - int(cargo_used)
    if space <= 0:
        return None

    budget = int(captain.silver * max_spend_pct)
    if budget <= 0:
        return None

    best_good = None
    best_score = 0

    for slot in port.market:
        if slot.buy_price <= 0 or slot.stock_current <= 0:
            continue
        affordable = min(budget // slot.buy_price, slot.stock_current, space)
        if affordable <= 0:
            continue

        # Score: how much margin upside exists
        # Low affinity = port consumes, so buying cheap here means selling expensive elsewhere
        # High stock / target ratio = cheaper now
        ratio = slot.stock_current / max(slot.stock_target, 1)
        score = ratio * (1.0 / max(slot.local_affinity, 0.3))
        if score > best_score:
            best_score = score
            best_good = (slot.good_id, min(affordable, space))

    if best_good:
        return ActionPlan("buy", {"good": best_good[0], "qty": best_good[1]})
    return None


def _best_sell(session: "GameSession", min_margin: float = 0.0) -> ActionPlan | None:
    """Find the best good to sell at current port."""
    port = session.current_port
    if not port:
        return None
    captain = session.captain
    if not captain.cargo:
        return None

    best = None
    best_margin = min_margin

    for item in captain.cargo:
        slot = next((s for s in port.market if s.good_id == item.good_id), None)
        if not slot or slot.sell_price <= 0:
            continue
        avg_cost = item.cost_basis / item.quantity if item.quantity > 0 else 1
        margin = (slot.sell_price - avg_cost) / max(avg_cost, 1)
        if margin > best_margin:
            best_margin = margin
            best = (item.good_id, item.quantity)

    if best:
        return ActionPlan("sell", {"good": best[0], "qty": best[1]})
    return None


def _best_route(session: "GameSession", prefer_long: bool = False) -> str | None:
    """Pick the best destination to sail to.

    Contract-aware: destinations that fulfill active contracts get a large
    score bonus so bots actually complete contracts they've accepted.
    """
    if session.at_sea or not session.current_port:
        return None
    world = session.world
    port_id = session.current_port.id
    captain = session.captain
    ship = captain.ship
    if not ship:
        return None

    from portlight.content.ships import SHIPS
    ship_class = SHIPS.get(ship.template_id)
    if not ship_class:
        return None

    # Pre-compute contract destinations and what goods we hold for them
    contract_dest_scores: dict[str, float] = {}
    for contract in session.board.active:
        remaining = contract.required_quantity - contract.delivered_quantity
        if remaining <= 0:
            continue
        held = sum(c.quantity for c in captain.cargo if c.good_id == contract.good_id)
        if held > 0:
            # Strong incentive: we have cargo and a destination to deliver to
            urgency = 1.0 + max(0.0, 1.0 - (contract.deadline_day - world.day) / 15.0)
            contract_dest_scores[contract.destination_port_id] = (
                contract_dest_scores.get(contract.destination_port_id, 0.0)
                + held * urgency * 5.0
            )

    candidates = []
    for route in world.routes:
        if route.port_a == port_id:
            dest = route.port_b
        elif route.port_b == port_id:
            dest = route.port_a
        else:
            continue

        # Check ship class requirement
        class_order = {"sloop": 0, "cutter": 1, "brigantine": 2, "galleon": 3, "man_of_war": 4}
        if class_order.get(ship_class.ship_class.value, 0) < class_order.get(route.min_ship_class, 0):
            continue

        # Check provisions
        travel_days = max(1, round(route.distance / ship.speed))
        if captain.provisions < travel_days + 3:
            continue

        # Score destination by sell opportunity
        dest_port = world.ports.get(dest)
        if not dest_port:
            continue

        score = 0.0
        for item in captain.cargo:
            slot = next((s for s in dest_port.market if s.good_id == item.good_id), None)
            if slot:
                ratio = slot.stock_target / max(slot.stock_current, 1)
                score += ratio * item.quantity

        # Contract delivery bonus (large — completing contracts is high value)
        score += contract_dest_scores.get(dest, 0.0)

        # Distance bonus/penalty
        if prefer_long:
            score += route.distance * 0.1
        else:
            score -= route.distance * 0.02

        candidates.append((dest, score))

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def _should_provision(session: "GameSession", min_days: int = 12) -> ActionPlan | None:
    """Provision if low."""
    captain = session.captain
    if captain.provisions < min_days and session.current_port:
        days = max(15, min_days + 5) - captain.provisions
        cost = days * session.current_port.provision_cost
        if cost <= captain.silver * 0.15:
            return ActionPlan("provision", {"days": days})
    return None


def _should_repair(session: "GameSession") -> ActionPlan | None:
    """Repair if damaged."""
    captain = session.captain
    ship = captain.ship
    if not ship or not session.current_port:
        return None
    if ship.hull < ship.hull_max * 0.7:
        return ActionPlan("repair", {})
    return None


def _should_hire(session: "GameSession") -> ActionPlan | None:
    """Hire sailors if undermanned (below crew_min + 2)."""
    captain = session.captain
    ship = captain.ship
    if not ship or not session.current_port:
        return None
    from portlight.content.ships import SHIPS
    template = SHIPS.get(ship.template_id)
    if template and ship.crew < template.crew_min + 2:
        return ActionPlan("hire", {"count": 99, "role": "sailor"})
    return None


def _should_sell_fleet_ship(session: "GameSession") -> ActionPlan | None:
    """Sell any docked fleet ships to reduce wage burn."""
    captain = session.captain
    port = session.current_port
    if not port or not captain.fleet:
        return None
    from portlight.engine.models import PortFeature
    if PortFeature.SHIPYARD not in port.features:
        return None
    for owned in captain.fleet:
        if owned.docked_port_id == port.id and not owned.cargo:
            return ActionPlan("sell_fleet_ship", {"ship_name": owned.ship.name})
    return None


def _should_upgrade_ship(session: "GameSession") -> ActionPlan | None:
    """Buy a better ship if affordable and at a shipyard."""
    port = session.current_port
    if not port:
        return None
    from portlight.engine.models import PortFeature
    if PortFeature.SHIPYARD not in port.features:
        return None
    captain = session.captain
    ship = captain.ship
    if not ship:
        return None

    from portlight.content.ships import SHIPS
    current = SHIPS.get(ship.template_id)
    if not current:
        return None

    class_order = {"sloop": 0, "cutter": 1, "brigantine": 2, "galleon": 3, "man_of_war": 4}
    current_rank = class_order.get(current.ship_class.value, 0)

    for sid, tmpl in SHIPS.items():
        rank = class_order.get(tmpl.ship_class.value, 0)
        if rank == current_rank + 1 and tmpl.price <= captain.silver * 0.8:
            return ActionPlan("buy_ship", {"ship_id": sid})
    return None


def _should_install_upgrade(session: "GameSession", prefer_categories: list[str] | None = None) -> ActionPlan | None:
    """Install a ship upgrade if at a shipyard with slots and silver."""
    port = session.current_port
    if not port:
        return None
    from portlight.engine.models import PortFeature
    if PortFeature.SHIPYARD not in port.features:
        return None
    captain = session.captain
    ship = captain.ship
    if not ship:
        return None
    if len(ship.upgrades) >= ship.upgrade_slots:
        return None

    # Only install upgrades when we have comfortable surplus
    if captain.silver < 300:
        return None

    from portlight.content.upgrades import UPGRADES
    installed_ids = {u.upgrade_id for u in ship.upgrades}
    budget = int(captain.silver * 0.2)

    # Score upgrades by category preference and ROI
    best = None
    best_score = 0
    for uid, tmpl in UPGRADES.items():
        if uid in installed_ids:
            continue
        if tmpl.price > budget:
            continue
        score = 1.0
        if prefer_categories and tmpl.category.value in prefer_categories:
            score *= 3.0
        # Speed and cargo upgrades are always valuable
        if tmpl.speed_bonus > 0:
            score *= 1.5
        if tmpl.cargo_bonus > 0:
            score *= 1.3
        # Cheaper = better ROI early
        score *= (1.0 / max(tmpl.price, 50)) * 100
        if score > best_score:
            best_score = score
            best = uid

    if best:
        return ActionPlan("install_upgrade", {"upgrade_id": best})
    return None


def _should_hire_specialist(session: "GameSession", prefer_roles: list[str] | None = None) -> ActionPlan | None:
    """Hire a specialist crew member if affordable (only with surplus silver)."""
    captain = session.captain
    ship = captain.ship
    if not ship or not session.current_port:
        return None

    # Only hire specialists when we have comfortable surplus (>800 silver)
    if captain.silver < 800:
        return None

    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolve_crew_max
    eff_crew_max = resolve_crew_max(ship, UPGRADES)
    if ship.crew >= eff_crew_max:
        return None

    from portlight.engine.models import CrewRole
    from portlight.content.crew_roles import ROLE_SPECS, get_role_count

    # Priority order (default): navigator > quartermaster > gunner > marine
    roles_to_try = prefer_roles or ["navigator", "quartermaster", "gunner", "marine"]

    for role_name in roles_to_try:
        try:
            role = CrewRole(role_name)
        except ValueError:
            continue
        spec = ROLE_SPECS[role]
        current = get_role_count(ship.roster, role)
        if spec.max_per_ship is not None and current >= spec.max_per_ship:
            continue
        hire_cost = spec.wage * 10  # hiring cost
        if hire_cost <= captain.silver * 0.05:  # very conservative: 5% of silver
            return ActionPlan("hire_role", {"role": role_name, "count": 1})

    return None


def _buy_for_active_contracts(session: "GameSession") -> ActionPlan | None:
    """Buy goods needed by any active contract if available at current port."""
    port = session.current_port
    if not port:
        return None
    captain = session.captain
    ship = captain.ship
    if not ship:
        return None
    cargo_used = sum(c.quantity for c in captain.cargo)
    space = ship.cargo_capacity - int(cargo_used)
    if space <= 0:
        return None

    for contract in session.board.active:
        remaining = contract.required_quantity - contract.delivered_quantity
        if remaining <= 0:
            continue
        held = sum(c.quantity for c in captain.cargo if c.good_id == contract.good_id)
        need = remaining - held
        if need <= 0:
            continue
        slot = next((sl for sl in port.market if sl.good_id == contract.good_id), None)
        if slot and slot.buy_price > 0 and slot.stock_current > 0:
            budget = int(captain.silver * 0.5)
            qty = min(need, slot.stock_current, space, budget // slot.buy_price if slot.buy_price > 0 else 0)
            if qty > 0:
                return ActionPlan("buy", {"good": contract.good_id, "qty": qty})
    return None


def _try_accept_contract(session: "GameSession", families: list[str] | None = None) -> ActionPlan | None:
    """Accept a contract if one looks good."""
    board = session.board
    if len(board.active) >= 3 or not board.offers:
        return None

    for offer in board.offers:
        if families and offer.family.value not in families:
            continue
        return ActionPlan("accept_contract", {"offer_id": offer.id})
    return None


# ---------------------------------------------------------------------------
# Policy implementations
# ---------------------------------------------------------------------------

def _lawful_conservative(s: "GameSession") -> list[ActionPlan]:
    """Low risk, trust-building, lawful growth."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    # Maintenance first
    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    # Sell profitable cargo
    sell = _best_sell(s, min_margin=0.05)
    if sell:
        actions.append(sell)

    # Accept lawful contracts
    contract = _try_accept_contract(s, ["procurement", "shortage", "return_freight"])
    if contract:
        actions.append(contract)

    # Buy for active contracts first
    contract_buy = _buy_for_active_contracts(s)
    if contract_buy:
        actions.append(contract_buy)

    # Buy if we have space
    buy = _best_buy(s, max_spend_pct=0.5)
    if buy:
        actions.append(buy)

    # Ship upgrade
    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    # Install ship component upgrades (conservative: cargo + navigation)
    comp = _should_install_upgrade(s, ["cargo", "navigation"])
    if comp:
        actions.append(comp)

    # Hire specialist (navigator first for speed)
    spec = _should_hire_specialist(s, ["navigator", "quartermaster"])
    if spec:
        actions.append(spec)

    # Sail
    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _opportunistic_trader(s: "GameSession") -> list[ActionPlan]:
    """Chase strongest visible margin. Moderate risk tolerance."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    sell = _best_sell(s, min_margin=-0.05)  # sell even at small loss to free space
    if sell:
        actions.append(sell)

    contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    # Buy for active contracts first
    contract_buy = _buy_for_active_contracts(s)
    if contract_buy:
        actions.append(contract_buy)

    buy = _best_buy(s, max_spend_pct=0.7)
    if buy:
        actions.append(buy)

    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    # Upgrades: speed + cargo for opportunistic trading
    comp = _should_install_upgrade(s, ["sails", "cargo"])
    if comp:
        actions.append(comp)

    # Hire specialist
    spec = _should_hire_specialist(s, ["navigator", "quartermaster", "gunner"])
    if spec:
        actions.append(spec)

    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _contract_forward(s: "GameSession") -> list[ActionPlan]:
    """Prioritize contracts. Trade supports obligations."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    sell = _best_sell(s, min_margin=0.0)
    if sell:
        actions.append(sell)

    # Accept contracts aggressively
    contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    # Buy goods that match active contracts
    _buy_for_contracts(s, actions)

    buy = _best_buy(s, max_spend_pct=0.4)
    if buy:
        actions.append(buy)

    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    comp = _should_install_upgrade(s, ["cargo", "sails"])
    if comp:
        actions.append(comp)

    spec = _should_hire_specialist(s, ["navigator", "quartermaster"])
    if spec:
        actions.append(spec)

    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _buy_for_contracts(s: "GameSession", actions: list[ActionPlan]) -> None:
    """Add buy actions for goods needed by active contracts."""
    port = s.current_port
    if not port:
        return
    for contract in s.board.active:
        remaining = contract.required_quantity - contract.delivered_quantity
        if remaining <= 0:
            continue
        held = sum(c.quantity for c in s.captain.cargo if c.good_id == contract.good_id)
        need = remaining - held
        if need <= 0:
            continue
        slot = next((sl for sl in port.market if sl.good_id == contract.good_id), None)
        if slot and slot.buy_price > 0 and slot.stock_current > 0:
            qty = min(need, slot.stock_current, s.captain.silver // slot.buy_price)
            if qty > 0:
                actions.append(ActionPlan("buy", {"good": contract.good_id, "qty": qty}))


def _infrastructure_forward(s: "GameSession") -> list[ActionPlan]:
    """Early warehouse/broker investment. Sacrifice liquidity for setup."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    sell = _best_sell(s, min_margin=0.0)
    if sell:
        actions.append(sell)

    # Try infrastructure purchases
    _try_infrastructure(s, actions)

    contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    buy = _best_buy(s, max_spend_pct=0.5)
    if buy:
        actions.append(buy)

    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    comp = _should_install_upgrade(s, ["cargo", "crew_quarters"])
    if comp:
        actions.append(comp)

    spec = _should_hire_specialist(s, ["quartermaster", "navigator"])
    if spec:
        actions.append(spec)

    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _try_infrastructure(s: "GameSession", actions: list[ActionPlan]) -> None:
    """Add infrastructure purchase actions if affordable."""
    port = s.current_port
    if not port:
        return

    # Warehouse
    active_wh = [w for w in s.infra.warehouses if w.active and w.port_id == port.id]
    if not active_wh and s.captain.silver >= 100:
        actions.append(ActionPlan("lease_warehouse", {"tier": "depot"}))

    # Broker
    from portlight.engine.infrastructure import get_broker_tier, BrokerTier
    current = get_broker_tier(s.infra, port.region)
    if current == BrokerTier.NONE and s.captain.silver >= 200:
        actions.append(ActionPlan("open_broker", {"region": port.region}))


def _leverage_forward(s: "GameSession") -> list[ActionPlan]:
    """Open credit early, take larger positions."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    sell = _best_sell(s, min_margin=0.0)
    if sell:
        actions.append(sell)

    # Try credit operations
    _try_credit(s, actions)

    contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    buy = _best_buy(s, max_spend_pct=0.8)  # more aggressive spending
    if buy:
        actions.append(buy)

    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    comp = _should_install_upgrade(s, ["sails", "cargo"])
    if comp:
        actions.append(comp)

    spec = _should_hire_specialist(s)
    if spec:
        actions.append(spec)

    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _try_credit(s: "GameSession", actions: list[ActionPlan]) -> None:
    """Try to open credit and draw if useful."""
    if not s.infra.credit or not s.infra.credit.active:
        actions.append(ActionPlan("open_credit", {}))
        return

    cred = s.infra.credit
    if cred.outstanding > 0 and s.captain.silver > cred.outstanding * 2:
        actions.append(ActionPlan("repay_credit", {"amount": cred.outstanding}))
    elif cred.outstanding == 0 and s.captain.silver < 200:
        available = cred.credit_limit - cred.outstanding
        if available > 50:
            actions.append(ActionPlan("draw_credit", {"amount": min(available, 200)}))


def _shadow_runner(s: "GameSession") -> list[ActionPlan]:
    """High-margin luxury focus, heat-tolerant."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    sell = _best_sell(s, min_margin=-0.1)  # sell aggressively
    if sell:
        actions.append(sell)

    # Prefer luxury/discreet contracts
    contract = _try_accept_contract(s, ["luxury_discreet", "shortage"])
    if not contract:
        contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    # Buy for active contracts
    contract_buy = _buy_for_active_contracts(s)
    if contract_buy:
        actions.append(contract_buy)

    # Buy luxury goods preferentially
    buy = _buy_luxury(s) or _best_buy(s, max_spend_pct=0.7)
    if buy:
        actions.append(buy)

    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    # Shadow runner: hidden compartments + speed
    comp = _should_install_upgrade(s, ["cargo", "sails", "navigation"])
    if comp:
        actions.append(comp)

    # Gunners for combat, quartermaster for sell bonus
    spec = _should_hire_specialist(s, ["gunner", "quartermaster", "navigator"])
    if spec:
        actions.append(spec)

    dest = _best_route(s)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions


def _buy_luxury(s: "GameSession") -> ActionPlan | None:
    """Prefer buying silk, spice, porcelain."""
    port = s.current_port
    if not port:
        return None
    captain = s.captain
    ship = captain.ship
    if not ship:
        return None

    from portlight.content.upgrades import UPGRADES as _UPG
    from portlight.engine.ship_stats import resolve_cargo_capacity
    cargo_used = sum(c.quantity for c in captain.cargo)
    eff_cap = resolve_cargo_capacity(ship, _UPG)
    space = eff_cap - int(cargo_used)
    budget = int(captain.silver * 0.6)

    luxury_ids = {"silk", "spice", "porcelain", "tea", "pearls"}
    for slot in port.market:
        if slot.good_id not in luxury_ids:
            continue
        if slot.buy_price <= 0 or slot.stock_current <= 0:
            continue
        qty = min(budget // slot.buy_price, slot.stock_current, space)
        if qty > 0:
            return ActionPlan("buy", {"good": slot.good_id, "qty": qty})
    return None


def _long_haul_optimizer(s: "GameSession") -> list[ActionPlan]:
    """Prioritize distance economics and East Indies access."""
    actions = []

    if s.at_sea:
        return [ActionPlan("advance")]

    for fn in [_should_repair, _should_hire, _should_provision]:
        a = fn(s)
        if a:
            actions.append(a)

    # Provision heavily for long hauls
    if s.captain.provisions < 20 and s.current_port:
        days = 25 - s.captain.provisions
        cost = days * s.current_port.provision_cost
        if cost <= s.captain.silver * 0.2:
            actions.append(ActionPlan("provision", {"days": days}))

    sell = _best_sell(s, min_margin=0.0)
    if sell:
        actions.append(sell)

    contract = _try_accept_contract(s)
    if contract:
        actions.append(contract)

    buy = _best_buy(s, max_spend_pct=0.6)
    if buy:
        actions.append(buy)

    # Prioritize ship upgrades for longer routes
    upgrade = _should_upgrade_ship(s)
    if upgrade:
        actions.append(upgrade)

    # Sell docked fleet ships to reduce wage burn (bots don't use fleet)
    sell_fleet = _should_sell_fleet_ship(s)
    if sell_fleet:
        actions.append(sell_fleet)

    # Long haul: storm resistance + speed + hull durability
    comp = _should_install_upgrade(s, ["sails", "hull_plating", "navigation"])
    if comp:
        actions.append(comp)

    # Navigator essential for long haul, surgeon for survival
    spec = _should_hire_specialist(s, ["navigator", "surgeon", "quartermaster"])
    if spec:
        actions.append(spec)

    # Prefer long routes
    dest = _best_route(s, prefer_long=True)
    if dest:
        actions.append(ActionPlan("sail", {"destination": dest}))
    elif not actions:
        actions.append(ActionPlan("advance"))

    return actions
