"""Playtest simulation harness — Star Freight Phase 8.

Runs archetyped 90-day campaigns to prove that different captain
postures produce genuinely different lives.

This is not AI. These are deterministic strategy profiles that
make consistent decisions based on captain identity. The harness
measures what diverges and what doesn't.

Three captain postures:
- Relief / Legitimacy: convoy discipline, trust-based access, public consequence
- Gray / Document: paper leverage, timing abuse, institutional risk
- Honor / Frontier: direct confrontation, house politics, reputation volatility
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from portlight.engine.sf_campaign import (
    CampaignState,
    dock_at_station,
    travel_to,
    execute_trade,
    run_combat,
    get_campaign_summary,
)
from portlight.engine.crew import (
    recruit,
    active_crew,
    fit_crew,
    cultural_knowledge_level,
    Civilization,
    CrewStatus,
)
from portlight.engine.grid_combat import CombatPhase
from portlight.engine.investigation import ThreadState
from portlight.content.star_freight import (
    SLICE_STATIONS,
    SLICE_LANES,
    SLICE_GOODS,
    create_thal,
    create_varek,
    create_sera,
    create_nera,
    create_ilen,
)


# ---------------------------------------------------------------------------
# Run metrics (what we measure)
# ---------------------------------------------------------------------------

@dataclass
class RunMetrics:
    """Everything tracked across a 90-day run."""
    captain_type: str = ""
    days_simulated: int = 0
    credits_history: list[int] = field(default_factory=list)
    stations_visited: dict[str, int] = field(default_factory=dict)
    lanes_used: dict[str, int] = field(default_factory=dict)
    contracts_completed: dict[str, int] = field(default_factory=dict)
    goods_traded: dict[str, int] = field(default_factory=dict)
    encounters_by_type: dict[str, int] = field(default_factory=dict)
    encounter_outcomes: dict[str, int] = field(default_factory=dict)
    combat_count: int = 0
    retreats: int = 0
    crew_injuries: int = 0
    crew_departures: int = 0
    repairs_needed: int = 0
    reputation_history: list[dict[str, int]] = field(default_factory=list)
    investigation_fragments: dict[str, list[str]] = field(default_factory=dict)
    investigation_sources: dict[str, int] = field(default_factory=dict)
    delays: int = 0
    seizures: int = 0
    cultural_interactions: int = 0
    pay_missed: int = 0
    consequence_tags: list[str] = field(default_factory=list)

    # Derived at end
    final_credits: int = 0
    final_reputation: dict[str, int] = field(default_factory=dict)
    final_investigation_progress: int = 0
    dominant_stations: list[str] = field(default_factory=list)
    dominant_lanes: list[str] = field(default_factory=list)
    captain_identity: str = ""


# ---------------------------------------------------------------------------
# Captain strategy profiles
# ---------------------------------------------------------------------------

class CaptainPosture(str, Enum):
    RELIEF = "relief"
    GRAY = "gray"
    HONOR = "honor"


@dataclass
class StrategyProfile:
    """Deterministic decision rules for a captain posture."""
    posture: CaptainPosture
    preferred_stations: list[str]
    avoided_stations: list[str]
    preferred_goods: list[str]
    preferred_contracts: list[str]
    combat_strategy: str              # aggressive | defensive | retreat
    risk_tolerance: float             # 0.0-1.0
    contraband_willingness: bool
    description: str


RELIEF_PROFILE = StrategyProfile(
    posture=CaptainPosture.RELIEF,
    preferred_stations=["communion_relay", "mourning_quay", "queue_of_flags"],
    avoided_stations=["ironjaw_den"],
    preferred_goods=["medical_supplies", "ration_grain", "coolant_ampoules", "keth_organics"],
    preferred_contracts=["standard_delivery", "cold_lantern_freight", "priority_relief"],
    combat_strategy="defensive",
    risk_tolerance=0.3,
    contraband_willingness=False,
    description="Legitimacy-leaning. Convoy discipline. Trust-based access. Public consequence.",
)

GRAY_PROFILE = StrategyProfile(
    posture=CaptainPosture.GRAY,
    preferred_stations=["registry_spindle", "grand_drift", "meridian_exchange", "communion_relay"],
    avoided_stations=["drashan_citadel"],
    preferred_goods=["bond_plate", "orryn_data", "compact_alloys", "reserve_grain", "orryn_brokered_goods"],
    preferred_contracts=["claim_courier", "bonded_relief_run", "witness_run", "embargo_slip"],
    combat_strategy="retreat",
    risk_tolerance=0.6,
    contraband_willingness=True,
    description="Paper leverage. Timing abuse. Institutional risk. Faster plot entanglement.",
)

HONOR_PROFILE = StrategyProfile(
    posture=CaptainPosture.HONOR,
    preferred_stations=["drashan_citadel", "ironjaw_den", "communion_relay"],
    avoided_stations=["queue_of_flags"],
    preferred_goods=["veshan_weapons", "veshan_minerals", "black_seal_resin", "compact_alloys"],
    preferred_contracts=["bounty_contract", "cultural_cargo", "witness_run"],
    combat_strategy="aggressive",
    risk_tolerance=0.8,
    contraband_willingness=False,
    description="Direct confrontation. House politics. Reputation volatility. Tactical exposure.",
)


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

def create_campaign_for_posture(posture: CaptainPosture) -> CampaignState:
    """Create a campaign with crew matching the posture."""
    state = CampaignState()

    if posture == CaptainPosture.RELIEF:
        recruit(state.crew, create_thal())
        recruit(state.crew, create_ilen())
    elif posture == CaptainPosture.GRAY:
        recruit(state.crew, create_sera())
        recruit(state.crew, create_nera())
    elif posture == CaptainPosture.HONOR:
        recruit(state.crew, create_varek())
        recruit(state.crew, create_thal())

    return state


def pick_destination(state: CampaignState, profile: StrategyProfile) -> str | None:
    """Choose next destination based on strategy."""
    current = state.current_station
    candidates = []

    for lane in SLICE_LANES.values():
        dest = None
        if lane.station_a == current:
            dest = lane.station_b
        elif lane.station_b == current:
            dest = lane.station_a
        if dest is None:
            continue

        # Check fuel
        if state.ship_fuel < lane.distance_days:
            continue

        # Score destination
        score = 0.0
        if dest in profile.preferred_stations:
            score += 3.0
        if dest in profile.avoided_stations:
            score -= 5.0

        # Cargo-aware routing: if carrying goods, prefer stations that demand them
        dest_station = SLICE_STATIONS.get(dest)
        cargo_urgency = len(state.ship_cargo) / max(1, state.ship_cargo_capacity)  # 0-1
        if dest_station and state.ship_cargo:
            for good_id in set(state.ship_cargo):
                count = state.ship_cargo.count(good_id)
                if good_id in dest_station.demands:
                    score += 5.0 * count * (0.5 + cargo_urgency)  # very strong pull
                elif good_id not in dest_station.produces:
                    score += 2.0 * count * (0.5 + cargo_urgency)  # decent pull

        # If cargo hold is empty or light, prefer source stations for restocking
        if len(state.ship_cargo) < state.ship_cargo_capacity // 2 and dest_station:
            for good_id in profile.preferred_goods:
                if good_id in dest_station.produces:
                    score += 2.0

        # Risk tolerance affects dangerous lane preference
        if lane.danger > 0.15:
            score += (profile.risk_tolerance - 0.5) * 2
        else:
            score += (0.5 - profile.risk_tolerance)

        # Contraband lanes
        if lane.contraband_risk > 0.2 and not profile.contraband_willingness:
            score -= 1.0

        # Don't revisit immediately
        if dest == current:
            continue

        candidates.append((dest, score, lane.id))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[1])
    return candidates[0][0]


def pick_trade_action(state: CampaignState, profile: StrategyProfile) -> list[dict]:
    """Decide what to buy/sell at current station.

    Strategy: sell cargo where it's demanded (best price) or where it wasn't
    produced (decent price). Buy preferred goods at source stations.
    A competent captain sells before buying.
    """
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return []

    actions = []

    # Sell first — always sell before buying
    for good_id in set(state.ship_cargo):
        count = state.ship_cargo.count(good_id)
        if count <= 0:
            continue

        # Best case: station demands this good (premium price)
        if good_id in station.demands:
            actions.append({"action": "sell", "good": good_id, "qty": count})
        # Good case: station doesn't produce this (base price, still profit if bought at source)
        elif good_id not in station.produces:
            actions.append({"action": "sell", "good": good_id, "qty": count})
        # Else: we're at the source — hold for a better destination

    # Buy preferred goods that are produced here (source discount)
    for good_id in profile.preferred_goods:
        if good_id in station.produces and good_id in SLICE_GOODS:
            good = SLICE_GOODS[good_id]
            if state.credits >= good.base_price and len(state.ship_cargo) < state.ship_cargo_capacity:
                qty = min(3, state.ship_cargo_capacity - len(state.ship_cargo))
                if qty > 0:
                    actions.append({"action": "buy", "good": good_id, "qty": qty})

    return actions


def simulate_run(
    posture: CaptainPosture,
    days: int = 90,
    seed: int = 42,
) -> tuple[CampaignState, RunMetrics]:
    """Run a complete simulation for one captain posture.

    Returns (final_state, metrics).
    """
    profile = {
        CaptainPosture.RELIEF: RELIEF_PROFILE,
        CaptainPosture.GRAY: GRAY_PROFILE,
        CaptainPosture.HONOR: HONOR_PROFILE,
    }[posture]

    state = create_campaign_for_posture(posture)
    state.seed = seed
    metrics = RunMetrics(captain_type=posture.value)

    # Start at Meridian Exchange
    dock_at_station(state, "meridian_exchange")
    metrics.stations_visited["meridian_exchange"] = 1

    turn = 0
    max_turns = days * 2  # safety limit (some turns are travel, some are station)
    recent_combat_days: list[int] = []  # tracks days of recent fights for escalation

    while state.day <= days and turn < max_turns:
        turn += 1

        # Record credit snapshot
        if state.day % 10 == 0 or turn == 1:
            metrics.credits_history.append(state.credits)
            metrics.reputation_history.append(dict(state.reputation))

        # At station: trade, then pick destination
        if state.current_station and not state.in_transit:
            # Trade
            trade_actions = pick_trade_action(state, profile)
            for ta in trade_actions:
                result = execute_trade(state, ta["good"], ta["action"], ta["qty"])
                if "error" not in result:
                    key = f"{ta['action']}_{ta['good']}"
                    metrics.goods_traded[key] = metrics.goods_traded.get(key, 0) + ta["qty"]
                    if result.get("investigation"):
                        src = result["investigation"].get("source", "unknown")
                        metrics.investigation_sources[src] = metrics.investigation_sources.get(src, 0) + 1

            # Pick destination and travel
            dest = pick_destination(state, profile)
            if dest is None:
                # Stuck — refuel if possible, otherwise wait
                state.ship_fuel = min(8, state.ship_fuel + 2)  # emergency refuel
                state.credits -= 30  # cost
                state.day += 1
                metrics.delays += 1
                continue

            travel_result = travel_to(state, dest)
            if "error" in travel_result:
                state.day += 1
                metrics.delays += 1
                continue

            # Track lane usage
            for lane in SLICE_LANES.values():
                if (lane.station_a == state.current_station and lane.station_b == dest) or \
                   (lane.station_b == state.current_station and lane.station_a == dest):
                    metrics.lanes_used[lane.id] = metrics.lanes_used.get(lane.id, 0) + 1
                    break

            # Process events
            for event in travel_result.get("events", []):
                etype = event.get("type", "")
                if etype == "pay" and not event.get("paid", True):
                    metrics.pay_missed += 1
                elif etype == "crew_departure":
                    metrics.crew_departures += 1
                elif etype == "loyalty_unlock":
                    pass  # tracked implicitly

            # Handle encounter if one occurred
            if travel_result.get("encounter"):
                enc = travel_result["encounter"]
                arch = enc.get("archetype", "unknown")
                metrics.encounters_by_type[arch] = metrics.encounters_by_type.get(arch, 0) + 1
                metrics.combat_count += 1

                # Escalation: count fights in the last 10 days
                recent_combat_days = [d for d in recent_combat_days if state.day - d <= 10]
                clustered = len(recent_combat_days)
                escalation = min(0.6, clustered * 0.15)
                recent_combat_days.append(state.day)

                result = run_combat(state, enc, strategy=profile.combat_strategy,
                                    escalation_factor=escalation)
                outcome = result.outcome.value
                metrics.encounter_outcomes[outcome] = metrics.encounter_outcomes.get(outcome, 0) + 1

                if result.outcome == CombatPhase.RETREAT:
                    metrics.retreats += 1
                if result.crew_injuries:
                    metrics.crew_injuries += len(result.crew_injuries)
                if result.hull_damage_taken > state.ship_hull_max * 0.3:
                    metrics.repairs_needed += 1

                metrics.consequence_tags.extend(result.consequence_tags)

                # If we didn't arrive, dock at nearest available
                if state.current_station != dest:
                    # Try to continue to destination
                    state.current_station = dest  # simplified: assume we limp there
            else:
                # Arrived — dock
                dock_result = dock_at_station(state, dest)
                for event in dock_result.get("events", []):
                    if event.get("type") == "investigation":
                        src = "station"
                        metrics.investigation_sources[src] = metrics.investigation_sources.get(src, 0) + 1

            # Track station visit
            if state.current_station:
                metrics.stations_visited[state.current_station] = \
                    metrics.stations_visited.get(state.current_station, 0) + 1

        else:
            # Shouldn't happen, but safety
            state.day += 1

    # --- Finalize metrics ---
    metrics.days_simulated = state.day
    metrics.final_credits = state.credits
    metrics.final_reputation = dict(state.reputation)
    metrics.final_investigation_progress = state.investigation.total_progress
    metrics.credits_history.append(state.credits)
    metrics.reputation_history.append(dict(state.reputation))

    # Dominant stations (top 3 by visit count)
    sorted_stations = sorted(metrics.stations_visited.items(), key=lambda x: -x[1])
    metrics.dominant_stations = [s[0] for s in sorted_stations[:3]]

    # Dominant lanes (top 3)
    sorted_lanes = sorted(metrics.lanes_used.items(), key=lambda x: -x[1])
    metrics.dominant_lanes = [l[0] for l in sorted_lanes[:3]]

    # Captain identity summary
    metrics.captain_identity = _derive_identity(metrics, profile)

    return state, metrics


def _derive_identity(metrics: RunMetrics, profile: StrategyProfile) -> str:
    """Derive a one-line captain identity from the run data."""
    # What kind of captain did this become?
    if metrics.retreats > metrics.combat_count * 0.5:
        combat_style = "evasive"
    elif metrics.combat_count > 5:
        combat_style = "battle-tested"
    else:
        combat_style = "cautious"

    if metrics.pay_missed > 2:
        financial = "struggling"
    elif metrics.final_credits > 1000:
        financial = "prosperous"
    else:
        financial = "stable"

    return f"{profile.description} [{combat_style}, {financial}]"


# ---------------------------------------------------------------------------
# Divergence analysis
# ---------------------------------------------------------------------------

def analyze_divergence(
    metrics_a: RunMetrics,
    metrics_b: RunMetrics,
    metrics_c: RunMetrics,
) -> dict:
    """Compare three runs and measure divergence.

    Returns a dict of divergence measurements.
    Higher numbers = more divergence = more replayability.
    """
    results = {}

    # 1. Route divergence: how different are dominant stations?
    sets = [set(m.dominant_stations) for m in [metrics_a, metrics_b, metrics_c]]
    all_stations = sets[0] | sets[1] | sets[2]
    shared_stations = sets[0] & sets[1] & sets[2]
    results["route_divergence"] = 1.0 - (len(shared_stations) / max(1, len(all_stations)))

    # 2. Lane divergence
    lane_sets = [set(m.dominant_lanes) for m in [metrics_a, metrics_b, metrics_c]]
    all_lanes = lane_sets[0] | lane_sets[1] | lane_sets[2]
    shared_lanes = lane_sets[0] & lane_sets[1] & lane_sets[2]
    results["lane_divergence"] = 1.0 - (len(shared_lanes) / max(1, len(all_lanes)))

    # 3. Economic divergence: credit spread
    credits = [m.final_credits for m in [metrics_a, metrics_b, metrics_c]]
    credit_range = max(credits) - min(credits)
    credit_avg = sum(credits) / 3
    results["economic_divergence"] = credit_range / max(1, credit_avg)

    # 4. Combat profile divergence
    combat_counts = [m.combat_count for m in [metrics_a, metrics_b, metrics_c]]
    retreat_rates = [m.retreats / max(1, m.combat_count) for m in [metrics_a, metrics_b, metrics_c]]
    results["combat_divergence"] = max(retreat_rates) - min(retreat_rates)

    # 5. Reputation divergence: how different are faction standings?
    rep_divergence = 0.0
    all_factions = set()
    for m in [metrics_a, metrics_b, metrics_c]:
        all_factions |= set(m.final_reputation.keys())
    for faction in all_factions:
        values = [m.final_reputation.get(faction, 0) for m in [metrics_a, metrics_b, metrics_c]]
        rep_divergence += max(values) - min(values)
    results["reputation_divergence"] = rep_divergence / max(1, len(all_factions))

    # 6. Failure texture divergence
    injury_rates = [m.crew_injuries for m in [metrics_a, metrics_b, metrics_c]]
    delay_rates = [m.delays for m in [metrics_a, metrics_b, metrics_c]]
    pay_rates = [m.pay_missed for m in [metrics_a, metrics_b, metrics_c]]
    results["failure_divergence"] = (
        (max(injury_rates) - min(injury_rates)) +
        (max(delay_rates) - min(delay_rates)) +
        (max(pay_rates) - min(pay_rates))
    ) / 3.0

    # 7. Goods traded divergence
    all_goods = set()
    for m in [metrics_a, metrics_b, metrics_c]:
        all_goods |= set(m.goods_traded.keys())
    goods_overlap = 0
    for g in all_goods:
        present = sum(1 for m in [metrics_a, metrics_b, metrics_c] if g in m.goods_traded)
        if present == 3:
            goods_overlap += 1
    results["trade_divergence"] = 1.0 - (goods_overlap / max(1, len(all_goods)))

    # Overall divergence score (0-1, higher = more different)
    scores = [v for v in results.values() if isinstance(v, float)]
    results["overall_divergence"] = sum(scores) / len(scores) if scores else 0.0

    return results


def _classify_fear(metrics: RunMetrics) -> str:
    """Classify what this captain feared based on telemetry, not prose.

    Each captain type has distinct fear families. The classifier asks:
    "what kind of danger was defining this captain's life?"

    Relief fears: delay, undercapacity, public failure
    Gray fears: seizure, exposure, paper closure
    Honor fears: escalation, crew loss, thin support
    """
    ct = metrics.captain_type

    if ct == "relief":
        # Relief fear: delivery lateness, runway compression, shortage pressure
        if metrics.delays > 3:
            return "delivery delay — late shipments eroding trust"
        if metrics.pay_missed > 0:
            return "undercapacity — runway too short for obligations"
        # Check if credits ever dipped below starting (500) mid-run
        if any(c < 300 for c in metrics.credits_history):
            return "public failure — visible decline in a legitimate path"
        return "schedule compression — too many stops, not enough margin"

    if ct == "gray":
        # Gray fear: seizure, exposure, paper closure
        if metrics.seizures > 0:
            return "seizure — cargo confiscated, cover blown"
        if metrics.retreats > metrics.combat_count * 0.3:
            return "exposure — too many close calls, scrutiny building"
        if metrics.delays > 2:
            return "paper closure — bureaucratic walls tightening"
        return "institutional pressure — the system remembering your name"

    if ct == "honor":
        # Honor fear: escalation, crew loss, thin support
        if metrics.crew_injuries > 2:
            return "crew loss — victories costing the people who fight beside you"
        if metrics.repairs_needed > 2:
            return "escalation — the ship can't take much more"
        if metrics.crew_departures > 0:
            return "thin support — allies leaving when the fights get real"
        return "combat attrition — winning fights but losing the war of wear"

    # Fallback for unknown captain types
    return "running out of options"


def generate_synthesis(
    metrics: RunMetrics,
) -> dict:
    """Generate the synthesis doc answers for one run.

    Answers:
    - What kind of captain did this become?
    - What did this run care about?
    - What was its main pressure?
    - What could it do that others couldn't?
    - What did it fear that others didn't?
    """
    # What it cared about (most visited stations)
    cared_about = metrics.dominant_stations[:2]

    # Main pressure
    if metrics.pay_missed > 2:
        pressure = "financial collapse"
    elif metrics.delays > 3:
        pressure = "time and access"
    elif metrics.crew_injuries > 3:
        pressure = "tactical survival"
    elif metrics.seizures > 0:
        pressure = "institutional exposure"
    else:
        pressure = "maintaining momentum"

    # What it feared — captain-specific detection from telemetry
    feared = _classify_fear(metrics)

    return {
        "captain_type": metrics.captain_type,
        "identity": metrics.captain_identity,
        "cared_about": cared_about,
        "main_pressure": pressure,
        "feared": feared,
        "days": metrics.days_simulated,
        "final_credits": metrics.final_credits,
        "combat_count": metrics.combat_count,
        "retreats": metrics.retreats,
        "crew_injuries": metrics.crew_injuries,
        "dominant_routes": metrics.dominant_lanes[:3],
        "goods_variety": len(metrics.goods_traded),
        "investigation_progress": metrics.final_investigation_progress,
    }
