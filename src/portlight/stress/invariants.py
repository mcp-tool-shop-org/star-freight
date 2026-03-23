"""Cross-system invariants — laws that must hold under any game state.

These are not tests of specific behavior. They are laws about what
must never happen regardless of how the game got to a state.

Call check_all_invariants() after any mutation to verify truth.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.stress.types import InvariantResult, Subsystem

if TYPE_CHECKING:
    from portlight.app.session import GameSession


def check_all_invariants(session: "GameSession") -> list[InvariantResult]:
    """Run all invariants against current session state. Returns failures only."""
    results = []
    for checker in _ALL_CHECKS:
        result = checker(session)
        if not result.passed:
            results.append(result)
    return results


# ---------------------------------------------------------------------------
# Economic truth
# ---------------------------------------------------------------------------

def _check_no_negative_silver(s: "GameSession") -> InvariantResult:
    silver = s.captain.silver
    return InvariantResult(
        name="no_negative_silver",
        subsystem=Subsystem.ECONOMY,
        passed=silver >= 0,
        message=f"Silver is {silver}" if silver < 0 else "",
    )


def _check_no_negative_cargo(s: "GameSession") -> InvariantResult:
    for item in s.captain.cargo:
        if item.quantity < 0:
            return InvariantResult(
                name="no_negative_cargo",
                subsystem=Subsystem.ECONOMY,
                passed=False,
                message=f"{item.good_id} has quantity {item.quantity}",
            )
    return InvariantResult(
        name="no_negative_cargo",
        subsystem=Subsystem.ECONOMY,
        passed=True,
    )


def _check_cargo_within_capacity(s: "GameSession") -> InvariantResult:
    ship = s.captain.ship
    if not ship:
        return InvariantResult(
            name="cargo_within_capacity",
            subsystem=Subsystem.ECONOMY,
            passed=True,
        )
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolve_cargo_capacity
    used = sum(c.quantity for c in s.captain.cargo)
    cap = resolve_cargo_capacity(ship, UPGRADES)
    return InvariantResult(
        name="cargo_within_capacity",
        subsystem=Subsystem.ECONOMY,
        passed=used <= cap,
        message=f"Cargo {used} exceeds capacity {cap}" if used > cap else "",
    )


def _check_market_stock_valid(s: "GameSession") -> InvariantResult:
    for port in s.world.ports.values():
        for slot in port.market:
            if slot.stock_current < 0:
                return InvariantResult(
                    name="market_stock_valid",
                    subsystem=Subsystem.ECONOMY,
                    passed=False,
                    message=f"{port.id}/{slot.good_id} stock={slot.stock_current}",
                )
    return InvariantResult(
        name="market_stock_valid",
        subsystem=Subsystem.ECONOMY,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Contract truth
# ---------------------------------------------------------------------------

def _check_no_dual_contract_resolution(s: "GameSession") -> InvariantResult:
    """No contract should appear in both active and completed."""
    active_ids = {c.offer_id for c in s.board.active}
    completed_ids = {o.contract_id for o in s.board.completed}
    overlap = active_ids & completed_ids
    return InvariantResult(
        name="no_dual_contract_resolution",
        subsystem=Subsystem.CONTRACTS,
        passed=len(overlap) == 0,
        message=f"Overlapping: {overlap}" if overlap else "",
    )


def _check_delivered_within_required(s: "GameSession") -> InvariantResult:
    """Delivered quantity never exceeds required quantity."""
    for c in s.board.active:
        if c.delivered_quantity > c.required_quantity:
            return InvariantResult(
                name="delivered_within_required",
                subsystem=Subsystem.CONTRACTS,
                passed=False,
                message=f"{c.offer_id}: delivered {c.delivered_quantity} > required {c.required_quantity}",
            )
    return InvariantResult(
        name="delivered_within_required",
        subsystem=Subsystem.CONTRACTS,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Infrastructure truth
# ---------------------------------------------------------------------------

def _check_inactive_warehouse_empty(s: "GameSession") -> InvariantResult:
    """Closed warehouses should have no inventory."""
    for w in s.infra.warehouses:
        if not w.active and w.inventory:
            return InvariantResult(
                name="inactive_warehouse_empty",
                subsystem=Subsystem.INFRASTRUCTURE,
                passed=False,
                message=f"Warehouse {w.id} inactive but has {len(w.inventory)} lots",
            )
    return InvariantResult(
        name="inactive_warehouse_empty",
        subsystem=Subsystem.INFRASTRUCTURE,
        passed=True,
    )


def _check_warehouse_within_capacity(s: "GameSession") -> InvariantResult:
    """Active warehouse inventory should not exceed capacity."""
    for w in s.infra.warehouses:
        if not w.active:
            continue
        used = sum(lot.quantity for lot in w.inventory)
        if used > w.capacity:
            return InvariantResult(
                name="warehouse_within_capacity",
                subsystem=Subsystem.INFRASTRUCTURE,
                passed=False,
                message=f"Warehouse {w.id}: used {used} > capacity {w.capacity}",
            )
    return InvariantResult(
        name="warehouse_within_capacity",
        subsystem=Subsystem.INFRASTRUCTURE,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Insurance truth
# ---------------------------------------------------------------------------

def _check_no_overclaimed_policy(s: "GameSession") -> InvariantResult:
    """Total paid claims should not exceed policy coverage cap."""
    from portlight.content.infrastructure import POLICY_CATALOG
    for claim in s.infra.claims:
        spec = POLICY_CATALOG.get(claim.policy_id)
        if spec and claim.payout > spec.coverage_cap:
            return InvariantResult(
                name="no_overclaimed_policy",
                subsystem=Subsystem.INSURANCE,
                passed=False,
                message=f"Claim {claim.policy_id}: paid {claim.payout} > cap {spec.coverage_cap}",
            )
    return InvariantResult(
        name="no_overclaimed_policy",
        subsystem=Subsystem.INSURANCE,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Credit truth
# ---------------------------------------------------------------------------

def _check_no_overdraw(s: "GameSession") -> InvariantResult:
    """Outstanding credit should not exceed credit limit."""
    cred = s.infra.credit
    if not cred or not cred.active:
        return InvariantResult(
            name="no_credit_overdraw",
            subsystem=Subsystem.CREDIT,
            passed=True,
        )
    if cred.outstanding > cred.credit_limit:
        return InvariantResult(
            name="no_credit_overdraw",
            subsystem=Subsystem.CREDIT,
            passed=False,
            message=f"Outstanding {cred.outstanding} > limit {cred.credit_limit}",
        )
    return InvariantResult(
        name="no_credit_overdraw",
        subsystem=Subsystem.CREDIT,
        passed=True,
    )


def _check_frozen_credit_no_draw(s: "GameSession") -> InvariantResult:
    """Frozen credit line should have zero draws since freeze."""
    cred = s.infra.credit
    if not cred:
        return InvariantResult(
            name="frozen_credit_no_draw",
            subsystem=Subsystem.CREDIT,
            passed=True,
        )
    # Credit is frozen when defaults >= 3
    if cred.defaults >= 3 and cred.active:
        return InvariantResult(
            name="frozen_credit_no_draw",
            subsystem=Subsystem.CREDIT,
            passed=False,
            message=f"Credit active despite {cred.defaults} defaults",
        )
    return InvariantResult(
        name="frozen_credit_no_draw",
        subsystem=Subsystem.CREDIT,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Campaign truth
# ---------------------------------------------------------------------------

def _check_completed_milestones_persistent(s: "GameSession") -> InvariantResult:
    """Completed milestones should never have duplicates."""
    ids = [m.milestone_id for m in s.campaign.completed]
    if len(ids) != len(set(ids)):
        dupes = [mid for mid in ids if ids.count(mid) > 1]
        return InvariantResult(
            name="completed_milestones_no_dupes",
            subsystem=Subsystem.CAMPAIGN,
            passed=False,
            message=f"Duplicate milestones: {set(dupes)}",
        )
    return InvariantResult(
        name="completed_milestones_no_dupes",
        subsystem=Subsystem.CAMPAIGN,
        passed=True,
    )


def _check_completed_paths_persistent(s: "GameSession") -> InvariantResult:
    """Completed victory paths should never have duplicates."""
    ids = [p.path_id for p in s.campaign.completed_paths]
    if len(ids) != len(set(ids)):
        return InvariantResult(
            name="completed_paths_no_dupes",
            subsystem=Subsystem.CAMPAIGN,
            passed=False,
            message=f"Duplicate paths: {ids}",
        )
    return InvariantResult(
        name="completed_paths_no_dupes",
        subsystem=Subsystem.CAMPAIGN,
        passed=True,
    )


def _check_first_path_stays_first(s: "GameSession") -> InvariantResult:
    """If any path is marked is_first, exactly one should be."""
    firsts = [p for p in s.campaign.completed_paths if p.is_first]
    if len(firsts) > 1:
        return InvariantResult(
            name="first_path_stays_first",
            subsystem=Subsystem.CAMPAIGN,
            passed=False,
            message=f"{len(firsts)} paths marked as first",
        )
    return InvariantResult(
        name="first_path_stays_first",
        subsystem=Subsystem.CAMPAIGN,
        passed=True,
    )


# ---------------------------------------------------------------------------
# Ship expansion truth
# ---------------------------------------------------------------------------

def _check_crew_matches_roster(s: "GameSession") -> InvariantResult:
    """ship.crew must equal roster.total for every ship."""
    ship = s.captain.ship
    if ship and hasattr(ship, "roster") and ship.roster.total > 0:
        if ship.crew != ship.roster.total:
            return InvariantResult(
                name="crew_matches_roster",
                subsystem=Subsystem.ECONOMY,
                passed=False,
                message=f"Flagship crew={ship.crew} != roster.total={ship.roster.total}",
            )
    for owned in s.captain.fleet:
        r = getattr(owned.ship, "roster", None)
        if r and r.total > 0 and owned.ship.crew != r.total:
            return InvariantResult(
                name="crew_matches_roster",
                subsystem=Subsystem.ECONOMY,
                passed=False,
                message=f"Fleet ship {owned.ship.name} crew={owned.ship.crew} != roster.total={r.total}",
            )
    return InvariantResult(name="crew_matches_roster", subsystem=Subsystem.ECONOMY, passed=True)


def _check_fleet_within_trust_limit(s: "GameSession") -> InvariantResult:
    """Fleet size must not exceed trust-based limit."""
    from portlight.engine.models import max_fleet_size
    trust = s.captain.standing.commercial_trust
    limit = max_fleet_size(trust)
    total = 1 + len(s.captain.fleet)
    return InvariantResult(
        name="fleet_within_trust_limit",
        subsystem=Subsystem.ECONOMY,
        passed=total <= limit,
        message=f"Fleet {total} > limit {limit}" if total > limit else "",
    )


def _check_upgrades_within_slots(s: "GameSession") -> InvariantResult:
    """No ship has more upgrades than its slot count."""
    ship = s.captain.ship
    if ship and len(ship.upgrades) > ship.upgrade_slots:
        return InvariantResult(
            name="upgrades_within_slots",
            subsystem=Subsystem.ECONOMY,
            passed=False,
            message=f"Flagship has {len(ship.upgrades)} upgrades in {ship.upgrade_slots} slots",
        )
    for owned in s.captain.fleet:
        if len(owned.ship.upgrades) > owned.ship.upgrade_slots:
            return InvariantResult(
                name="upgrades_within_slots",
                subsystem=Subsystem.ECONOMY,
                passed=False,
                message=f"Fleet ship {owned.ship.name} exceeds upgrade slots",
            )
    return InvariantResult(name="upgrades_within_slots", subsystem=Subsystem.ECONOMY, passed=True)


def _check_no_negative_crew_roles(s: "GameSession") -> InvariantResult:
    """No role count in any roster is negative."""
    for ship in [s.captain.ship] + [o.ship for o in s.captain.fleet]:
        if ship and hasattr(ship, "roster"):
            r = ship.roster
            for field in ["sailors", "gunners", "navigators", "surgeons", "marines", "quartermasters"]:
                val = getattr(r, field, 0)
                if val < 0:
                    return InvariantResult(
                        name="no_negative_crew_roles",
                        subsystem=Subsystem.ECONOMY,
                        passed=False,
                        message=f"{ship.name} has {field}={val}",
                    )
    return InvariantResult(name="no_negative_crew_roles", subsystem=Subsystem.ECONOMY, passed=True)


def _check_flagship_exists(s: "GameSession") -> InvariantResult:
    """Captain must always have a flagship."""
    return InvariantResult(
        name="flagship_exists",
        subsystem=Subsystem.ECONOMY,
        passed=s.captain.ship is not None,
        message="No flagship" if s.captain.ship is None else "",
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_ALL_CHECKS = [
    # Economy
    _check_no_negative_silver,
    _check_no_negative_cargo,
    _check_cargo_within_capacity,
    _check_market_stock_valid,
    # Contracts
    _check_no_dual_contract_resolution,
    _check_delivered_within_required,
    # Infrastructure
    _check_inactive_warehouse_empty,
    _check_warehouse_within_capacity,
    # Insurance
    _check_no_overclaimed_policy,
    # Credit
    _check_no_overdraw,
    _check_frozen_credit_no_draw,
    # Campaign
    _check_completed_milestones_persistent,
    _check_completed_paths_persistent,
    _check_first_path_stays_first,
    # Ship expansion
    _check_crew_matches_roster,
    _check_fleet_within_trust_limit,
    _check_upgrades_within_slots,
    _check_no_negative_crew_roles,
    _check_flagship_exists,
]
