"""Naval combat engine — ship-to-ship engagement in the Age of Exploration.

Turn-based ship combat with four actions:
  BROADSIDE — fire cannons (damage = cannons * 1-3, reduced by maneuver)
  CLOSE     — advance boarding counter (takes fire if opponent shoots)
  EVADE     — reduce incoming damage by 50%, no progress
  RAKE      — target crew (lower hull damage, kills sailors)

Ships with 0 cannons (sloops) can only CLOSE or EVADE — historically
accurate for small craft that fought by boarding alongside.

Boarding triggers when the boarding counter reaches a threshold based
on ship sizes and maneuver ratings. After boarding, combat transitions
to the personal duel system.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import math
import random

from portlight.engine.models import (
    EnemyShip,
    NavalRound,
    Ship,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NAVAL_ACTIONS = ("broadside", "close", "evade", "rake")
BOARDING_BASE_THRESHOLD = 3


# ---------------------------------------------------------------------------
# Enemy ship generation
# ---------------------------------------------------------------------------

def generate_enemy_ship(
    captain_name: str,
    strength: int,
    rng: random.Random,
) -> EnemyShip:
    """Generate a pirate ship based on captain strength.

    Strength 1-3: sloop-class (fast, fragile, no cannons)
    Strength 4-6: cutter/brigantine (moderate)
    Strength 7-8: brigantine/galleon (dangerous)
    Strength 9-10: galleon (fortress)
    """
    if strength <= 3:
        hull = 40 + strength * 8
        cannons = 0
        maneuver = 0.85
        speed = 7.0 + rng.random()
        crew = 4 + strength
        crew_max = crew + 3
    elif strength <= 6:
        hull = 60 + strength * 10
        cannons = 2 + (strength - 3) * 2  # 2, 4, 6
        maneuver = 0.6 + (6 - strength) * 0.05
        speed = 6.0 + rng.random() * 0.5
        crew = 8 + (strength - 3) * 4
        crew_max = crew + 5
    elif strength <= 8:
        hull = 90 + strength * 10
        cannons = 6 + (strength - 6) * 3  # 9, 12
        maneuver = 0.4 + (8 - strength) * 0.05
        speed = 5.0 + rng.random() * 0.5
        crew = 18 + (strength - 6) * 5
        crew_max = crew + 8
    else:
        hull = 130 + strength * 8
        cannons = 12 + (strength - 8) * 4  # 16, 20
        maneuver = 0.25
        speed = 4.0 + rng.random() * 0.5
        crew = 30 + (strength - 8) * 8
        crew_max = crew + 10

    return EnemyShip(
        name=f"{captain_name}'s Ship",
        hull=hull,
        hull_max=hull,
        cannons=cannons,
        maneuver=maneuver,
        speed=speed,
        crew=crew,
        crew_max=crew_max,
    )


# ---------------------------------------------------------------------------
# Flee attempt
# ---------------------------------------------------------------------------

def attempt_flee(
    player_ship: Ship,
    enemy_ship: EnemyShip,
    rng: random.Random,
) -> tuple[bool, int]:
    """Attempt to flee from naval engagement.

    Returns (escaped, hull_damage_taken).
    Faster/nimbler ships escape more easily. Failed flee = free broadside.
    """
    escape_chance = (
        0.3
        + (player_ship.speed - enemy_ship.speed) * 0.1
        + player_ship.maneuver * 0.2
    )
    escape_chance = max(0.1, min(0.95, escape_chance))

    if rng.random() < escape_chance:
        # Escaped — grazing shot as you pull away
        graze = rng.randint(1, 3) if enemy_ship.cannons > 0 else 0
        return True, graze

    # Failed — enemy gets a free broadside
    if enemy_ship.cannons > 0:
        damage = enemy_ship.cannons * rng.randint(1, 2)
        damage = max(1, int(damage * (1 - player_ship.maneuver * 0.3)))
    else:
        damage = rng.randint(2, 5)  # ramming/grappling damage
    return False, damage


# ---------------------------------------------------------------------------
# Action validation
# ---------------------------------------------------------------------------

def get_valid_actions(cannons: int) -> tuple[str, ...]:
    """Return valid naval actions for a ship. Ships with 0 cannons can't fire.

    Flee is always available — any ship can attempt to disengage.
    """
    if cannons <= 0:
        return ("close", "evade", "flee")
    return (*NAVAL_ACTIONS, "flee")


# ---------------------------------------------------------------------------
# Boarding threshold
# ---------------------------------------------------------------------------

def calc_boarding_threshold(player_maneuver: float, enemy_maneuver: float) -> int:
    """How many CLOSE actions needed to board.

    Nimbler ships close faster. Base 3, reduced by attacker's maneuver.
    """
    threshold = BOARDING_BASE_THRESHOLD - math.floor(player_maneuver * 2)
    return max(1, threshold)


# ---------------------------------------------------------------------------
# Enemy AI
# ---------------------------------------------------------------------------

_NAVAL_AI_WEIGHTS: dict[str, dict[str, float]] = {
    "aggressive": {"broadside": 0.45, "close": 0.35, "evade": 0.05, "rake": 0.15},
    "defensive":  {"broadside": 0.20, "close": 0.10, "evade": 0.40, "rake": 0.30},
    "balanced":   {"broadside": 0.35, "close": 0.25, "evade": 0.20, "rake": 0.20},
    "wild":       {"broadside": 0.30, "close": 0.25, "evade": 0.20, "rake": 0.25},
}


def pick_enemy_naval_action(
    personality: str,
    enemy_ship: EnemyShip,
    player_ship: Ship,
    boarding_progress: int,
    boarding_threshold: int,
    rng: random.Random,
) -> str:
    """Pick enemy naval action based on personality and tactical situation."""
    weights = dict(_NAVAL_AI_WEIGHTS.get(personality, _NAVAL_AI_WEIGHTS["balanced"]))

    # Can't fire without cannons
    if enemy_ship.cannons <= 0:
        weights["broadside"] = 0.0
        weights["rake"] = 0.0
        weights["close"] += 0.5
        weights["evade"] += 0.2

    # Balanced adapts: go aggressive if winning on hull, defensive if losing
    if personality == "balanced":
        hull_ratio = enemy_ship.hull / max(1, enemy_ship.hull_max)
        player_hull_ratio = player_ship.hull / max(1, player_ship.hull_max)
        if hull_ratio > player_hull_ratio + 0.2:
            weights["broadside"] += 0.15
            weights["close"] += 0.10
        elif hull_ratio < player_hull_ratio - 0.2:
            weights["evade"] += 0.15
            weights["rake"] += 0.10

    # If close to boarding, push it
    if boarding_progress >= boarding_threshold - 1:
        weights["close"] += 0.30

    actions = list(weights.keys())
    w = [max(0.0, weights[a]) for a in actions]
    total = sum(w)
    if total <= 0:
        return "evade"
    return rng.choices(actions, weights=w, k=1)[0]


# ---------------------------------------------------------------------------
# Round resolution
# ---------------------------------------------------------------------------

_NAVAL_FLAVOR = {
    ("broadside", "broadside"): "Cannons roar from both ships — smoke and splinters fill the air.",
    ("broadside", "close"):     "Your broadside catches them closing. Wood splinters fly as they press forward.",
    ("broadside", "evade"):     "They weave hard but your guns still find timber.",
    ("broadside", "rake"):      "Both ships fire — your broadside hammers their hull while their high shot sweeps your deck.",
    ("close", "broadside"):     "You press forward through their broadside. Iron and wood fly past your bow.",
    ("close", "close"):         "Both ships close, hulls nearly touching. Grappling hooks ready.",
    ("close", "evade"):         "You lunge forward but they slip aside. The gap holds.",
    ("close", "rake"):          "You close through a hail of grapeshot aimed at your crew.",
    ("evade", "broadside"):     "You turn hard. Their broadside catches only wake and spray.",
    ("evade", "close"):         "They try to close but your evasion keeps them at arm's length.",
    ("evade", "evade"):         "Both ships circle warily. Neither commits.",
    ("evade", "rake"):          "You evade but their high shot still peppers the rigging.",
    ("rake", "broadside"):      "Your grapeshot rakes their deck as their broadside finds your hull.",
    ("rake", "close"):          "Your crew-killing shot catches them as they close.",
    ("rake", "evade"):          "They evade but your grapeshot still finds a few sailors.",
    ("rake", "rake"):           "Both ships fire high — crew on both sides fall to grapeshot.",
}


def resolve_naval_round(
    player_action: str,
    enemy_action: str,
    player_ship: Ship,
    enemy_ship: EnemyShip,
    boarding_progress: int,
    rng: random.Random,
) -> NavalRound:
    """Resolve one turn of naval combat. Returns NavalRound with deltas."""
    p_hull_delta = 0
    e_hull_delta = 0
    p_crew_delta = 0
    e_crew_delta = 0
    new_boarding = boarding_progress

    # --- Player damage to enemy ---
    if player_action == "broadside" and player_ship.cannons > 0:
        base = player_ship.cannons * rng.randint(1, 3)
        reduced = max(1, int(base * (1 - enemy_ship.maneuver * 0.3)))
        if enemy_action == "evade":
            reduced = max(0, reduced // 2)  # evade can fully dodge a weak broadside
        e_hull_delta -= reduced

    elif player_action == "rake" and player_ship.cannons > 0:
        hull_dmg = player_ship.cannons * rng.randint(0, 1)
        if enemy_action == "evade":
            hull_dmg = max(0, hull_dmg // 2)
        e_hull_delta -= hull_dmg
        crew_kill = rng.randint(1, max(1, player_ship.cannons // 3 + 1))
        if enemy_action == "evade":
            crew_kill = max(0, crew_kill // 2)
        e_crew_delta -= crew_kill

    elif player_action == "close":
        if enemy_action != "evade":
            new_boarding += 1

    # player_action == "evade" -> no offensive effect

    # --- Enemy damage to player ---
    if enemy_action == "broadside" and enemy_ship.cannons > 0:
        base = enemy_ship.cannons * rng.randint(1, 3)
        reduced = max(1, int(base * (1 - player_ship.maneuver * 0.3)))
        if player_action == "evade":
            reduced = max(0, reduced // 2)  # evade can fully dodge a weak broadside
        p_hull_delta -= reduced

    elif enemy_action == "rake" and enemy_ship.cannons > 0:
        hull_dmg = enemy_ship.cannons * rng.randint(0, 1)
        if player_action == "evade":
            hull_dmg = max(0, hull_dmg // 2)
        p_hull_delta -= hull_dmg
        crew_kill = rng.randint(1, max(1, enemy_ship.cannons // 3 + 1))
        if player_action == "evade":
            crew_kill = max(0, crew_kill // 2)
        p_crew_delta -= crew_kill

    elif enemy_action == "close":
        if player_action != "evade":
            new_boarding += 1

    flavor = _NAVAL_FLAVOR.get(
        (player_action, enemy_action),
        "The ships maneuver across the waves.",
    )

    return NavalRound(
        turn=0,  # caller sets this
        player_action=player_action,
        enemy_action=enemy_action,
        player_hull_delta=p_hull_delta,
        enemy_hull_delta=e_hull_delta,
        player_crew_delta=p_crew_delta,
        enemy_crew_delta=e_crew_delta,
        boarding_progress=new_boarding,
        flavor=flavor,
    )


# ---------------------------------------------------------------------------
# Boarding resolution
# ---------------------------------------------------------------------------

def resolve_boarding(
    player_crew: int,
    enemy_crew: int,
    rng: random.Random,
) -> tuple[int, int, bool]:
    """Resolve boarding melee. Returns (player_crew_lost, enemy_crew_lost, player_advantage).

    Crew advantage determines how brutal the boarding is:
      >2:1 — swift capture, minimal losses
      1.5-2:1 — boarding fight, moderate losses
      ~1:1 — brutal, heavy losses both sides
      <1:1.5 — player disadvantaged, extra losses
    """
    ratio = player_crew / max(1, enemy_crew)

    if ratio > 2.0:
        p_lost = rng.randint(0, 1)
        e_lost = rng.randint(2, 4)
    elif ratio > 1.5:
        p_lost = rng.randint(1, 3)
        e_lost = rng.randint(2, 4)
    elif ratio > 0.67:
        p_lost = rng.randint(2, 5)
        e_lost = rng.randint(2, 5)
    else:
        p_lost = rng.randint(3, 6)
        e_lost = rng.randint(1, 3)

    # Cap losses at actual crew count
    p_lost = min(p_lost, max(0, player_crew - 1))  # always keep at least 1
    e_lost = min(e_lost, enemy_crew)

    player_advantage = player_crew - p_lost > enemy_crew - e_lost
    return p_lost, e_lost, player_advantage
