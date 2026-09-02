"""Campaign integration layer — Star Freight Phase 6.

This is the glue. It wires crew, combat, culture, investigation, and
content into one playable loop. Every action flows through here so
the systems can transact with each other.

The campaign state is the single source of truth. All systems read
and write it. No system talks directly to another — they all go
through the campaign.

This is not a game engine. It's a state machine that proves the
systems produce a game.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random as _random

from portlight.engine.crew import (
    CrewMember,
    CrewRosterState,
    CrewRole,
    Civilization,
    CrewStatus,
    LoyaltyTier,
    recruit,
    dismiss,
    active_crew,
    fit_crew,
    crew_by_civ,
    get_ship_abilities,
    cultural_knowledge_level,
    cultural_access_check,
    get_combat_abilities,
    get_narrative_hooks,
    apply_morale_change,
    check_departures,
    injure,
    recover_day,
    add_loyalty_points,
    daily_loyalty_tick,
    calculate_crew_pay,
    apply_pay_result,
    crew_impact_report,
)
from portlight.engine.grid_combat import (
    Pos,
    TileType,
    Team,
    Combatant,
    CombatAbility,
    CombatState,
    CombatPhase,
    CombatResult,
    init_combat,
    start_turn,
    end_turn,
    action_move,
    action_attack,
    action_defend,
    action_retreat,
    action_ability,
    get_valid_targets,
    get_valid_moves,
    get_available_abilities,
    enemy_act,
    resolve_combat,
)
from portlight.engine.cultural_knowledge import (
    InteractionOutcome,
    CulturalInteraction,
    InteractionResult,
    evaluate_interaction,
    get_visible_options,
    get_crew_advice,
    keth_trade_interaction,
    veshan_encounter_interaction,
    VeshanDebt,
    KethSeason,
    get_keth_season,
    keth_season_visible,
    cultural_trade_modifier,
    cultural_encounter_options,
)
from portlight.engine.investigation import (
    EvidenceGrade,
    Fragment,
    InvestigationState,
    InvestigationThread,
    ThreadState,
    discover_fragment,
    check_lead_sources,
    check_delay_consequences,
    upgrade_corroborated,
    investigation_trade_impact,
    investigation_encounter_impact,
    investigation_narrative_impact,
    create_medical_cargo_thread,
    get_medical_cargo_fragments,
)
from portlight.content.star_freight import (
    SLICE_STATIONS,
    SLICE_LANES,
    SLICE_GOODS,
    SLICE_ENCOUNTERS,
    SLICE_CONTRACTS,
    create_thal,
    create_varek,
)


# ---------------------------------------------------------------------------
# Campaign state (the single source of truth)
# ---------------------------------------------------------------------------


@dataclass
class CampaignState:
    """Complete game state for the vertical slice."""

    captain_name: str = "Captain"
    credits: int = 500
    day: int = 1
    crew: CrewRosterState = field(default_factory=CrewRosterState)
    ship_hull: int = 1800
    ship_hull_max: int = 2000
    ship_shield: int = 200
    ship_shield_max: int = 250
    ship_fuel: int = 8
    ship_fuel_max: int = 8
    ship_cargo: list[str] = field(default_factory=list)
    ship_cargo_capacity: int = 8
    ship_weapon_power: int = 150
    ship_speed: int = 2
    reputation: dict[str, int] = field(
        default_factory=lambda: {
            "compact": -25,
            "keth": 0,
            "veshan.drashan": 0,
            "veshan.vekhari": 0,
            "orryn": 0,
            "reach.ironjaw": 0,
        }
    )
    cultural_knowledge: dict[str, int] = field(
        default_factory=lambda: {
            "compact": 1,
            "keth": 0,
            "veshan": 0,
            "orryn": 0,
            "reach": 0,
        }
    )
    investigation: InvestigationState = field(
        default_factory=lambda: InvestigationState(
            threads={"medical_cargo": create_medical_cargo_thread()},
        )
    )
    veshan_debts: list[VeshanDebt] = field(default_factory=list)
    current_station: str = "meridian_exchange"
    in_transit: bool = False
    pending_destination: str | None = None
    consequence_tags: list[str] = field(default_factory=list)
    seed: int = 42
    rng: _random.Random = field(default_factory=lambda: _random.Random(42))
    last_pay_day: int = 1
    danger_multiplier: float = 1.0  # world pressure: encounter rate scaling


# ---------------------------------------------------------------------------
# Campaign actions
# ---------------------------------------------------------------------------


def dock_at_station(state: CampaignState, station_id: str) -> dict:
    """Arrive at a station. Systems intersect here."""
    station = SLICE_STATIONS.get(station_id)
    if station is None:
        return {"error": f"Unknown station: {station_id}"}

    state.current_station = station_id
    state.in_transit = False
    events = []

    # Docking fee
    state.credits -= station.docking_fee
    events.append({"type": "fee", "amount": station.docking_fee})

    # Cultural greeting
    civ = (
        Civilization(station.civilization)
        if station.civilization in [c.value for c in Civilization]
        else None
    )
    knowledge = (
        cultural_knowledge_level(state.crew, civ, state.cultural_knowledge)
        if civ
        else 0
    )
    events.append(
        {
            "type": "cultural",
            "greeting": station.cultural_greeting,
            "knowledge_level": knowledge,
        }
    )

    # Investigation — station fragments
    for thread in state.investigation.threads.values():
        trigger = f"station_rumor_{station.civilization}_medical"
        matches = check_lead_sources(
            thread,
            "station",
            trigger,
            crew_ids=[m.id for m in active_crew(state.crew)],
            cultural_knowledge=state.cultural_knowledge,
            reputation=state.reputation,
        )
        for source in matches:
            frags = get_medical_cargo_fragments()
            if source.fragment_id in frags:
                frag = frags[source.fragment_id]
                frag.day_acquired = state.day
                result = discover_fragment(state.investigation, thread.id, frag)
                if not result.get("duplicate"):
                    events.append({"type": "investigation", "fragment": result})

    # Crew recovery
    for member in state.crew.members:
        recovery = recover_day(member)
        if recovery:
            events.append({"type": "crew_recovery", "event": recovery})

    # Delay consequences
    for delay in check_delay_consequences(state.investigation, state.day):
        events.append({"type": "investigation_delay", "warning": delay})
        state.consequence_tags.append(delay["consequence_tag"])

    return {"station": station_id, "events": events, "credits": state.credits}


def travel_to(state: CampaignState, destination: str) -> dict:
    """Transit along a lane. Encounters can interrupt."""
    lane = None
    for l in SLICE_LANES.values():
        if (l.station_a == state.current_station and l.station_b == destination) or (
            l.station_b == state.current_station and l.station_a == destination
        ):
            lane = l
            break

    if lane is None:
        return {"error": f"No lane from {state.current_station} to {destination}"}
    if state.ship_fuel < lane.distance_days:
        return {
            "error": f"Not enough fuel. Need {lane.distance_days}, have {state.ship_fuel}."
        }

    events = []
    encounter = None

    for _day_num in range(lane.distance_days):
        events.extend(_tick_day(state))

        # Encounter roll
        if (
            state.rng.random() < lane.danger * state.danger_multiplier
            and encounter is None
        ):
            civ = lane.controlled_by
            if civ == "disputed":
                civ = state.rng.choice(["compact", "reach"])
            arch_id = {"compact": "compact_patrol", "veshan": "veshan_challenge"}.get(
                civ, "reach_pirate"
            )
            encounter = {
                "archetype": arch_id,
                "civilization": civ,
                "cultural_options": cultural_encounter_options(
                    Civilization(civ)
                    if civ in [c.value for c in Civilization]
                    else Civilization.COMPACT,
                    state.crew,
                    state.cultural_knowledge,
                ),
            }
            events.append({"type": "encounter", "day": state.day})
            break

    if encounter is None:
        state.current_station = destination
        state.in_transit = False
        state.pending_destination = None
        events.append({"type": "arrival", "station": destination})
    else:
        state.in_transit = True
        state.pending_destination = destination

    return {
        "destination": destination,
        "events": events,
        "encounter": encounter,
        "credits": state.credits,
        "fuel": state.ship_fuel,
    }


# P1: Demand premiums — specialist goods command higher prices at demand stations.
# This lifts Gray (orryn goods) and Honor (veshan/luxury goods) without helping Relief.
_DEMAND_PREMIUMS: dict[str, float] = {
    # Gray/Honor specialist goods — higher premium (lifts thin-margin captains)
    "orryn_data": 1.7,  # intelligence is highly valued
    "orryn_brokered_goods": 1.6,  # cross-civ brokered goods carry markup
    "veshan_weapons": 1.6,  # weapons in demand carry premium
    "black_seal_resin": 1.7,  # luxury status good
    "bond_plate": 1.6,  # legal certification has institutional value
    # Relief volume goods — lower premium (trims dominant loop)
    "medical_supplies": 1.3,  # widely needed but commoditized
    "keth_organics": 1.35,  # broad demand, lower premium
}


def _demand_premium(good_id: str) -> float:
    """Get demand premium multiplier for a good. Default 1.5, specialist goods higher."""
    return _DEMAND_PREMIUMS.get(good_id, 1.5)


def execute_trade(
    state: CampaignState, good_id: str, action: str, quantity: int = 1
) -> dict:
    """Buy or sell goods. Cultural knowledge affects prices. Trade can trigger investigation."""
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return {"error": "Not at a station"}
    good = SLICE_GOODS.get(good_id)
    if good is None:
        return {"error": f"Unknown good: {good_id}"}

    civ = (
        Civilization(station.civilization)
        if station.civilization in [c.value for c in Civilization]
        else None
    )
    price_mod = (
        cultural_trade_modifier(civ, state.crew, state.cultural_knowledge, state.day)
        if civ
        else 0.0
    )

    base_price = good.base_price
    if good_id in station.produces:
        # Source discount: 35% off normally, reduced for Relief-dominant loop goods
        source_mult = 0.65
        if good_id in ("keth_organics", "medical_supplies"):
            source_mult = 0.72  # P1: trim Relief compounding on volume goods
        base_price = int(base_price * source_mult)
    elif good_id in station.demands:
        # Demand premium: base 50%, higher for specialist goods
        demand_mult = _demand_premium(good_id)
        base_price = int(base_price * demand_mult)
    price = max(1, int(base_price * (1.0 + price_mod)))

    if action == "buy":
        if good.cultural_restriction and civ:
            ok, reason = cultural_access_check(
                state.crew,
                civ,
                state.cultural_knowledge,
                station.knowledge_required_for_restricted,
            )
            if not ok:
                return {"error": f"Cannot buy {good.name}: {reason}"}
        total = price * quantity
        if state.credits < total:
            return {"error": f"Cannot afford {quantity}x {good.name} ({total}₡)."}
        if len(state.ship_cargo) + quantity > state.ship_cargo_capacity:
            return {"error": "Cargo hold full."}
        state.credits -= total
        for _ in range(quantity):
            state.ship_cargo.append(good_id)
        result = {
            "action": "buy",
            "good": good.name,
            "quantity": quantity,
            "price_each": price,
            "total": total,
            "credits": state.credits,
        }
    elif action == "sell":
        count = state.ship_cargo.count(good_id)
        if count < quantity:
            return {"error": f"Only have {count}x {good.name}."}
        total = price * quantity
        state.credits += total
        for _ in range(quantity):
            state.ship_cargo.remove(good_id)
        if civ and station.civilization in state.reputation:
            state.reputation[station.civilization] = min(
                100, state.reputation[station.civilization] + 1
            )
        result = {
            "action": "sell",
            "good": good.name,
            "quantity": quantity,
            "price_each": price,
            "total": total,
            "credits": state.credits,
        }
    else:
        return {"error": f"Unknown action: {action}"}

    # Investigation trigger
    if good_id == "medical_supplies" and station.civilization == "keth":
        for thread in state.investigation.threads.values():
            for source in check_lead_sources(
                thread,
                "trade",
                "trade_medical_at_keth",
                [m.id for m in active_crew(state.crew)],
                state.cultural_knowledge,
                state.reputation,
            ):
                frags = get_medical_cargo_fragments()
                if source.fragment_id in frags:
                    frag = frags[source.fragment_id]
                    frag.day_acquired = state.day
                    disc = discover_fragment(state.investigation, thread.id, frag)
                    if not disc.get("duplicate"):
                        result["investigation"] = disc

    return result


def begin_combat(state: CampaignState, encounter: dict) -> CombatState:
    """Open a live CombatState from campaign + encounter. Does not auto-play."""
    arch = SLICE_ENCOUNTERS.get(
        encounter["archetype"], SLICE_ENCOUNTERS["reach_pirate"]
    )

    abilities = []
    for ab in get_ship_abilities(state.crew):
        abilities.append(
            CombatAbility(
                id=ab["ability"],
                name=ab["ability"].replace("_", " ").title(),
                description=f"Crew: {ab['crew_name']}",
                action_cost=1,
                cooldown=2,
                effect_type="heal" if "repair" in ab["ability"] else "damage",
                effect_value=300 if "repair" in ab["ability"] else 400,
                crew_source=ab["crew_name"],
                degraded=ab["degraded"],
            )
        )

    player_ship = Combatant(
        id="player_ship",
        name="Star Freighter Nyx",
        team=Team.PLAYER,
        pos=Pos(1, 3),
        hp=state.ship_hull,
        hp_max=state.ship_hull_max,
        shield=state.ship_shield,
        shield_max=state.ship_shield_max,
        speed=state.ship_speed,
        evasion=0.1,
        armor=10,
        base_attack_damage=state.ship_weapon_power,
        base_attack_range=3,
        abilities=abilities,
    )
    enemy_ship = Combatant(
        id="enemy_1",
        name=arch.name,
        team=Team.ENEMY,
        pos=Pos(6, 3),
        hp=arch.ship_hull,
        hp_max=arch.ship_hull,
        shield=arch.ship_shield,
        shield_max=arch.ship_shield,
        speed=arch.ship_speed,
        evasion=0.15,
        armor=5,
        base_attack_damage=arch.ship_damage,
        base_attack_range=3,
    )

    cs = init_combat([player_ship], [enemy_ship], seed=state.seed + state.day)
    start_turn(cs)
    return cs


def finish_combat(
    state: CampaignState,
    cs: CombatState,
    encounter: dict,
    escalation_factor: float = 0.0,
) -> CombatResult:
    """Resolve a completed CombatState and write it back to the campaign."""
    result = resolve_combat(
        cs,
        encounter.get("civilization", ""),
        list(state.ship_cargo),
        escalation_factor=escalation_factor,
    )

    state.ship_hull = result.player_hull_remaining
    state.ship_shield = result.player_shield_remaining
    state.credits += result.credits_gained
    for f, d in result.reputation_delta.items():
        if f in state.reputation:
            state.reputation[f] = max(-100, min(100, state.reputation[f] + d))
    for g in result.cargo_lost:
        if g in state.ship_cargo:
            state.ship_cargo.remove(g)
    for cid in result.crew_injuries:
        for m in state.crew.members:
            if m.id == cid and m.status == CrewStatus.ACTIVE:
                injure(m, 5)
    state.consequence_tags.extend(result.consequence_tags)

    if result.outcome == CombatPhase.VICTORY:
        for thread in state.investigation.threads.values():
            for source in check_lead_sources(
                thread,
                "combat",
                "salvage_freighter_debris",
                [m.id for m in active_crew(state.crew)],
                state.cultural_knowledge,
                state.reputation,
            ):
                frags = get_medical_cargo_fragments()
                if source.fragment_id in frags:
                    frag = frags[source.fragment_id]
                    frag.day_acquired = state.day
                    discover_fragment(state.investigation, thread.id, frag)

    return result


def run_combat(
    state: CampaignState,
    encounter: dict,
    strategy: str = "aggressive",
    escalation_factor: float = 0.0,
) -> CombatResult:
    """Auto-resolve combat (CLI / playtest) and write back to campaign state."""
    cs = begin_combat(state, encounter)

    for _ in range(100):
        if cs.phase != CombatPhase.ACTIVE:
            break
        current = cs.current_actor
        if current is None:
            break
        if current.team == Team.PLAYER:
            if strategy == "retreat":
                action_retreat(cs, current.id)
            else:
                if current.hp < current.hp_max * 0.5:
                    avail = get_available_abilities(cs, current.id)
                    heal = next((a for a in avail if a.effect_type == "heal"), None)
                    if heal:
                        action_ability(cs, current.id, heal.id, current.id)
                targets = get_valid_targets(cs, current.id)
                if targets and current.actions_remaining > 0:
                    action_attack(cs, current.id, targets[0])
                elif current.actions_remaining > 0:
                    moves = get_valid_moves(cs, current.id)
                    if moves:
                        action_move(
                            cs,
                            current.id,
                            min(moves, key=lambda m: m.distance_to(Pos(6, 3))),
                        )
                if current.actions_remaining > 0:
                    targets = get_valid_targets(cs, current.id)
                    if targets:
                        action_attack(cs, current.id, targets[0])
                    else:
                        action_defend(cs, current.id)
        else:
            enemy_act(cs, current.id)
        end_turn(cs)

    return finish_combat(state, cs, encounter, escalation_factor=escalation_factor)


# ---------------------------------------------------------------------------
# Approach — the encounter decision surface (C2)
#
# Every interdiction opens an approach: stakes first, then Negotiate / Flee /
# Fight. The grid is only reached on Fight. A Veshan honor challenge (behavior
# "honor") cannot skip the grid — refusing is dishonor, so negotiate and flee
# are closed. These are read/resolve helpers; the TUI ApproachScreen drives them.
# ---------------------------------------------------------------------------


def _encounter_archetype(encounter: dict) -> "EncounterArchetype":
    return SLICE_ENCOUNTERS.get(
        encounter.get("archetype", ""), SLICE_ENCOUNTERS["reach_pirate"]
    )


def approach_encounter(state: CampaignState, encounter: dict) -> dict:
    """Stakes + available approaches for an interdiction. Pure read, no writes."""
    arch = _encounter_archetype(encounter)
    opts = encounter.get("cultural_options", {}) or {}
    must_fight = arch.behavior == "honor"
    knowledge = int(opts.get("knowledge_level", 0))
    can_negotiate = bool(opts.get("can_negotiate")) and not must_fight
    can_flee = not must_fight

    dest = state.pending_destination
    dest_name = ""
    if dest:
        st = SLICE_STATIONS.get(dest)
        dest_name = st.name if st else dest

    return {
        "archetype": arch.id,
        "name": arch.name,
        "civilization": arch.civilization,
        "behavior": arch.behavior,
        "description": arch.description,
        "must_fight": must_fight,
        "can_negotiate": can_negotiate,
        "can_flee": can_flee,
        "knowledge_level": knowledge,
        "negotiate_hint": arch.cultural_option,
        "flee_consequence": arch.retreat_consequence,
        "victory_consequence": arch.victory_consequence,
        "defeat_consequence": arch.defeat_consequence,
        "enemy_hull": arch.ship_hull,
        "enemy_shield": arch.ship_shield,
        "enemy_damage": arch.ship_damage,
        "player_hull": state.ship_hull,
        "player_hull_max": state.ship_hull_max,
        "cargo": list(state.ship_cargo),
        "destination": dest,
        "destination_name": dest_name,
    }


def _cargo_name(good_id: str) -> str:
    good = SLICE_GOODS.get(good_id)
    return good.name if good else good_id


def negotiate_encounter(state: CampaignState, encounter: dict) -> dict:
    """Talk instead of fight. Requires cultural standing; grid is skipped.

    On success you resolve the transit and dock at the pending destination.
    """
    info = approach_encounter(state, encounter)
    if info["must_fight"]:
        return {
            "resolved": False,
            "error": "A Veshan honor challenge cannot be talked away.",
        }
    if not info["can_negotiate"]:
        return {
            "resolved": False,
            "error": "You lack the cultural standing to negotiate this. Fight or flee.",
        }

    arch = _encounter_archetype(encounter)
    civ = encounter.get("civilization", "")
    reputation_delta: dict[str, int] = {}
    credits_spent = 0

    if arch.id == "compact_patrol":
        # Comply and present papers — the Compact notes your cooperation.
        if civ in state.reputation:
            state.reputation[civ] = min(100, state.reputation[civ] + 2)
            reputation_delta[civ] = 2
        line = (
            "You submit to inspection and present your permits. "
            "The patrol logs your cooperation and waves you through."
        )
    elif arch.id == "reach_pirate":
        # Buy them off — the Reach respect a paid debt more than a fight.
        toll = min(state.credits, 60 + arch.ship_damage // 2)
        state.credits -= toll
        credits_spent = toll
        line = (
            f"You open a channel and buy the raiders off for {toll}\u20a1. "
            "They peel away to hunt easier prey."
        )
    else:
        line = "You talk your way clear of the encounter."

    state.consequence_tags.append(f"negotiated_{arch.id}")

    arrival = resolve_transit(state) if state.in_transit else {}
    return {
        "resolved": True,
        "outcome": "negotiated",
        "line": line,
        "reputation_delta": reputation_delta,
        "credits_spent": credits_spent,
        "arrival": arrival,
        "destination_name": info["destination_name"],
    }


def flee_encounter(state: CampaignState, encounter: dict) -> dict:
    """Run rather than fight. Aborts the voyage back to the origin station.

    Cost is the archetype's retreat consequence: Reach raiders take a cargo
    unit; a Compact patrol flags you as wanted. Honor challenges cannot be fled.
    """
    info = approach_encounter(state, encounter)
    if info["must_fight"]:
        return {
            "resolved": False,
            "error": "Refusing a Veshan honor challenge is dishonor. You cannot flee.",
        }

    arch = _encounter_archetype(encounter)
    civ = encounter.get("civilization", "")
    cargo_lost: list[str] = []
    reputation_delta: dict[str, int] = {}

    if arch.id == "compact_patrol":
        if civ in state.reputation:
            state.reputation[civ] = max(-100, state.reputation[civ] - 10)
            reputation_delta[civ] = -10
        state.consequence_tags.append("wanted_compact")
        line = (
            "You burn past the patrol and run the blockade. Your transponder is "
            "flagged system-wide — the Compact will remember this."
        )
    elif arch.id == "reach_pirate":
        if state.ship_cargo:
            dropped = state.ship_cargo.pop()
            cargo_lost.append(dropped)
            line = (
                f"You jettison {_cargo_name(dropped)} and run dark. "
                "The raiders break off to scoop the spoils."
            )
        else:
            line = (
                "You run with an empty hold. The raiders give chase but your "
                "engines hold and you slip into the dark."
            )
        state.consequence_tags.append("fled_reach")
    else:
        line = "You disengage and slip away into the dark."

    # Fleeing aborts the run — you fall back to the station you left.
    state.in_transit = False
    state.pending_destination = None

    return {
        "resolved": True,
        "outcome": "fled",
        "line": line,
        "cargo_lost": cargo_lost,
        "reputation_delta": reputation_delta,
    }


def get_campaign_summary(state: CampaignState) -> dict:
    """Snapshot for testing and display."""
    return {
        "day": state.day,
        "credits": state.credits,
        "station": state.current_station,
        "fuel": state.ship_fuel,
        "hull": f"{state.ship_hull}/{state.ship_hull_max}",
        "cargo": list(state.ship_cargo),
        "crew": [m.name for m in active_crew(state.crew)],
        "crew_fit": len(fit_crew(state.crew)),
        "reputation": dict(state.reputation),
        "cultural_knowledge": dict(state.cultural_knowledge),
        "investigation_progress": state.investigation.total_progress,
        "consequence_tags": list(state.consequence_tags),
        "monthly_cost": calculate_crew_pay(state.crew),
        "captain": state.captain_name,
    }


# ---------------------------------------------------------------------------
# Day ticks, station services, persistence
# ---------------------------------------------------------------------------


def _tick_day(state: CampaignState, *, burn_fuel: bool = True) -> list[dict]:
    """One campaign day: crew, pay, optional fuel. Used by travel and idle advance."""
    events: list[dict] = []
    state.day += 1
    if burn_fuel:
        state.ship_fuel = max(0, state.ship_fuel - 1)

    for member in active_crew(state.crew):
        loyalty = daily_loyalty_tick(member)
        if loyalty and loyalty.get("unlocks"):
            events.append({"type": "loyalty_unlock", "event": loyalty})
        recover_day(member)

    if state.day - state.last_pay_day >= 30:
        pay_due = calculate_crew_pay(state.crew)
        paid = state.credits >= pay_due
        if paid:
            state.credits -= pay_due
        apply_pay_result(state.crew, paid=paid)
        events.append({"type": "pay", "amount": pay_due, "paid": paid})
        state.last_pay_day = state.day

    for dep in check_departures(state.crew):
        events.append({"type": "crew_departure", "event": dep})
    return events


def advance_docked(state: CampaignState) -> dict:
    """Spend a day at the current station."""
    if state.in_transit:
        return {"error": "In transit."}
    events = _tick_day(state, burn_fuel=False)
    return {
        "day": state.day,
        "events": events,
        "credits": state.credits,
        "fuel": state.ship_fuel,
    }


def resolve_transit(state: CampaignState) -> dict:
    """Finish a lane after an encounter. Docks at the pending destination."""
    dest = state.pending_destination
    if not dest:
        return {"error": "Not in transit to a destination."}
    state.pending_destination = None
    state.in_transit = False
    return dock_at_station(state, dest)


def start_campaign(
    captain_name: str = "Captain",
    seed: int | None = None,
    starting_station: str = "meridian_exchange",
) -> CampaignState:
    """Live-game start. Empty crew, Meridian Exchange, Compact disgrace standing."""
    if seed is None:
        seed = _random.randint(1, 10_000_000)
    state = CampaignState(
        captain_name=captain_name,
        seed=seed,
        rng=_random.Random(seed),
        current_station=starting_station,
    )
    dock_at_station(state, starting_station)
    return state


def hire_crew(state: CampaignState, crew_id: str) -> dict:
    """Recruit an overlay crew member at the current station."""
    from portlight.content.star_freight import (
        STATION_HIRES,
        create_crew,
        SLICE_STATIONS,
    )
    from portlight.engine.crew import can_recruit, recruit as do_recruit

    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return {"error": "Not at a station."}
    if "crew_hire" not in station.services:
        return {"error": f"{station.name} does not hire crew."}
    available = STATION_HIRES.get(state.current_station, [])
    if crew_id not in available:
        return {"error": f"{crew_id} is not hiring here."}
    member = create_crew(crew_id)
    cost = member.pay_rate
    err = can_recruit(state.crew, member.id, state.credits, cost)
    if err:
        return {"error": err}
    state.credits -= cost
    do_recruit(state.crew, member)
    return {"hired": member.name, "cost": cost, "credits": state.credits}


def refuel(state: CampaignState, days: int | None = None) -> dict:
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return {"error": "Not at a station."}
    if "fuel" not in station.services:
        return {"error": "No fuel here."}
    need = state.ship_fuel_max - state.ship_fuel
    qty = need if days is None else min(days, need)
    if qty <= 0:
        return {"error": "Tanks are full."}
    cost = qty * station.fuel_cost_per_day
    if state.credits < cost:
        return {"error": f"Fuel costs {cost}₡. You have {state.credits}₡."}
    state.credits -= cost
    state.ship_fuel += qty
    return {
        "fueled": qty,
        "cost": cost,
        "fuel": state.ship_fuel,
        "credits": state.credits,
    }


def repair_ship(state: CampaignState, points: int | None = None) -> dict:
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return {"error": "Not at a station."}
    if "repair" not in station.services and "drydock" not in station.services:
        return {"error": "No repair here."}
    need = state.ship_hull_max - state.ship_hull
    qty = need if points is None else min(points, need)
    if qty <= 0:
        return {"error": "Hull is intact."}
    cost = qty * station.repair_cost_per_point
    if state.credits < cost:
        return {"error": f"Repair costs {cost}₡. You have {state.credits}₡."}
    state.credits -= cost
    state.ship_hull += qty
    return {
        "repaired": qty,
        "cost": cost,
        "hull": state.ship_hull,
        "credits": state.credits,
    }


def campaign_to_dict(state: CampaignState) -> dict:
    """JSON-safe campaign snapshot. RNG is rebuilt from seed+day on load."""
    return {
        "kind": "star-freight",
        "version": 1,
        "captain_name": state.captain_name,
        "credits": state.credits,
        "day": state.day,
        "crew": [_crew_to_dict(m) for m in state.crew.members],
        "departed": list(state.crew.departed),
        "ship_hull": state.ship_hull,
        "ship_hull_max": state.ship_hull_max,
        "ship_shield": state.ship_shield,
        "ship_shield_max": state.ship_shield_max,
        "ship_fuel": state.ship_fuel,
        "ship_fuel_max": state.ship_fuel_max,
        "ship_cargo": list(state.ship_cargo),
        "ship_cargo_capacity": state.ship_cargo_capacity,
        "ship_weapon_power": state.ship_weapon_power,
        "ship_speed": state.ship_speed,
        "reputation": dict(state.reputation),
        "cultural_knowledge": dict(state.cultural_knowledge),
        "veshan_debts": [
            {
                "id": d.id,
                "house": d.house,
                "weight": d.weight,
                "direction": d.direction,
                "description": d.description,
                "day_created": d.day_created,
                "age_days": d.age_days,
            }
            for d in state.veshan_debts
        ],
        "current_station": state.current_station,
        "in_transit": state.in_transit,
        "pending_destination": state.pending_destination,
        "consequence_tags": list(state.consequence_tags),
        "seed": state.seed,
        "last_pay_day": state.last_pay_day,
        "danger_multiplier": state.danger_multiplier,
        "investigation": _investigation_to_dict(state.investigation),
    }


def campaign_from_dict(data: dict) -> CampaignState:
    from portlight.engine.crew import CrewRosterState
    from portlight.engine.cultural_knowledge import VeshanDebt

    seed = int(data.get("seed", 42))
    day = int(data.get("day", 1))
    members = [_crew_from_dict(m) for m in data.get("crew", [])]
    state = CampaignState(
        captain_name=data.get("captain_name", "Captain"),
        credits=int(data.get("credits", 500)),
        day=day,
        crew=CrewRosterState(members=members, departed=list(data.get("departed", []))),
        ship_hull=int(data.get("ship_hull", 1800)),
        ship_hull_max=int(data.get("ship_hull_max", 2000)),
        ship_shield=int(data.get("ship_shield", 200)),
        ship_shield_max=int(data.get("ship_shield_max", 250)),
        ship_fuel=int(data.get("ship_fuel", 8)),
        ship_fuel_max=int(data.get("ship_fuel_max", 8)),
        ship_cargo=list(data.get("ship_cargo", [])),
        ship_cargo_capacity=int(data.get("ship_cargo_capacity", 8)),
        ship_weapon_power=int(data.get("ship_weapon_power", 150)),
        ship_speed=int(data.get("ship_speed", 2)),
        reputation=dict(data.get("reputation", {})),
        cultural_knowledge=dict(data.get("cultural_knowledge", {})),
        current_station=data.get("current_station", "meridian_exchange"),
        in_transit=bool(data.get("in_transit", False)),
        pending_destination=data.get("pending_destination"),
        consequence_tags=list(data.get("consequence_tags", [])),
        seed=seed,
        rng=_random.Random(seed + day),
        last_pay_day=int(data.get("last_pay_day", 1)),
        danger_multiplier=float(data.get("danger_multiplier", 1.0)),
        veshan_debts=[
            VeshanDebt(
                id=d["id"],
                house=d["house"],
                weight=d["weight"],
                direction=d["direction"],
                description=d.get("description", ""),
                day_created=int(d.get("day_created", 0)),
                age_days=int(d.get("age_days", 0)),
            )
            for d in data.get("veshan_debts", [])
        ],
    )
    inv = data.get("investigation")
    if inv:
        state.investigation = _investigation_from_dict(inv)
    return state


def _crew_to_dict(m) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "civilization": m.civilization.value,
        "role": m.role.value,
        "hp": m.hp,
        "hp_max": m.hp_max,
        "speed": m.speed,
        "abilities": list(m.abilities),
        "ship_skill": m.ship_skill,
        "morale": m.morale,
        "morale_streak": m.morale_streak,
        "loyalty_tier": m.loyalty_tier.value,
        "loyalty_points": m.loyalty_points,
        "status": m.status.value,
        "injury_days_remaining": m.injury_days_remaining,
        "pay_rate": m.pay_rate,
        "narrative_hooks": list(m.narrative_hooks),
        "personal_quest_available": m.personal_quest_available,
        "loyalty_mission_available": m.loyalty_mission_available,
        "opinions": dict(m.opinions),
    }


def _crew_from_dict(d: dict):
    from portlight.engine.crew import (
        CrewMember,
        CrewRole,
        Civilization,
        LoyaltyTier,
        CrewStatus,
    )

    return CrewMember(
        id=d["id"],
        name=d["name"],
        civilization=Civilization(d["civilization"]),
        role=CrewRole(d["role"]),
        hp=int(d.get("hp", 100)),
        hp_max=int(d.get("hp_max", 100)),
        speed=int(d.get("speed", 3)),
        abilities=list(d.get("abilities", [])),
        ship_skill=d.get("ship_skill", ""),
        morale=int(d.get("morale", 45)),
        morale_streak=int(d.get("morale_streak", 0)),
        loyalty_tier=LoyaltyTier(d.get("loyalty_tier", "stranger")),
        loyalty_points=int(d.get("loyalty_points", 0)),
        status=CrewStatus(d.get("status", "active")),
        injury_days_remaining=int(d.get("injury_days_remaining", 0)),
        pay_rate=int(d.get("pay_rate", 50)),
        narrative_hooks=list(d.get("narrative_hooks", [])),
        personal_quest_available=bool(d.get("personal_quest_available", False)),
        loyalty_mission_available=bool(d.get("loyalty_mission_available", False)),
        opinions=dict(d.get("opinions", {})),
    )


def _investigation_to_dict(inv: InvestigationState) -> dict:
    threads = {}
    for tid, thread in inv.threads.items():
        threads[tid] = {
            "id": thread.id,
            "title": thread.title,
            "premise": thread.premise,
            "resolution_threshold": thread.resolution_threshold,
            "fragments_required": thread.fragments_required,
            "max_delay_days": thread.max_delay_days,
            "delay_consequence_tag": thread.delay_consequence_tag,
            "state": thread.state.value,
            "discovered_day": thread.discovered_day,
            "last_progress_day": thread.last_progress_day,
            "fragments": [_fragment_to_dict(f) for f in thread.fragments],
            "sources": [_source_to_dict(s) for s in thread.sources],
        }
    return {
        "threads": threads,
        "all_fragments": [_fragment_to_dict(f) for f in inv.all_fragments],
        "total_progress": inv.total_progress,
        "delay_warnings_issued": list(inv.delay_warnings_issued),
    }


def _investigation_from_dict(data: dict) -> InvestigationState:
    from portlight.engine.investigation import (
        InvestigationState,
        InvestigationThread,
        ThreadState,
    )

    threads = {}
    for tid, t in data.get("threads", {}).items():
        threads[tid] = InvestigationThread(
            id=t["id"],
            title=t["title"],
            premise=t["premise"],
            resolution_threshold=int(t["resolution_threshold"]),
            fragments_required=int(t["fragments_required"]),
            max_delay_days=int(t["max_delay_days"]),
            delay_consequence_tag=t.get("delay_consequence_tag", ""),
            state=ThreadState(t.get("state", "dormant")),
            discovered_day=int(t.get("discovered_day", 0)),
            last_progress_day=int(t.get("last_progress_day", 0)),
            fragments=[_fragment_from_dict(f) for f in t.get("fragments", [])],
            sources=[_source_from_dict(s) for s in t.get("sources", [])],
        )
    return InvestigationState(
        threads=threads,
        all_fragments=[_fragment_from_dict(f) for f in data.get("all_fragments", [])],
        total_progress=int(data.get("total_progress", 0)),
        delay_warnings_issued=list(data.get("delay_warnings_issued", [])),
    )


def _fragment_to_dict(f) -> dict:
    return {
        "id": f.id,
        "thread_id": f.thread_id,
        "content": f.content,
        "source_type": f.source_type,
        "source_detail": f.source_detail,
        "grade": f.grade.value,
        "day_acquired": f.day_acquired,
        "connections": list(f.connections),
        "crew_interpreter": f.crew_interpreter,
        "acted_on": f.acted_on,
    }


def _fragment_from_dict(d: dict):
    from portlight.engine.investigation import Fragment, EvidenceGrade

    return Fragment(
        id=d["id"],
        thread_id=d["thread_id"],
        content=d["content"],
        source_type=d["source_type"],
        source_detail=d.get("source_detail", ""),
        grade=EvidenceGrade(d["grade"]),
        day_acquired=int(d.get("day_acquired", 0)),
        connections=list(d.get("connections", [])),
        crew_interpreter=d.get("crew_interpreter", ""),
        acted_on=bool(d.get("acted_on", False)),
    )


def _source_to_dict(s) -> dict:
    return {
        "fragment_id": s.fragment_id,
        "source_type": s.source_type.value
        if hasattr(s.source_type, "value")
        else s.source_type,
        "trigger": s.trigger,
        "crew_required": s.crew_required,
        "civ_knowledge_required": s.civ_knowledge_required,
        "knowledge_level_required": s.knowledge_level_required,
        "reputation_required": dict(s.reputation_required),
        "description": s.description,
    }


def _source_from_dict(d: dict):
    from portlight.engine.investigation import LeadSource, SourceType

    st = d.get("source_type", "station")
    return LeadSource(
        fragment_id=d["fragment_id"],
        source_type=SourceType(st) if not isinstance(st, SourceType) else st,
        trigger=d.get("trigger", ""),
        crew_required=d.get("crew_required", ""),
        civ_knowledge_required=d.get("civ_knowledge_required", ""),
        knowledge_level_required=int(d.get("knowledge_level_required", 0)),
        reputation_required=dict(d.get("reputation_required", {})),
        description=d.get("description", ""),
    )


def _dataclass_enum_dict(obj) -> dict:
    from dataclasses import asdict, is_dataclass

    if is_dataclass(obj) and not isinstance(obj, type):
        raw = asdict(obj)
        return {k: (v.value if hasattr(v, "value") else v) for k, v in raw.items()}
    return {"value": str(obj)}
