"""Ranged weapon catalog — period-appropriate firearms and thrown weapons.

These are the "magic equivalent" in Portlight's combat system. Limited ammo,
high impact, require resources. Historically grounded in the 16th century
Age of Exploration.

Weapon types:
  firearm    — loud, high damage, 1-turn reload, can't be parried
  thrown      — silent, moderate damage, no reload, expendable
  mechanical  — crossbow family, high accuracy, 2-turn reload

Firearms attract attention (faction reputation consequence for using in duels).
Thrown weapons are silent — no social cost.
DODGE avoids all ranged attacks.
PARRY cannot block firearms (bullets go through guards).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RangedWeapon:
    """Static weapon definition — content data."""
    id: str
    name: str
    weapon_type: str            # "firearm", "thrown", "mechanical"
    damage_min: int
    damage_max: int
    accuracy: float             # base hit chance (0.0-1.0)
    reload_turns: int           # 0 = no reload (thrown), 1+ = turns to reload
    silver_cost: int            # per unit (weapon or ammo bundle)
    ammo_per_purchase: int      # how many you get per purchase
    available_regions: tuple[str, ...]  # regions where this can be bought
    description: str
    # Special effects
    stun_turns: int = 0         # turns opponent is stunned on hit (bolas)
    loud: bool = False          # attracts attention, faction consequences


# ---------------------------------------------------------------------------
# Weapon catalog
# ---------------------------------------------------------------------------

RANGED_WEAPONS: dict[str, RangedWeapon] = {w.id: w for w in [
    RangedWeapon(
        id="matchlock_pistol",
        name="Matchlock Pistol",
        weapon_type="firearm",
        damage_min=4,
        damage_max=6,
        accuracy=0.65,
        reload_turns=1,
        silver_cost=50,
        ammo_per_purchase=1,  # buy the gun, ammo sold separately
        available_regions=("Mediterranean", "North Atlantic"),
        description="A clumsy but devastating single-shot pistol. The slow match glows in the dark.",
        loud=True,
    ),
    RangedWeapon(
        id="wheellock_pistol",
        name="Wheellock Pistol",
        weapon_type="firearm",
        damage_min=5,
        damage_max=7,
        accuracy=0.75,
        reload_turns=1,
        silver_cost=120,
        ammo_per_purchase=1,
        available_regions=("Mediterranean", "North Atlantic"),
        description="German engineering. The spring-wound mechanism fires faster and more reliably than matchlock.",
        loud=True,
    ),
    RangedWeapon(
        id="arquebus_pistol",
        name="Arquebus Pistol",
        weapon_type="firearm",
        damage_min=4,
        damage_max=7,
        accuracy=0.60,
        reload_turns=1,
        silver_cost=65,
        ammo_per_purchase=1,
        available_regions=("East Indies", "West Africa"),
        description="A Portuguese trade pistol, common wherever the carracks sailed. Rough but reliable.",
        loud=True,
    ),
    RangedWeapon(
        id="hand_crossbow",
        name="Hand Crossbow",
        weapon_type="mechanical",
        damage_min=3,
        damage_max=5,
        accuracy=0.80,
        reload_turns=2,
        silver_cost=40,
        ammo_per_purchase=1,
        available_regions=("Mediterranean",),
        description="A compact crossbow that fits in a belt holster. Silent and accurate, but slow to reload.",
        loud=False,
    ),
    RangedWeapon(
        id="throwing_knife",
        name="Throwing Knife",
        weapon_type="thrown",
        damage_min=2,
        damage_max=3,
        accuracy=0.70,
        reload_turns=0,
        silver_cost=8,
        ammo_per_purchase=1,
        available_regions=("Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"),
        description="A balanced blade weighted for throwing. Cheap, silent, disposable.",
        loud=False,
    ),
    RangedWeapon(
        id="sling",
        name="Sling",
        weapon_type="thrown",
        damage_min=1,
        damage_max=3,
        accuracy=0.60,
        reload_turns=0,
        silver_cost=5,
        ammo_per_purchase=3,  # stones are cheap
        available_regions=("West Africa", "South Seas"),
        description="A leather sling and smooth stones. Ancient, effective, and completely silent.",
        loud=False,
    ),
    RangedWeapon(
        id="blowgun",
        name="Blowgun",
        weapon_type="mechanical",
        damage_min=1,
        damage_max=2,
        accuracy=0.85,
        reload_turns=0,
        silver_cost=20,
        ammo_per_purchase=5,
        available_regions=("East Indies", "South Seas"),
        description="A slender bamboo tube firing poisoned darts. Almost no damage, but the toxin weakens. Silent as breath.",
        loud=False,
        stun_turns=1,
    ),
    RangedWeapon(
        id="bolas",
        name="Bolas",
        weapon_type="thrown",
        damage_min=1,
        damage_max=2,
        accuracy=0.55,
        reload_turns=0,
        silver_cost=15,
        ammo_per_purchase=1,
        available_regions=("South Seas",),
        description="Three weighted stones on cord. Wraps around legs, arms, or weapons. More disabling than damaging.",
        loud=False,
        stun_turns=1,
    ),
]}


# ---------------------------------------------------------------------------
# Ammo types (sold separately from firearms/crossbows)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AmmoDef:
    """Ammunition sold at ports."""
    id: str
    name: str
    weapon_type: str            # "firearm" or "mechanical"
    silver_cost: int            # per bundle
    quantity: int               # rounds per bundle
    available_regions: tuple[str, ...]


AMMO: dict[str, AmmoDef] = {a.id: a for a in [
    AmmoDef(
        id="pistol_shot",
        name="Pistol Shot & Powder",
        weapon_type="firearm",
        silver_cost=5,
        quantity=3,
        available_regions=("Mediterranean", "North Atlantic", "East Indies", "West Africa"),
    ),
    AmmoDef(
        id="crossbow_bolts",
        name="Crossbow Bolts",
        weapon_type="mechanical",
        silver_cost=4,
        quantity=5,
        available_regions=("Mediterranean",),
    ),
    AmmoDef(
        id="blowgun_darts",
        name="Blowgun Darts (poisoned)",
        weapon_type="mechanical",
        silver_cost=3,
        quantity=8,
        available_regions=("East Indies", "South Seas"),
    ),
]}


def get_weapons_for_region(region: str) -> list[RangedWeapon]:
    """Get ranged weapons available for purchase in a region."""
    return [w for w in RANGED_WEAPONS.values() if region in w.available_regions]


def get_ammo_for_region(region: str) -> list[AmmoDef]:
    """Get ammo types available in a region."""
    return [a for a in AMMO.values() if region in a.available_regions]
