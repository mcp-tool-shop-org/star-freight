"""Injury engine — trigger, heal, and effect application.

Injuries are sustained in personal combat when a single round deals
significant damage. They persist between combats, heal over time at port,
and can block fighting styles that require injured body parts.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random

from portlight.content.injuries import INJURIES, get_injury_pool
from portlight.engine.models import ActiveInjury


# ---------------------------------------------------------------------------
# Injury trigger
# ---------------------------------------------------------------------------

INJURY_DAMAGE_THRESHOLD = 4
INJURY_BASE_CHANCE = 0.15  # per point of damage above threshold


def roll_injury(
    damage: int,
    attack_type: str,
    rng: random.Random,
    injury_bonus: float = 0.0,
) -> str | None:
    """Roll for an injury after taking damage.

    Returns injury_id or None. Chance scales with damage above threshold.
    attack_type determines which injuries are possible.
    injury_bonus adds to the trigger chance (e.g. from Lua fighting style).
    """
    if damage < INJURY_DAMAGE_THRESHOLD:
        return None

    chance = (damage - INJURY_DAMAGE_THRESHOLD + 1) * INJURY_BASE_CHANCE + injury_bonus
    chance = min(0.90, chance)  # cap at 90%

    if rng.random() >= chance:
        return None

    pool = get_injury_pool(attack_type)
    if not pool:
        return None

    return rng.choice(pool).id


def create_injury(injury_id: str, current_day: int) -> ActiveInjury:
    """Create an ActiveInjury from an injury definition."""
    inj = INJURIES[injury_id]
    return ActiveInjury(
        injury_id=injury_id,
        acquired_day=current_day,
        heal_remaining=inj.heal_days,
        treated=False,
    )


# ---------------------------------------------------------------------------
# Healing
# ---------------------------------------------------------------------------

def heal_injury_tick(
    injuries: list[ActiveInjury],
    days: int = 1,
    in_port: bool = True,
    has_medicines: bool = False,
) -> list[ActiveInjury]:
    """Advance healing for all injuries. Returns updated injury list.

    Healing only progresses while in port. Medicines halve remaining time.
    Returns a new list with healed injuries removed.
    """
    if not in_port:
        return list(injuries)

    result: list[ActiveInjury] = []
    for injury in injuries:
        if injury.heal_remaining is None:
            # Permanent injury — never heals
            result.append(injury)
            continue

        heal_rate = days * 2 if has_medicines else days
        remaining = max(0, injury.heal_remaining - heal_rate)

        if remaining <= 0:
            continue  # healed — remove from list

        result.append(ActiveInjury(
            injury_id=injury.injury_id,
            acquired_day=injury.acquired_day,
            heal_remaining=remaining,
            treated=injury.treated or has_medicines,
        ))

    return result


def treat_injury(
    injury: ActiveInjury,
    silver: int,
) -> tuple[ActiveInjury | None, int, str | None]:
    """Pay for medical treatment at port.

    Returns (updated_injury_or_None, remaining_silver, error_or_None).
    Treatment halves remaining heal time and marks as treated.
    """
    inj_def = INJURIES.get(injury.injury_id)
    if inj_def is None:
        return injury, silver, f"Unknown injury: {injury.injury_id}"

    if injury.heal_remaining is None:
        return injury, silver, f"{inj_def.name} is permanent and cannot be treated."

    if injury.treated:
        return injury, silver, f"{inj_def.name} has already been treated."

    cost = inj_def.heal_silver
    if silver < cost:
        return injury, silver, f"Treatment costs {cost} silver. You have {silver}."

    new_remaining = max(1, injury.heal_remaining // 2)
    treated = ActiveInjury(
        injury_id=injury.injury_id,
        acquired_day=injury.acquired_day,
        heal_remaining=new_remaining,
        treated=True,
    )
    return treated, silver - cost, None


# ---------------------------------------------------------------------------
# Effect queries
# ---------------------------------------------------------------------------

def get_injury_effects(injury_ids: list[str]) -> dict:
    """Aggregate combat effects from all active injuries.

    Returns a dict with cumulative modifiers:
      melee_damage_mod, stamina_max_mod, hp_max_mod, ranged_accuracy_mod,
      can_dodge, can_use_firearms, thrust_multiplier
    """
    effects = {
        "melee_damage_mod": 0,
        "stamina_max_mod": 0,
        "hp_max_mod": 0,
        "ranged_accuracy_mod": 0.0,
        "can_dodge": True,
        "can_use_firearms": True,
        "thrust_multiplier": 1.0,
    }

    for iid in injury_ids:
        inj = INJURIES.get(iid)
        if inj is None:
            continue
        effects["melee_damage_mod"] += inj.melee_damage_mod
        effects["stamina_max_mod"] += inj.stamina_max_mod
        effects["hp_max_mod"] += inj.hp_max_mod
        effects["ranged_accuracy_mod"] += inj.ranged_accuracy_mod
        if not inj.can_dodge:
            effects["can_dodge"] = False
        if not inj.can_use_firearms:
            effects["can_use_firearms"] = False
        effects["thrust_multiplier"] *= inj.thrust_multiplier

    return effects


def check_injury_blocks_style(
    injury_ids: list[str],
    required_body_parts: tuple[str, ...] | list[str],
) -> bool:
    """Check if any active injury blocks a style that requires given body parts."""
    from portlight.content.injuries import get_injured_body_parts

    injured_parts = get_injured_body_parts(injury_ids)
    return bool(injured_parts & set(required_body_parts))
