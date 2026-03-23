"""Weapon provenance — items that remember their history.

Every weapon tracks its kills, its origin, and the captains it has faced.
Over time, weapons earn epithets and become recognized by pirates, granting
fear and respect bonuses in encounters.

Cherry-picked from ai-rpg-engine's equipment provenance + relic growth systems.

Relic growth tiers:
  unnamed    — fresh weapon, no history
  bloodied   — 3+ kills. "A blade that's tasted blood."
  reaper     — 10+ kills. "This weapon has a reputation."
  legendary  — 25+ kills. "Songs are sung about this blade."

Named weapons: defeating a named pirate captain brands the weapon.
  "Gnaw's Bane" — the sword that killed Gnaw.

Recognition: pirates who know of the weapon's history react to it.
  Fear bonus from legendary weapons. Respect from reaper-tier.

Pure functions — callers decide what to mutate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Provenance data
# ---------------------------------------------------------------------------

@dataclass
class WeaponProvenance:
    """History of a single weapon. Stored in CombatGear.weapon_provenance."""
    weapon_id: str
    acquired_port: str = ""
    acquired_day: int = 0
    acquired_region: str = ""
    # Kill tracking
    kills: int = 0
    named_kills: list[str] = field(default_factory=list)  # captain_ids defeated with this weapon
    # Naming
    epithet: str | None = None  # "Gnaw's Bane", "The Red Tide", etc.
    custom_name: str | None = None  # player-chosen name
    # Recognition
    times_recognized: int = 0
    # Computed (not stored — derived on read)


# ---------------------------------------------------------------------------
# Relic growth tiers
# ---------------------------------------------------------------------------

RELIC_TIERS = ("unnamed", "bloodied", "reaper", "legendary")

RELIC_THRESHOLDS = {
    "bloodied": 3,
    "reaper": 10,
    "legendary": 25,
}

RELIC_LABELS = {
    "unnamed": "",
    "bloodied": "Bloodied",
    "reaper": "Reaper",
    "legendary": "Legendary",
}

RELIC_COLORS = {
    "unnamed": "white",
    "bloodied": "red",
    "reaper": "bold red",
    "legendary": "bold magenta",
}


def get_relic_tier(kills: int) -> str:
    """Derive relic tier from kill count."""
    if kills >= RELIC_THRESHOLDS["legendary"]:
        return "legendary"
    elif kills >= RELIC_THRESHOLDS["reaper"]:
        return "reaper"
    elif kills >= RELIC_THRESHOLDS["bloodied"]:
        return "bloodied"
    return "unnamed"


# ---------------------------------------------------------------------------
# Kill recording
# ---------------------------------------------------------------------------

def record_kill(
    provenance: WeaponProvenance,
    captain_id: str | None = None,
    captain_name: str | None = None,
) -> tuple[str | None, str | None]:
    """Record a kill with this weapon. Returns (new_tier_or_None, new_epithet_or_None).

    new_tier is set if the weapon just crossed a relic threshold.
    new_epithet is set if this was a named captain kill and the weapon gets a name.
    """
    provenance.kills += 1
    old_tier = get_relic_tier(provenance.kills - 1)
    new_tier = get_relic_tier(provenance.kills)

    tier_change = new_tier if new_tier != old_tier else None

    new_epithet = None
    if captain_id and captain_id not in provenance.named_kills:
        provenance.named_kills.append(captain_id)
        # First named kill brands the weapon (if no epithet yet)
        if provenance.epithet is None and captain_name:
            provenance.epithet = f"{captain_name}'s Bane"
            new_epithet = provenance.epithet
        # Additional named kills add flavor but don't change the name
        elif len(provenance.named_kills) >= 3 and provenance.epithet and "Bane" in provenance.epithet:
            # Upgrade from "X's Bane" to a more fearsome name
            provenance.epithet = _generate_legendary_name(provenance)
            new_epithet = provenance.epithet

    return tier_change, new_epithet


def _generate_legendary_name(prov: WeaponProvenance) -> str:
    """Generate a legendary epithet for a weapon with 3+ named kills."""
    kill_count = len(prov.named_kills)
    if kill_count >= 5:
        return "Drinker of Captains"
    elif kill_count >= 3:
        return "The Captain Killer"
    return prov.epithet or ""


# ---------------------------------------------------------------------------
# Recognition
# ---------------------------------------------------------------------------

@dataclass
class RecognitionResult:
    """Result of a pirate recognizing the player's weapon."""
    recognized: bool = False
    weapon_name: str = ""
    relic_tier: str = "unnamed"
    fear_bonus: int = 0
    respect_bonus: int = 0
    flavor: str = ""


def check_recognition(
    provenance: WeaponProvenance | None,
    weapon_name: str,
    enemy_captain_id: str,
    enemy_familiarity: int,
    rng: "random.Random",
) -> RecognitionResult:
    """Check if a pirate captain recognizes the player's weapon.

    Recognition chance based on:
    - Relic tier (legendary = always, reaper = 60%, bloodied = 30%, unnamed = never)
    - Familiarity with player (higher = more likely to notice)
    - Whether this captain was killed by the weapon before (named_kills)
    """
    if provenance is None:
        return RecognitionResult()

    tier = get_relic_tier(provenance.kills)
    if tier == "unnamed":
        return RecognitionResult()

    # Base recognition chance by tier
    base_chance = {
        "bloodied": 0.30,
        "reaper": 0.60,
        "legendary": 0.90,
    }.get(tier, 0.0)

    # Familiarity bonus: +1% per familiarity point
    chance = base_chance + enemy_familiarity * 0.01

    # If this captain was killed by this weapon before, always recognize
    if enemy_captain_id in provenance.named_kills:
        chance = 1.0

    chance = min(0.95, chance)

    if rng.random() > chance:
        return RecognitionResult()

    # Recognized!
    provenance.times_recognized += 1
    display_name = provenance.custom_name or provenance.epithet or weapon_name

    fear_bonus = {"bloodied": 3, "reaper": 7, "legendary": 15}.get(tier, 0)
    respect_bonus = {"bloodied": 2, "reaper": 5, "legendary": 10}.get(tier, 0)

    # Flavor text
    if enemy_captain_id in provenance.named_kills:
        flavor = "Their eyes fix on your weapon. They KNOW that blade — it took one of their own."
    elif tier == "legendary":
        flavor = f"The pirate's grip tightens on their own sword. They've heard of {display_name}."
    elif tier == "reaper":
        flavor = "A flicker of recognition — they've heard stories about that weapon."
    else:
        flavor = "They notice the notches on your blade. This weapon has seen blood."

    return RecognitionResult(
        recognized=True,
        weapon_name=display_name,
        relic_tier=tier,
        fear_bonus=fear_bonus,
        respect_bonus=respect_bonus,
        flavor=flavor,
    )


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def get_weapon_display_name(
    base_name: str,
    provenance: WeaponProvenance | None,
) -> str:
    """Get the display name for a weapon, including epithet and tier."""
    if provenance is None:
        return base_name

    name = provenance.custom_name or provenance.epithet or base_name
    tier = get_relic_tier(provenance.kills)

    if tier == "unnamed":
        return name

    label = RELIC_LABELS[tier]
    color = RELIC_COLORS[tier]
    return f"[{color}]{name}[/{color}] ({label})"


def get_provenance_summary(provenance: WeaponProvenance) -> dict:
    """Get a summary dict for display."""
    tier = get_relic_tier(provenance.kills)
    return {
        "weapon_id": provenance.weapon_id,
        "kills": provenance.kills,
        "named_kills": provenance.named_kills,
        "epithet": provenance.epithet,
        "custom_name": provenance.custom_name,
        "relic_tier": tier,
        "relic_label": RELIC_LABELS[tier],
        "relic_color": RELIC_COLORS[tier],
        "times_recognized": provenance.times_recognized,
        "acquired_port": provenance.acquired_port,
        "acquired_day": provenance.acquired_day,
    }


# ---------------------------------------------------------------------------
# Provenance creation
# ---------------------------------------------------------------------------

def create_provenance(
    weapon_id: str,
    port_id: str = "",
    region: str = "",
    day: int = 0,
) -> WeaponProvenance:
    """Create fresh provenance for a newly acquired weapon."""
    return WeaponProvenance(
        weapon_id=weapon_id,
        acquired_port=port_id,
        acquired_day=day,
        acquired_region=region,
    )
