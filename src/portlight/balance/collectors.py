"""Metric collectors — extract balance metrics from game state.

Translates raw game events and state into comparable balance evidence.
Collectors never mutate game state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from portlight.balance.types import PhaseTiming, RouteRunMetrics, RunMetrics

if TYPE_CHECKING:
    from portlight.app.session import GameSession
    from portlight.balance.types import BalanceRunConfig


def collect_run_metrics(
    session: "GameSession",
    config: "BalanceRunConfig",
    route_tracker: dict[str, RouteRunMetrics],
    timing: PhaseTiming,
) -> RunMetrics:
    """Build final RunMetrics from completed session state."""
    captain = session.captain
    world = session.world
    ledger = session.ledger
    board = session.board
    infra = session.infra
    campaign = session.campaign

    from portlight.content.ships import SHIPS
    ship_class = "sloop"
    if captain.ship:
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl:
            ship_class = tmpl.ship_class.value

    # Net worth = silver + ship value + cargo value
    net_worth = captain.silver
    if captain.ship:
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl:
            net_worth += int(tmpl.price * 0.4)
    for item in captain.cargo:
        net_worth += item.cost_basis

    # Count inspections/seizures from reputation incidents
    inspections = 0
    seizures = 0
    for inc in captain.standing.recent_incidents:
        if inc.incident_type == "inspection":
            inspections += 1
        if "seized" in inc.description.lower() or "seizure" in inc.description.lower():
            seizures += 1

    # Avg heat by region
    avg_heat = {}
    for region, heat in captain.standing.customs_heat.items():
        avg_heat[region] = float(heat)

    # Contract stats
    contracts_completed = sum(
        1 for o in board.completed if o.outcome_type == "completed"
    )
    contracts_failed = sum(
        1 for o in board.completed
        if o.outcome_type in ("expired", "failed", "abandoned")
    )

    # Infrastructure counts
    warehouses_opened = sum(1 for w in infra.warehouses)
    brokers_opened = sum(
        1 for b in infra.brokers if b.tier.value != "none"
    )
    licenses_bought = len(infra.licenses)

    # Finance
    insurance_bought = len(infra.policies)
    claims_paid = sum(1 for c in infra.claims if c.paid_amount > 0)
    credit_draw = 0
    credit_repaid = 0
    defaults = 0
    if infra.credit:
        credit_draw = infra.credit.total_borrowed
        credit_repaid = infra.credit.total_repaid
        defaults = infra.credit.defaults

    # Victory
    from portlight.engine.campaign import (
        SessionSnapshot,
        compute_victory_progress,
    )
    snap = SessionSnapshot(
        captain=captain, world=world, board=board,
        infra=infra, ledger=ledger, campaign=campaign,
    )
    progress = compute_victory_progress(snap)
    strongest = progress[0].path_id if progress else ""
    completed_paths = [vc.path_id for vc in campaign.completed_paths]

    # Trade stats
    total_trades = len(ledger.receipts)
    total_profit = ledger.net_profit
    voyages = sum(
        1 for inc in captain.standing.recent_incidents
        if inc.incident_type == "arrival"
    )

    m = RunMetrics(
        config=config,
        days_played=world.day,
        final_silver=captain.silver,
        final_net_worth=net_worth,
        final_ship_class=ship_class,
        voyages_completed=voyages,
        total_trades=total_trades,
        total_trade_profit=total_profit,
        contracts_accepted=len(board.active) + contracts_completed + contracts_failed,
        contracts_completed=contracts_completed,
        contracts_failed=contracts_failed,
        inspections=inspections,
        seizures=seizures,
        defaults=defaults,
        avg_heat_by_region=avg_heat,
        warehouses_opened=warehouses_opened,
        brokers_opened=brokers_opened,
        licenses_bought=licenses_bought,
        insurance_policies_bought=insurance_bought,
        claims_paid=claims_paid,
        credit_draw_total=credit_draw,
        credit_repaid_total=credit_repaid,
        strongest_victory_path=strongest,
        completed_victory_paths=completed_paths,
        timing=timing,
        route_metrics=list(route_tracker.values()),
    )
    return m


def compute_net_worth(session: "GameSession") -> int:
    """Compute current net worth for day-band snapshots."""
    captain = session.captain
    net = captain.silver
    if captain.ship:
        from portlight.content.ships import SHIPS
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl:
            net += int(tmpl.price * 0.4)
    for item in captain.cargo:
        net += item.cost_basis
    return net


def update_route_tracker(
    tracker: dict[str, RouteRunMetrics],
    origin: str,
    destination: str,
    profit: int,
) -> None:
    """Record a completed voyage in the route tracker."""
    key = f"{origin}->{destination}"
    if key not in tracker:
        tracker[key] = RouteRunMetrics(route_key=key)
    rm = tracker[key]
    rm.times_used += 1
    rm.total_profit += profit
    if profit < 0:
        rm.loss_count += 1


def update_timing(
    timing: PhaseTiming,
    session: "GameSession",
    day: int,
) -> None:
    """Check if any phase-timing event just occurred."""
    infra = session.infra
    captain = session.captain

    if timing.first_warehouse == -1 and any(w.active for w in infra.warehouses):
        timing.first_warehouse = day

    if timing.first_broker == -1 and any(
        b.active and b.tier.value != "none" for b in infra.brokers
    ):
        timing.first_broker = day

    if timing.first_license == -1 and any(lic.active for lic in infra.licenses):
        timing.first_license = day

    if timing.first_credit_line == -1 and infra.credit and infra.credit.active:
        timing.first_credit_line = day

    if timing.first_insurance == -1 and infra.policies:
        timing.first_insurance = day

    if captain.ship:
        from portlight.content.ships import SHIPS
        tmpl = SHIPS.get(captain.ship.template_id)
        if tmpl:
            if timing.first_brigantine == -1 and tmpl.ship_class.value == "brigantine":
                timing.first_brigantine = day
            if timing.first_galleon == -1 and tmpl.ship_class.value == "galleon":
                timing.first_galleon = day

    # East Indies check — are we docked in East Indies?
    port = session.current_port
    if timing.first_east_indies == -1 and port and port.region == "East Indies":
        timing.first_east_indies = day
