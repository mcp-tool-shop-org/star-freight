"""Encounter engine — pirate encounter state machine.

Bridges voyage events to the combat system. A pirate encounter flows through
phases: approach -> naval -> boarding -> duel -> resolved.

At each phase, the player chooses an action:
  approach: negotiate / flee / fight
  naval:    broadside / close / evade / rake (per turn)
  duel:     thrust / slash / parry / shoot / throw / dodge / style (per turn)

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import Captain, OwnedShip

from portlight.content.factions import FACTIONS, get_captains_for_faction, get_faction_for_region
from portlight.engine.models import (
    EnemyShip,
    EncounterState,
    Ship,
)
from portlight.engine.naval import (
    attempt_flee,
    calc_boarding_threshold,
    generate_enemy_ship,
    get_valid_actions as get_naval_actions,
    pick_enemy_naval_action,
    resolve_boarding,
    resolve_naval_round,
)
from portlight.engine.combat import (
    CombatantState,
    CombatRound,
    apply_round_to_states,
    create_opponent_combatant,
    create_player_combatant,
    get_available_actions as get_combat_actions,
    resolve_combat_round,
)
from portlight.engine.underworld import get_faction_hostility


# ---------------------------------------------------------------------------
# Encounter creation
# ---------------------------------------------------------------------------

def create_encounter(
    world_ports: dict,
    voyage_destination_id: str,
    rng: random.Random,
) -> EncounterState | None:
    """Create a pirate encounter for the current voyage region.

    Returns None if no suitable faction/captain found.
    """
    dest_port = world_ports.get(voyage_destination_id)
    region = dest_port.region if dest_port else "Mediterranean"
    active_factions = get_faction_for_region(region)
    if not active_factions:
        active_factions = list(FACTIONS.values())[:1]

    faction = rng.choice(active_factions)
    faction_captains = get_captains_for_faction(faction.id)
    if not faction_captains:
        return None

    pirate_captain = rng.choice(faction_captains)
    enemy_ship = generate_enemy_ship(pirate_captain.name, pirate_captain.strength, rng)

    return EncounterState(
        enemy_captain_id=pirate_captain.id,
        enemy_captain_name=pirate_captain.name,
        enemy_faction_id=faction.id,
        enemy_personality=pirate_captain.personality,
        enemy_strength=pirate_captain.strength,
        enemy_region=region,
        enemy_ship_hull=enemy_ship.hull,
        enemy_ship_hull_max=enemy_ship.hull_max,
        enemy_ship_cannons=enemy_ship.cannons,
        enemy_ship_maneuver=enemy_ship.maneuver,
        enemy_ship_speed=enemy_ship.speed,
        enemy_ship_crew=enemy_ship.crew,
        enemy_ship_crew_max=enemy_ship.crew_max,
        phase="approach",
        boarding_progress=0,
        boarding_threshold=3,  # will be recalculated on fight
    )


# ---------------------------------------------------------------------------
# Approach phase
# ---------------------------------------------------------------------------

def resolve_negotiate(
    encounter: EncounterState,
    underworld_standing: dict[str, int],
    captain_type: str,
    rng: random.Random,
) -> tuple[bool, str]:
    """Attempt to negotiate with the pirate captain.

    Returns (success, message).
    """
    hostility = get_faction_hostility(
        underworld_standing, encounter.enemy_faction_id, captain_type,
    )

    if hostility == "allied":
        encounter.phase = "resolved"
        return True, f"{encounter.enemy_captain_name} recognizes you as an ally. Safe passage granted."
    elif hostility == "trade":
        encounter.phase = "resolved"
        return True, f"{encounter.enemy_captain_name} agrees to let you pass. Professional courtesy."
    elif hostility == "neutral":
        if rng.random() < 0.50:
            encounter.phase = "resolved"
            return True, f"{encounter.enemy_captain_name} considers, then waves you through. This time."
        else:
            return False, f"{encounter.enemy_captain_name} isn't interested in talking. Prepare to fight!"
    else:
        return False, f"{encounter.enemy_captain_name} sees prey, not a diplomat. Steel it is."


def resolve_flee(
    encounter: EncounterState,
    player_ship: Ship,
    rng: random.Random,
) -> tuple[bool, int, str]:
    """Attempt to flee from the encounter.

    Returns (escaped, hull_damage, message).
    """
    enemy_ship = _encounter_to_enemy_ship(encounter)
    escaped, damage = attempt_flee(player_ship, enemy_ship, rng)

    if escaped:
        encounter.phase = "resolved"
        msg = "You break away!"
        if damage > 0:
            msg += f" A parting shot catches your hull for {damage} damage."
        return True, damage, msg
    else:
        msg = f"Can't outrun them! {encounter.enemy_captain_name}'s ship closes in. "
        msg += f"Their broadside rakes you for {damage} hull damage. Battle is joined!"
        return False, damage, msg


def begin_fight(
    encounter: EncounterState,
    player_ship: Ship,
) -> str:
    """Transition encounter to naval combat phase."""
    encounter.phase = "naval"
    encounter.boarding_threshold = calc_boarding_threshold(
        player_ship.maneuver, encounter.enemy_ship_maneuver,
    )
    return f"Battle stations! {encounter.enemy_captain_name} engages! " \
           f"Boarding threshold: {encounter.boarding_threshold} close actions."


# ---------------------------------------------------------------------------
# Naval phase
# ---------------------------------------------------------------------------

def resolve_naval_turn(
    encounter: EncounterState,
    player_action: str,
    player_ship: Ship,
    rng: random.Random,
) -> dict:
    """Resolve one turn of naval combat within the encounter.

    Returns a dict with: hull_deltas, crew_deltas, boarding_progress,
    enemy_sunk, boarding_triggered, flavor.
    """
    enemy_ship = _encounter_to_enemy_ship(encounter)

    enemy_action = pick_enemy_naval_action(
        encounter.enemy_personality,
        enemy_ship, player_ship,
        encounter.boarding_progress, encounter.boarding_threshold,
        rng,
    )

    result = resolve_naval_round(
        player_action, enemy_action,
        player_ship, enemy_ship,
        encounter.boarding_progress, rng,
    )

    # Apply to encounter state
    encounter.enemy_ship_hull = max(0, encounter.enemy_ship_hull + result.enemy_hull_delta)
    encounter.enemy_ship_crew = max(0, encounter.enemy_ship_crew + result.enemy_crew_delta)
    encounter.boarding_progress = result.boarding_progress
    encounter.naval_turns += 1

    # Check transitions
    enemy_sunk = encounter.enemy_ship_hull <= 0
    boarding_triggered = encounter.boarding_progress >= encounter.boarding_threshold

    if enemy_sunk:
        encounter.phase = "resolved"
    elif boarding_triggered:
        encounter.phase = "boarding"

    return {
        "turn": encounter.naval_turns,
        "player_action": player_action,
        "enemy_action": enemy_action,
        "player_hull_delta": result.player_hull_delta,
        "enemy_hull_delta": result.enemy_hull_delta,
        "player_crew_delta": result.player_crew_delta,
        "enemy_crew_delta": result.enemy_crew_delta,
        "boarding_progress": encounter.boarding_progress,
        "boarding_threshold": encounter.boarding_threshold,
        "enemy_sunk": enemy_sunk,
        "boarding_triggered": boarding_triggered,
        "flavor": result.flavor,
    }


# ---------------------------------------------------------------------------
# Boarding phase
# ---------------------------------------------------------------------------

def resolve_boarding_phase(
    encounter: EncounterState,
    player_crew: int,
    rng: random.Random,
) -> dict:
    """Resolve boarding melee. Returns crew losses and transitions to duel phase."""
    p_lost, e_lost, player_advantage = resolve_boarding(
        player_crew, encounter.enemy_ship_crew, rng,
    )
    encounter.enemy_ship_crew = max(0, encounter.enemy_ship_crew - e_lost)
    encounter.phase = "duel"

    return {
        "player_crew_lost": p_lost,
        "enemy_crew_lost": e_lost,
        "player_advantage": player_advantage,
        "flavor": (
            "Grappling hooks fly! Your crew boards the enemy vessel. "
            f"You lose {p_lost} crew, they lose {e_lost}. "
            f"{'You have the advantage!' if player_advantage else 'They outnumber you on deck!'} "
            f"Now face {encounter.enemy_captain_name} blade to blade."
        ),
    }


# ---------------------------------------------------------------------------
# Duel phase (delegates to combat engine)
# ---------------------------------------------------------------------------

def create_duel_combatants(
    encounter: EncounterState,
    player_crew: int,
    player_style: str | None,
    player_injury_ids: list[str],
    player_firearm: str | None,
    player_ammo: int,
    player_throwing: int,
    player_mechanical: str | None = None,
    player_mechanical_ammo: int = 0,
) -> tuple[CombatantState, CombatantState]:
    """Create combatant states for the personal duel phase."""
    p = create_player_combatant(
        crew=player_crew,
        active_style=player_style,
        injury_ids=player_injury_ids,
        firearm_id=player_firearm,
        firearm_ammo=player_ammo,
        throwing_weapons=player_throwing,
        mechanical_weapon_id=player_mechanical,
        mechanical_ammo=player_mechanical_ammo,
    )

    # Opponent gets some ranged weapons based on strength
    opp_ammo = min(2, encounter.enemy_strength // 4)
    opp_throwing = min(3, encounter.enemy_strength // 3)

    o = create_opponent_combatant(
        strength=encounter.enemy_strength,
        personality=encounter.enemy_personality,
        ammo=opp_ammo,
        throwing_weapons=opp_throwing,
    )

    return p, o


def resolve_duel_turn(
    encounter: EncounterState,
    player_action: str,
    player_state: CombatantState,
    opponent_state: CombatantState,
    rng: random.Random,
) -> CombatRound:
    """Resolve one turn of personal combat within the encounter."""
    encounter.duel_turns += 1

    result = resolve_combat_round(
        player_action, player_state, opponent_state,
        encounter.enemy_personality, rng,
    )
    result.turn = encounter.duel_turns

    apply_round_to_states(result, player_state, opponent_state)

    # Check if fight is over
    if player_state.hp <= 0 or opponent_state.hp <= 0:
        encounter.phase = "resolved"

    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _encounter_to_enemy_ship(encounter: EncounterState) -> EnemyShip:
    return EnemyShip(
        name=f"{encounter.enemy_captain_name}'s Ship",
        hull=encounter.enemy_ship_hull,
        hull_max=encounter.enemy_ship_hull_max,
        cannons=encounter.enemy_ship_cannons,
        maneuver=encounter.enemy_ship_maneuver,
        speed=encounter.enemy_ship_speed,
        crew=encounter.enemy_ship_crew,
        crew_max=encounter.enemy_ship_crew_max,
    )


def get_encounter_naval_actions(player_cannons: int) -> tuple[str, ...]:
    """Get valid naval actions for the player's ship."""
    return get_naval_actions(player_cannons)


def get_encounter_combat_actions(player_state: CombatantState) -> list[str]:
    """Get valid combat actions for the player."""
    return get_combat_actions(player_state)


# ---------------------------------------------------------------------------
# Ship capture (prize-taking)
# ---------------------------------------------------------------------------

# Maps enemy strength to a ship template for prizes
_PRIZE_TEMPLATE_MAP: list[tuple[range, str]] = [
    (range(1, 4), "coastal_sloop"),
    (range(4, 6), "swift_cutter"),
    (range(6, 8), "trade_brigantine"),
    (range(8, 10), "merchant_galleon"),
    (range(10, 11), "merchant_galleon"),
]


def prize_template_id(strength: int) -> str:
    """Map enemy strength to a ship template for prize capture."""
    for r, tid in _PRIZE_TEMPLATE_MAP:
        if strength in r:
            return tid
    return "coastal_sloop"


def can_capture_prize(
    captain: "Captain",
    encounter: EncounterState,
    fleet_size_limit: int,
) -> tuple[bool, str]:
    """Check if the player can capture the enemy ship as a prize.

    Requirements:
    - Encounter must be resolved (enemy sunk or duel won)
    - Fleet must have space
    - Captain must have enough crew to man both ships
    """

    fleet_count = len(captain.fleet) + 1  # +1 for flagship
    if fleet_count >= fleet_size_limit:
        return False, "Fleet is full"

    # Need at least crew_min on both ships
    from portlight.content.ships import SHIPS
    current_template = SHIPS.get(captain.ship.template_id)
    prize_tid = prize_template_id(encounter.enemy_strength)
    prize_template = SHIPS.get(prize_tid)

    current_min = current_template.crew_min if current_template else 3
    prize_min = prize_template.crew_min if prize_template else 3

    if captain.ship.crew < current_min + prize_min:
        return False, f"Need at least {current_min + prize_min} crew to man both ships (have {captain.ship.crew})"

    return True, ""


def capture_prize(
    captain: "Captain",
    encounter: EncounterState,
    crew_to_prize: int,
) -> "OwnedShip":
    """Create an OwnedShip from the defeated enemy.

    Splits crew between flagship and prize. Prize starts with no upgrades.
    Returns the new OwnedShip (caller adds to fleet).
    """
    from portlight.content.ships import SHIPS
    from portlight.engine.models import OwnedShip

    prize_tid = prize_template_id(encounter.enemy_strength)
    prize_template = SHIPS.get(prize_tid)

    # Create prize ship with combat-end hull
    hull_remaining = max(1, encounter.enemy_ship_hull)
    hull_max = prize_template.hull_max if prize_template else encounter.enemy_ship_hull_max

    prize_ship = Ship(
        template_id=prize_tid,
        name=f"{encounter.enemy_captain_name}'s Prize",
        hull=min(hull_remaining, hull_max),
        hull_max=hull_max,
        cargo_capacity=prize_template.cargo_capacity if prize_template else 30,
        speed=prize_template.speed if prize_template else 6.0,
        crew=crew_to_prize,
        crew_max=prize_template.crew_max if prize_template else 8,
        cannons=prize_template.cannons if prize_template else 0,
        maneuver=prize_template.maneuver if prize_template else 0.5,
    )

    # Split crew
    captain.ship.crew -= crew_to_prize

    return OwnedShip(
        ship=prize_ship,
        docked_port_id="",  # Will be set when arriving at port
    )
