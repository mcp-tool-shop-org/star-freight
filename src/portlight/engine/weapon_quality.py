"""Weapon quality engine — degradation, maintenance, and smith upgrades.

Five quality tiers from rusted junk to masterwork legend:
  rusted     — corroded, damaged. -1 damage, -0.10 accuracy. Can't degrade further.
  worn       — battle-scarred, reliable enough. -0.05 accuracy.
  standard   — fresh from purchase. Baseline stats.
  fine       — crafted with care. +1 damage, +0.05 accuracy.
  masterwork — legendary craftsmanship. +2 damage, +0.10 accuracy.

Weapons degrade with use:
  - Melee: every 10 combats, drop one tier
  - Firearms: every 20 shots, drop one tier
  - Armor: every 15 combats, drop one tier
  - Rusted weapons can't degrade further

Maintenance at any port with a shipyard prevents degradation.
Master smiths at select ports can upgrade quality one tier (expensive, takes days).

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Quality tiers
# ---------------------------------------------------------------------------

QUALITY_TIERS = ("rusted", "worn", "standard", "fine", "masterwork")

# Index for ordering (higher = better)
_QUALITY_INDEX = {q: i for i, q in enumerate(QUALITY_TIERS)}


@dataclass(frozen=True)
class QualityEffects:
    """Combat modifiers for a quality tier."""
    damage_mod: int
    accuracy_mod: float
    label: str           # display name
    color: str           # Rich markup color


QUALITY_EFFECTS: dict[str, QualityEffects] = {
    "rusted":     QualityEffects(damage_mod=-1, accuracy_mod=-0.10, label="Rusted",     color="red"),
    "worn":       QualityEffects(damage_mod=0,  accuracy_mod=-0.05, label="Worn",       color="yellow"),
    "standard":   QualityEffects(damage_mod=0,  accuracy_mod=0.0,   label="Standard",   color="white"),
    "fine":       QualityEffects(damage_mod=1,  accuracy_mod=0.05,  label="Fine",       color="green"),
    "masterwork": QualityEffects(damage_mod=2,  accuracy_mod=0.10,  label="Masterwork", color="bold cyan"),
}


def get_quality_effects(quality: str) -> QualityEffects:
    """Get combat modifiers for a quality tier."""
    return QUALITY_EFFECTS.get(quality, QUALITY_EFFECTS["standard"])


# ---------------------------------------------------------------------------
# Degradation thresholds
# ---------------------------------------------------------------------------

MELEE_DEGRADE_USES = 10      # combats before melee drops a tier
FIREARM_DEGRADE_USES = 20    # shots before firearm drops a tier
ARMOR_DEGRADE_USES = 15      # combats before armor drops a tier
MECHANICAL_DEGRADE_USES = 25 # shots before mechanical drops a tier


def degrade_quality(current: str) -> str:
    """Drop quality one tier. Rusted can't go lower."""
    idx = _QUALITY_INDEX.get(current, 2)
    if idx <= 0:
        return "rusted"
    return QUALITY_TIERS[idx - 1]


def check_degradation(
    weapon_id: str,
    weapon_type: str,
    usage: int,
    threshold_bonus: int = 0,
) -> bool:
    """Check if a weapon should degrade based on usage count.

    weapon_type: 'melee', 'firearm', 'mechanical', 'armor'
    threshold_bonus: extra uses from blacksmith skill (0 = no bonus)
    """
    threshold = {
        "melee": MELEE_DEGRADE_USES,
        "firearm": FIREARM_DEGRADE_USES,
        "mechanical": MECHANICAL_DEGRADE_USES,
        "armor": ARMOR_DEGRADE_USES,
    }.get(weapon_type, MELEE_DEGRADE_USES)

    return usage >= threshold + threshold_bonus


def tick_weapon_degradation(
    weapon_quality: dict[str, str],
    weapon_usage: dict[str, int],
    weapon_id: str,
    weapon_type: str,
    uses: int = 1,
    threshold_bonus: int = 0,
) -> tuple[bool, str | None]:
    """Record weapon use and check for degradation.

    Returns (degraded, new_quality_or_None).
    threshold_bonus: extra uses from blacksmith skill (slows degradation).
    Mutates weapon_usage in place. Mutates weapon_quality if degradation occurs.
    """
    current_uses = weapon_usage.get(weapon_id, 0) + uses
    weapon_usage[weapon_id] = current_uses

    current_quality = weapon_quality.get(weapon_id, "standard")
    if current_quality == "rusted":
        return False, None  # can't go lower

    if check_degradation(weapon_id, weapon_type, current_uses, threshold_bonus):
        new_quality = degrade_quality(current_quality)
        weapon_quality[weapon_id] = new_quality
        weapon_usage[weapon_id] = 0  # reset counter after degradation
        return True, new_quality

    return False, None


# ---------------------------------------------------------------------------
# Maintenance
# ---------------------------------------------------------------------------

# Cost to maintain (per quality tier — higher quality costs more to maintain)
MAINTENANCE_COST = {
    "rusted": 5,        # cheap cleanup
    "worn": 10,
    "standard": 15,
    "fine": 25,
    "masterwork": 40,
}


def get_maintenance_cost(weapon_id: str, weapon_quality: dict[str, str]) -> int:
    """Get silver cost to maintain a weapon (reset usage counter)."""
    quality = weapon_quality.get(weapon_id, "standard")
    return MAINTENANCE_COST.get(quality, 15)


def maintain_weapon(
    weapon_id: str,
    weapon_quality: dict[str, str],
    weapon_usage: dict[str, int],
    silver: int,
) -> tuple[int, str | None]:
    """Maintain a weapon — reset usage counter. Returns (remaining_silver, error).

    Maintenance prevents degradation but doesn't improve quality.
    """
    cost = get_maintenance_cost(weapon_id, weapon_quality)
    if silver < cost:
        return silver, f"Maintenance costs {cost} silver. You have {silver}."

    weapon_usage[weapon_id] = 0
    return silver - cost, None


# ---------------------------------------------------------------------------
# Smith upgrades
# ---------------------------------------------------------------------------

# Cost to upgrade one tier (escalating)
UPGRADE_COST = {
    "rusted": 20,       # rusted -> worn
    "worn": 40,         # worn -> standard
    "standard": 100,    # standard -> fine
    "fine": 300,        # fine -> masterwork
}

UPGRADE_DAYS = {
    "rusted": 1,
    "worn": 2,
    "standard": 3,
    "fine": 5,
}


def can_upgrade(
    weapon_id: str,
    weapon_quality: dict[str, str],
    silver: int,
    at_smith: bool = True,
) -> str | None:
    """Check if a weapon can be upgraded. Returns error message or None."""
    if not at_smith:
        return "No smith at this port. Visit a port with a shipyard."

    quality = weapon_quality.get(weapon_id, "standard")
    if quality == "masterwork":
        return "Already masterwork quality. This weapon cannot be improved further."

    cost = UPGRADE_COST.get(quality, 100)
    if silver < cost:
        return f"Upgrade costs {cost} silver. You have {silver}."

    return None


def upgrade_weapon(
    weapon_id: str,
    weapon_quality: dict[str, str],
    weapon_usage: dict[str, int],
    silver: int,
) -> tuple[str, int, int]:
    """Upgrade a weapon one quality tier.

    Returns (new_quality, remaining_silver, training_days).
    Also resets usage counter.
    """
    current = weapon_quality.get(weapon_id, "standard")
    cost = UPGRADE_COST.get(current, 100)
    days = UPGRADE_DAYS.get(current, 3)

    idx = _QUALITY_INDEX.get(current, 2)
    new_quality = QUALITY_TIERS[min(idx + 1, len(QUALITY_TIERS) - 1)]

    weapon_quality[weapon_id] = new_quality
    weapon_usage[weapon_id] = 0  # fresh after upgrade
    return new_quality, silver - cost, days


# ---------------------------------------------------------------------------
# Quality assignment helpers (for loot, purchases, etc.)
# ---------------------------------------------------------------------------

def assign_purchase_quality() -> str:
    """New purchases are always standard quality."""
    return "standard"


def assign_loot_quality(
    opponent_strength: int,
    rng: "random.Random",
) -> str:
    """Determine quality of a looted weapon based on opponent strength.

    Weak opponents: mostly rusted/worn
    Strong opponents: standard/fine possible
    Boss-tier: fine/masterwork possible
    """
    roll = rng.random()

    if opponent_strength <= 3:
        if roll < 0.40:
            return "rusted"
        elif roll < 0.80:
            return "worn"
        else:
            return "standard"
    elif opponent_strength <= 6:
        if roll < 0.15:
            return "rusted"
        elif roll < 0.50:
            return "worn"
        elif roll < 0.90:
            return "standard"
        else:
            return "fine"
    elif opponent_strength <= 8:
        if roll < 0.10:
            return "worn"
        elif roll < 0.50:
            return "standard"
        elif roll < 0.85:
            return "fine"
        else:
            return "masterwork"
    else:  # 9-10 (boss tier)
        if roll < 0.20:
            return "standard"
        elif roll < 0.60:
            return "fine"
        else:
            return "masterwork"


def get_quality_display(weapon_id: str, weapon_quality: dict[str, str]) -> str:
    """Get display string for a weapon's quality with Rich color markup."""
    quality = weapon_quality.get(weapon_id, "standard")
    effects = QUALITY_EFFECTS[quality]
    return f"[{effects.color}]{effects.label}[/{effects.color}]"


def get_weapon_summary(
    weapon_id: str,
    weapon_name: str,
    weapon_quality: dict[str, str],
    weapon_usage: dict[str, int],
    weapon_type: str = "melee",
) -> dict:
    """Get a summary dict for display. Includes quality, usage, degradation warning."""
    quality = weapon_quality.get(weapon_id, "standard")
    usage = weapon_usage.get(weapon_id, 0)
    effects = get_quality_effects(quality)

    threshold = {
        "melee": MELEE_DEGRADE_USES,
        "firearm": FIREARM_DEGRADE_USES,
        "mechanical": MECHANICAL_DEGRADE_USES,
        "armor": ARMOR_DEGRADE_USES,
    }.get(weapon_type, MELEE_DEGRADE_USES)

    uses_remaining = max(0, threshold - usage)
    near_degradation = uses_remaining <= 3 and quality != "rusted"

    return {
        "weapon_id": weapon_id,
        "name": weapon_name,
        "quality": quality,
        "quality_label": effects.label,
        "quality_color": effects.color,
        "damage_mod": effects.damage_mod,
        "accuracy_mod": effects.accuracy_mod,
        "usage": usage,
        "uses_until_degrade": uses_remaining,
        "near_degradation": near_degradation,
    }
