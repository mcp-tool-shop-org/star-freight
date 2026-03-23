"""Armor catalog — period-appropriate defensive gear for personal combat.

Three tiers balance protection against mobility:
  light   — leather and padding. DR 1, no penalties. Universal.
  medium  — chain and brigandine. DR 1, dodge/stamina penalties. Tradeoff vs agility.
  heavy   — plate cuirass. DR 2, significant weight. Real protection, real cost.

Base melee damage is 2-3. DR 1 reduces to 1-2 (manageable). DR 2 reduces to 0-1
(serious protection, but firearms at 4-7 still punch through — historically accurate).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArmorDef:
    """Static armor definition — content data."""
    id: str
    name: str
    armor_type: str                     # "light", "medium", "heavy"
    damage_reduction: int               # flat DR subtracted from incoming damage
    dodge_penalty: int                  # extra stamina cost added to dodge action
    stamina_penalty: int                # reduction to max stamina (negative value)
    silver_cost: int
    available_regions: tuple[str, ...]  # regions where purchasable
    description: str


# ---------------------------------------------------------------------------
# Armor catalog
# ---------------------------------------------------------------------------

ARMOR: dict[str, ArmorDef] = {a.id: a for a in [
    ArmorDef(
        id="leather_vest",
        name="Leather Vest",
        armor_type="light",
        damage_reduction=1,
        dodge_penalty=0,
        stamina_penalty=0,
        silver_cost=30,
        available_regions=("Mediterranean", "North Atlantic", "West Africa"),
        description="Stiff cowhide shaped to the torso. Won't stop a bullet, but a blade has to work for it.",
    ),
    ArmorDef(
        id="padded_coat",
        name="Padded Coat",
        armor_type="light",
        damage_reduction=1,
        dodge_penalty=0,
        stamina_penalty=0,
        silver_cost=35,
        available_regions=("North Atlantic", "East Indies"),
        description="Layered cotton quilting over a wool core. Surprisingly effective against slashing attacks.",
    ),
    ArmorDef(
        id="chain_shirt",
        name="Chain Shirt",
        armor_type="medium",
        damage_reduction=1,
        dodge_penalty=1,
        stamina_penalty=-1,
        silver_cost=80,
        available_regions=("Mediterranean", "North Atlantic"),
        description="Riveted iron rings over a linen undershirt. The weight is real, but so is the protection.",
    ),
    ArmorDef(
        id="brigandine",
        name="Brigandine",
        armor_type="medium",
        damage_reduction=1,
        dodge_penalty=1,
        stamina_penalty=-1,
        silver_cost=90,
        available_regions=("East Indies", "West Africa"),
        description="Small steel plates riveted between layers of cloth. Eastern craftsmanship, flexible and quiet.",
    ),
    ArmorDef(
        id="coconut_fiber_armor",
        name="Coconut Fiber Armor",
        armor_type="light",
        damage_reduction=1,
        dodge_penalty=0,
        stamina_penalty=0,
        silver_cost=20,
        available_regions=("South Seas",),
        description="Woven coconut husk and pandanus leaves, layered thick. Surprisingly tough against blades, and it floats.",
    ),
    ArmorDef(
        id="cuirass",
        name="Steel Cuirass",
        armor_type="heavy",
        damage_reduction=2,
        dodge_penalty=2,
        stamina_penalty=-2,
        silver_cost=200,
        available_regions=("North Atlantic",),
        description="A hammered breastplate from a Northern foundry. You feel every ounce, but blades bounce off.",
    ),
]}


def get_armor_for_region(region: str) -> list[ArmorDef]:
    """Get armor available for purchase in a region."""
    return [a for a in ARMOR.values() if region in a.available_regions]
