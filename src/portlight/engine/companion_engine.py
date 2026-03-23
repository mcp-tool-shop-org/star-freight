"""Companion engine — recruitment, morale, departure, and combat bonuses.

Companions are NPCs who travel with the player, provide role-based bonuses,
react to decisions via morale, and can leave if pushed too far.

Max 2 active companions. Each has morale (0-100) that shifts with events.
Departure triggers at morale <= 10.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from portlight.content.companions import (
    COMPANIONS,
    MORALE_REACTIONS,
    PERSONALITY_MODIFIERS,
    ROLES,
)


# ---------------------------------------------------------------------------
# Companion state (stored on Captain)
# ---------------------------------------------------------------------------

@dataclass
class CompanionState:
    """Active companion traveling with the player."""
    companion_id: str
    role_id: str
    morale: int = 70               # 0-100, starts at 70
    joined_day: int = 0
    personality: str = "pragmatic"


@dataclass
class PartyState:
    """The player's companion party."""
    companions: list[CompanionState] = field(default_factory=list)
    max_size: int = 2
    # History
    departed: list[str] = field(default_factory=list)  # companion_ids that left


MAX_PARTY_SIZE = 2


# ---------------------------------------------------------------------------
# Recruitment
# ---------------------------------------------------------------------------

def can_recruit(
    party: PartyState,
    companion_id: str,
    player_silver: int,
    player_regional_standing: dict[str, int],
    current_port_id: str,
) -> str | None:
    """Check if a companion can be recruited. Returns error or None."""
    comp = COMPANIONS.get(companion_id)
    if comp is None:
        return f"Unknown companion: {companion_id}"

    if comp.home_port_id != current_port_id:
        return f"{comp.name} is not at this port."

    if any(c.companion_id == companion_id for c in party.companions):
        return f"{comp.name} is already in your party."

    if companion_id in party.departed:
        return f"{comp.name} already left your crew. They won't come back."

    if len(party.companions) >= party.max_size:
        return f"Party is full (max {party.max_size} companions)."

    if player_silver < comp.hire_cost:
        return f"{comp.name} costs {comp.hire_cost} silver to recruit. You have {player_silver}."

    standing = player_regional_standing.get(comp.region, 0)
    if standing < comp.required_standing:
        return f"Need {comp.required_standing} standing in {comp.region} to recruit {comp.name}. You have {standing}."

    return None


def recruit(
    party: PartyState,
    companion_id: str,
    current_day: int,
) -> CompanionState:
    """Add a companion to the party. Returns the new CompanionState."""
    comp = COMPANIONS[companion_id]
    state = CompanionState(
        companion_id=companion_id,
        role_id=comp.role_id,
        morale=70,
        joined_day=current_day,
        personality=comp.personality,
    )
    party.companions.append(state)
    return state


def dismiss(
    party: PartyState,
    companion_id: str,
) -> str | None:
    """Remove a companion from the party. Returns error or None."""
    idx = None
    for i, c in enumerate(party.companions):
        if c.companion_id == companion_id:
            idx = i
            break
    if idx is None:
        return f"No companion with id {companion_id} in party."
    party.companions.pop(idx)
    return None


# ---------------------------------------------------------------------------
# Morale
# ---------------------------------------------------------------------------

def apply_morale_trigger(
    party: PartyState,
    trigger: str,
) -> list[tuple[str, int, str]]:
    """Apply a morale trigger to all companions.

    Returns list of (companion_id, morale_delta, reaction_flavor).
    """
    reactions_row = MORALE_REACTIONS.get(trigger)
    if reactions_row is None:
        return []

    results: list[tuple[str, int, str]] = []

    for comp_state in party.companions:
        base_delta = reactions_row.get(comp_state.role_id, 0)
        if base_delta == 0:
            continue

        # Apply personality modifier
        pers_mods = PERSONALITY_MODIFIERS.get(comp_state.personality, {})
        pers_delta = pers_mods.get(trigger, 0)
        total_delta = base_delta + pers_delta

        if total_delta == 0:
            continue

        comp_def = COMPANIONS.get(comp_state.companion_id)
        name = comp_def.name if comp_def else comp_state.companion_id

        # Apply
        comp_state.morale = max(0, min(100, comp_state.morale + total_delta))

        # Generate flavor
        if total_delta > 0:
            flavor = f"{name} approves. (+{total_delta} morale)"
        else:
            flavor = f"{name} disapproves. ({total_delta} morale)"

        results.append((comp_state.companion_id, total_delta, flavor))

    return results


# ---------------------------------------------------------------------------
# Departure check
# ---------------------------------------------------------------------------

@dataclass
class DepartureEvent:
    """A companion leaving the party."""
    companion_id: str
    companion_name: str
    reason: str
    departure_line: str


def check_departures(party: PartyState) -> list[DepartureEvent]:
    """Check if any companions should depart due to low morale.

    Departure triggers at morale <= 10. Returns list of departure events.
    Removes departing companions from party.
    """
    departures: list[DepartureEvent] = []
    remaining: list[CompanionState] = []

    for comp_state in party.companions:
        if comp_state.morale <= 10:
            comp_def = COMPANIONS.get(comp_state.companion_id)
            name = comp_def.name if comp_def else comp_state.companion_id
            line = comp_def.departure_line if comp_def else "They leave without a word."
            departures.append(DepartureEvent(
                companion_id=comp_state.companion_id,
                companion_name=name,
                reason="Morale collapsed",
                departure_line=line,
            ))
            party.departed.append(comp_state.companion_id)
        else:
            remaining.append(comp_state)

    party.companions = remaining
    return departures


# ---------------------------------------------------------------------------
# Combat bonuses
# ---------------------------------------------------------------------------

def get_party_combat_bonus(party: PartyState) -> dict:
    """Get aggregated combat bonuses from all active companions."""
    bonus = {
        "damage_bonus": 0,
        "interception_chance": 0.0,
        "speed_bonus": 0.0,
        "danger_reduction": 0.0,
        "heal_rate_bonus": 0.0,
        "inspection_evasion": 0.0,
        "trade_bonus": 0.0,
    }

    for comp_state in party.companions:
        role = ROLES.get(comp_state.role_id)
        if role is None:
            continue
        # Scale bonuses by morale (below 30 = reduced effectiveness)
        morale_mult = 1.0 if comp_state.morale >= 30 else comp_state.morale / 30.0
        bonus["damage_bonus"] += int(role.combat_damage_bonus * morale_mult)
        bonus["interception_chance"] += role.combat_interception_chance * morale_mult
        bonus["speed_bonus"] += role.speed_bonus * morale_mult
        bonus["danger_reduction"] += role.danger_reduction * morale_mult
        bonus["heal_rate_bonus"] += role.heal_rate_bonus * morale_mult
        bonus["inspection_evasion"] += role.inspection_evasion * morale_mult
        bonus["trade_bonus"] += role.trade_bonus * morale_mult

    return bonus


def roll_interception(
    party: PartyState,
    damage: int,
    rng: random.Random,
) -> tuple[bool, str]:
    """Roll for a marine companion intercepting damage.

    Returns (intercepted, flavor_text). If intercepted, companion takes
    a morale hit but player avoids the damage.
    """
    for comp_state in party.companions:
        role = ROLES.get(comp_state.role_id)
        if role is None or role.combat_interception_chance <= 0:
            continue

        morale_mult = 1.0 if comp_state.morale >= 30 else comp_state.morale / 30.0
        chance = role.combat_interception_chance * morale_mult

        if rng.random() < chance:
            comp_def = COMPANIONS.get(comp_state.companion_id)
            name = comp_def.name if comp_def else "Your companion"
            comp_state.morale = max(0, comp_state.morale - 2)  # slight morale cost
            return True, f"{name} throws themselves in the way! They take the hit for you."

    return False, ""


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def get_party_summary(party: PartyState) -> list[dict]:
    """Get summary dicts for all companions."""
    results = []
    for cs in party.companions:
        comp_def = COMPANIONS.get(cs.companion_id)
        role = ROLES.get(cs.role_id)
        morale_status = "happy" if cs.morale >= 60 else "concerned" if cs.morale >= 30 else "unhappy" if cs.morale > 10 else "leaving"
        results.append({
            "id": cs.companion_id,
            "name": comp_def.name if comp_def else cs.companion_id,
            "role": role.name if role else cs.role_id,
            "morale": cs.morale,
            "morale_status": morale_status,
            "personality": cs.personality,
            "joined_day": cs.joined_day,
        })
    return results


def get_cohesion(party: PartyState) -> int:
    """Get party cohesion (average morale of active companions). 0 if empty."""
    if not party.companions:
        return 0
    return sum(c.morale for c in party.companions) // len(party.companions)
