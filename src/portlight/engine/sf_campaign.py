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
    credits: int = 500
    day: int = 1
    crew: CrewRosterState = field(default_factory=CrewRosterState)
    ship_hull: int = 1800
    ship_hull_max: int = 2000
    ship_shield: int = 200
    ship_shield_max: int = 250
    ship_fuel: int = 8
    ship_cargo: list[str] = field(default_factory=list)
    ship_cargo_capacity: int = 8
    ship_weapon_power: int = 150
    ship_speed: int = 2
    reputation: dict[str, int] = field(default_factory=lambda: {
        "compact": -25, "keth": 0, "veshan.drashan": 0,
        "veshan.vekhari": 0, "orryn": 0, "reach.ironjaw": 0,
    })
    cultural_knowledge: dict[str, int] = field(default_factory=lambda: {
        "compact": 1, "keth": 0, "veshan": 0, "orryn": 0, "reach": 0,
    })
    investigation: InvestigationState = field(default_factory=lambda: InvestigationState(
        threads={"medical_cargo": create_medical_cargo_thread()},
    ))
    veshan_debts: list[VeshanDebt] = field(default_factory=list)
    current_station: str = "meridian_exchange"
    in_transit: bool = False
    consequence_tags: list[str] = field(default_factory=list)
    seed: int = 42
    rng: _random.Random = field(default_factory=lambda: _random.Random(42))
    last_pay_day: int = 1


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
    civ = Civilization(station.civilization) if station.civilization in [c.value for c in Civilization] else None
    knowledge = cultural_knowledge_level(state.crew, civ, state.cultural_knowledge) if civ else 0
    events.append({"type": "cultural", "greeting": station.cultural_greeting, "knowledge_level": knowledge})

    # Investigation — station fragments
    for thread in state.investigation.threads.values():
        trigger = f"station_rumor_{station.civilization}_medical"
        matches = check_lead_sources(
            thread, "station", trigger,
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
        if (l.station_a == state.current_station and l.station_b == destination) or \
           (l.station_b == state.current_station and l.station_a == destination):
            lane = l
            break

    if lane is None:
        return {"error": f"No lane from {state.current_station} to {destination}"}
    if state.ship_fuel < lane.distance_days:
        return {"error": f"Not enough fuel. Need {lane.distance_days}, have {state.ship_fuel}."}

    events = []
    encounter = None

    for day_num in range(lane.distance_days):
        state.day += 1
        state.ship_fuel -= 1

        # Crew ticks
        for member in active_crew(state.crew):
            loyalty = daily_loyalty_tick(member)
            if loyalty and loyalty.get("unlocks"):
                events.append({"type": "loyalty_unlock", "event": loyalty})
            recover_day(member)

        # Pay check
        if state.day - state.last_pay_day >= 30:
            pay_due = calculate_crew_pay(state.crew)
            paid = state.credits >= pay_due
            if paid:
                state.credits -= pay_due
            apply_pay_result(state.crew, paid=paid)
            events.append({"type": "pay", "amount": pay_due, "paid": paid})
            state.last_pay_day = state.day

        # Departures
        for dep in check_departures(state.crew):
            events.append({"type": "crew_departure", "event": dep})

        # Encounter roll
        if state.rng.random() < lane.danger and encounter is None:
            civ = lane.controlled_by
            if civ == "disputed":
                civ = state.rng.choice(["compact", "reach"])
            arch_id = {"compact": "compact_patrol", "veshan": "veshan_challenge"}.get(civ, "reach_pirate")
            encounter = {
                "archetype": arch_id,
                "civilization": civ,
                "cultural_options": cultural_encounter_options(
                    Civilization(civ) if civ in [c.value for c in Civilization] else Civilization.COMPACT,
                    state.crew, state.cultural_knowledge,
                ),
            }
            events.append({"type": "encounter", "day": state.day})
            break

    if encounter is None:
        state.current_station = destination
        state.in_transit = False
        events.append({"type": "arrival", "station": destination})

    return {"destination": destination, "events": events, "encounter": encounter,
            "credits": state.credits, "fuel": state.ship_fuel}


# P1: Demand premiums — specialist goods command higher prices at demand stations.
# This lifts Gray (orryn goods) and Honor (veshan/luxury goods) without helping Relief.
_DEMAND_PREMIUMS: dict[str, float] = {
    # Gray/Honor specialist goods — higher premium (lifts thin-margin captains)
    "orryn_data": 1.7,            # intelligence is highly valued
    "orryn_brokered_goods": 1.6,  # cross-civ brokered goods carry markup
    "veshan_weapons": 1.6,        # weapons in demand carry premium
    "black_seal_resin": 1.7,      # luxury status good
    "bond_plate": 1.6,            # legal certification has institutional value
    # Relief volume goods — lower premium (trims dominant loop)
    "medical_supplies": 1.3,      # widely needed but commoditized
    "keth_organics": 1.35,        # broad demand, lower premium
}


def _demand_premium(good_id: str) -> float:
    """Get demand premium multiplier for a good. Default 1.5, specialist goods higher."""
    return _DEMAND_PREMIUMS.get(good_id, 1.5)


def execute_trade(state: CampaignState, good_id: str, action: str, quantity: int = 1) -> dict:
    """Buy or sell goods. Cultural knowledge affects prices. Trade can trigger investigation."""
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return {"error": "Not at a station"}
    good = SLICE_GOODS.get(good_id)
    if good is None:
        return {"error": f"Unknown good: {good_id}"}

    civ = Civilization(station.civilization) if station.civilization in [c.value for c in Civilization] else None
    price_mod = cultural_trade_modifier(civ, state.crew, state.cultural_knowledge, state.day) if civ else 0.0

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
                state.crew, civ, state.cultural_knowledge,
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
        result = {"action": "buy", "good": good.name, "quantity": quantity,
                  "price_each": price, "total": total, "credits": state.credits}
    elif action == "sell":
        count = state.ship_cargo.count(good_id)
        if count < quantity:
            return {"error": f"Only have {count}x {good.name}."}
        total = price * quantity
        state.credits += total
        for _ in range(quantity):
            state.ship_cargo.remove(good_id)
        if civ and station.civilization in state.reputation:
            state.reputation[station.civilization] = min(100, state.reputation[station.civilization] + 1)
        result = {"action": "sell", "good": good.name, "quantity": quantity,
                  "price_each": price, "total": total, "credits": state.credits}
    else:
        return {"error": f"Unknown action: {action}"}

    # Investigation trigger
    if good_id == "medical_supplies" and station.civilization == "keth":
        for thread in state.investigation.threads.values():
            for source in check_lead_sources(
                thread, "trade", "trade_medical_at_keth",
                [m.id for m in active_crew(state.crew)],
                state.cultural_knowledge, state.reputation,
            ):
                frags = get_medical_cargo_fragments()
                if source.fragment_id in frags:
                    frag = frags[source.fragment_id]
                    frag.day_acquired = state.day
                    disc = discover_fragment(state.investigation, thread.id, frag)
                    if not disc.get("duplicate"):
                        result["investigation"] = disc

    return result


def run_combat(
    state: CampaignState, encounter: dict, strategy: str = "aggressive",
    escalation_factor: float = 0.0,
) -> CombatResult:
    """Run combat and write back to campaign state."""
    arch = SLICE_ENCOUNTERS.get(encounter["archetype"], SLICE_ENCOUNTERS["reach_pirate"])

    abilities = []
    for ab in get_ship_abilities(state.crew):
        abilities.append(CombatAbility(
            id=ab["ability"], name=ab["ability"].replace("_", " ").title(),
            description=f"Crew: {ab['crew_name']}", action_cost=1, cooldown=2,
            effect_type="heal" if "repair" in ab["ability"] else "damage",
            effect_value=300 if "repair" in ab["ability"] else 400,
            crew_source=ab["crew_id"], degraded=ab["degraded"],
        ))

    player_ship = Combatant(
        id="player_ship", name="Star Freighter Nyx", team=Team.PLAYER, pos=Pos(1, 3),
        hp=state.ship_hull, hp_max=state.ship_hull_max,
        shield=state.ship_shield, shield_max=state.ship_shield_max,
        speed=state.ship_speed, evasion=0.1, armor=10,
        base_attack_damage=state.ship_weapon_power, base_attack_range=3, abilities=abilities,
    )
    enemy_ship = Combatant(
        id="enemy_1", name=arch.name, team=Team.ENEMY, pos=Pos(6, 3),
        hp=arch.ship_hull, hp_max=arch.ship_hull,
        shield=arch.ship_shield, shield_max=arch.ship_shield,
        speed=arch.ship_speed, evasion=0.15, armor=5,
        base_attack_damage=arch.ship_damage, base_attack_range=3,
    )

    cs = init_combat([player_ship], [enemy_ship], seed=state.seed + state.day)
    start_turn(cs)

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
                        action_move(cs, current.id, min(moves, key=lambda m: m.distance_to(Pos(6, 3))))
                if current.actions_remaining > 0:
                    targets = get_valid_targets(cs, current.id)
                    if targets:
                        action_attack(cs, current.id, targets[0])
                    else:
                        action_defend(cs, current.id)
        else:
            enemy_act(cs, current.id)
        end_turn(cs)

    result = resolve_combat(
        cs, encounter.get("civilization", ""), list(state.ship_cargo),
        escalation_factor=escalation_factor,
    )

    # Write back
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
                thread, "combat", "salvage_freighter_debris",
                [m.id for m in active_crew(state.crew)], state.cultural_knowledge, state.reputation,
            ):
                frags = get_medical_cargo_fragments()
                if source.fragment_id in frags:
                    frag = frags[source.fragment_id]
                    frag.day_acquired = state.day
                    discover_fragment(state.investigation, thread.id, frag)

    return result


def get_campaign_summary(state: CampaignState) -> dict:
    """Snapshot for testing and display."""
    return {
        "day": state.day, "credits": state.credits,
        "station": state.current_station, "fuel": state.ship_fuel,
        "hull": f"{state.ship_hull}/{state.ship_hull_max}",
        "cargo": list(state.ship_cargo),
        "crew": [m.name for m in active_crew(state.crew)],
        "crew_fit": len(fit_crew(state.crew)),
        "reputation": dict(state.reputation),
        "cultural_knowledge": dict(state.cultural_knowledge),
        "investigation_progress": state.investigation.total_progress,
        "consequence_tags": list(state.consequence_tags),
        "monthly_cost": calculate_crew_pay(state.crew),
    }
