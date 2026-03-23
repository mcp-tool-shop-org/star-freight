"""Melee weapon catalog — blades, axes, and pole arms of the Age of Exploration.

Melee weapons replace bare fists as the primary combat tool. Each weapon adds
a flat damage bonus plus action-specific bonuses for thrust or slash.

Some weapons have style compatibility — wielding a rapier with La Destreza
training yields an extra +1 damage, reflecting how the weapon was designed
to be used.

Speed modifiers adjust stamina capacity: light daggers give +1 max stamina,
heavy polearms cost -1.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MeleeWeaponDef:
    """Static melee weapon definition — content data."""
    id: str
    name: str
    weapon_class: str                   # "blade", "dagger", "polearm"
    damage_bonus: int                   # flat bonus on any melee win
    thrust_bonus: int                   # extra damage on thrust wins
    slash_bonus: int                    # extra damage on slash wins
    silver_cost: int
    available_regions: tuple[str, ...]  # regions where purchasable
    description: str
    compatible_styles: tuple[str, ...] = ()  # fighting style IDs that synergize (+1 dmg)
    speed_mod: int = 0                  # stamina max adjustment (+ for light, - for heavy)


# ---------------------------------------------------------------------------
# Weapon catalog
# ---------------------------------------------------------------------------

MELEE_WEAPONS: dict[str, MeleeWeaponDef] = {w.id: w for w in [
    MeleeWeaponDef(
        id="cutlass",
        name="Cutlass",
        weapon_class="blade",
        damage_bonus=1,
        thrust_bonus=0,
        slash_bonus=1,
        silver_cost=25,
        available_regions=("Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"),
        description="The sailor's sword. Short, curved, and built for close quarters on a rolling deck.",
    ),
    MeleeWeaponDef(
        id="rapier",
        name="Rapier",
        weapon_class="blade",
        damage_bonus=1,
        thrust_bonus=2,
        slash_bonus=0,
        silver_cost=45,
        available_regions=("Mediterranean", "North Atlantic"),
        description="A long, thin thrusting sword. Devastating in trained hands, awkward in untrained ones.",
        compatible_styles=("la_destreza",),
    ),
    MeleeWeaponDef(
        id="boarding_axe",
        name="Boarding Axe",
        weapon_class="axe",
        damage_bonus=2,
        thrust_bonus=0,
        slash_bonus=1,
        silver_cost=35,
        available_regions=("North Atlantic",),
        description="Half hatchet, half hook. Made for cutting ropes and skulls in equal measure.",
        compatible_styles=("highland_broadsword",),
    ),
    MeleeWeaponDef(
        id="dagger",
        name="Dagger",
        weapon_class="dagger",
        damage_bonus=0,
        thrust_bonus=1,
        slash_bonus=0,
        silver_cost=10,
        available_regions=("Mediterranean", "North Atlantic", "West Africa", "East Indies", "South Seas"),
        description="A short blade for close work. Fast in the hand, light on the belt.",
        speed_mod=1,
    ),
    MeleeWeaponDef(
        id="kris",
        name="Kris",
        weapon_class="blade",
        damage_bonus=1,
        thrust_bonus=1,
        slash_bonus=1,
        silver_cost=40,
        available_regions=("East Indies", "South Seas"),
        description="A wavy-bladed dagger of spiritual significance. Every kris has a name and a history.",
        compatible_styles=("silat",),
    ),
    MeleeWeaponDef(
        id="ida_sword",
        name="Ida Sword",
        weapon_class="blade",
        damage_bonus=1,
        thrust_bonus=0,
        slash_bonus=2,
        silver_cost=35,
        available_regions=("West Africa",),
        description="A broad, leaf-shaped blade from the Yoruba kingdoms. Built for powerful slashing arcs.",
        compatible_styles=("dambe",),
    ),
    MeleeWeaponDef(
        id="leiomano",
        name="Leiomano",
        weapon_class="club",
        damage_bonus=2,
        thrust_bonus=0,
        slash_bonus=1,
        silver_cost=30,
        available_regions=("South Seas",),
        description="A war club edged with shark teeth. The wounds it leaves never heal cleanly.",
        compatible_styles=("lua",),
    ),
    MeleeWeaponDef(
        id="halberd",
        name="Halberd",
        weapon_class="polearm",
        damage_bonus=3,
        thrust_bonus=0,
        slash_bonus=2,
        silver_cost=60,
        available_regions=("Mediterranean",),
        description="An axe blade on a six-foot shaft. Reach and power, but slow in tight spaces.",
        speed_mod=-1,
    ),
]}


def get_melee_weapons_for_region(region: str) -> list[MeleeWeaponDef]:
    """Get melee weapons available for purchase in a region."""
    return [w for w in MELEE_WEAPONS.values() if region in w.available_regions]
