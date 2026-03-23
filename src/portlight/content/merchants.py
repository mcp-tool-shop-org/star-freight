"""NPC merchant catalog — named shopkeepers at ports across the Known World.

Each merchant has a personality, regional inventory, and price markup.
Not every port has a merchant — remote or lawless ports may lack proper shops.
Merchants sell melee weapons, armor, ranged weapons, and ammo from their
port's region.

The `armory` CLI command remains a quick-buy shortcut at base price.
Merchants add flavor, personality, and a small markup.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MerchantDef:
    """A named shopkeeper at a specific port."""
    id: str
    name: str
    port_id: str
    title: str                          # "Weaponsmith", "Armorer", "Outfitter"
    personality: str                    # "gruff", "charming", "shrewd", "quiet"
    description: str
    greeting: str
    inventory_types: tuple[str, ...]    # "melee", "armor", "ranged", "ammo"
    price_markup: float                 # 1.0 = base, 1.15 = 15% markup


# ---------------------------------------------------------------------------
# Merchant catalog — one per major port, some ports have none
# ---------------------------------------------------------------------------

MERCHANTS: dict[str, MerchantDef] = {m.id: m for m in [
    # === Mediterranean ===
    MerchantDef(
        id="marco_the_blade",
        name="Marco",
        port_id="porto_novo",
        title="Master Weaponsmith",
        personality="charming",
        description="A stocky Genoese smith with oil-stained hands and a shop full of blades hanging from the ceiling.",
        greeting="Ah, a captain with taste! Come, see what Marco has forged this week.",
        inventory_types=("melee", "ranged", "ammo"),
        price_markup=1.10,
    ),
    MerchantDef(
        id="fatima_armorworks",
        name="Fatima",
        port_id="al_manar",
        title="Armorer",
        personality="shrewd",
        description="She runs the finest armor workshop south of the strait. Her chain is tight and her prices tighter.",
        greeting="You want protection? Protection costs. But so does a funeral.",
        inventory_types=("armor", "melee"),
        price_markup=1.15,
    ),
    MerchantDef(
        id="old_silva",
        name="Old Silva",
        port_id="silva_bay",
        title="Ship Outfitter",
        personality="quiet",
        description="A retired shipwright who sells what sailors need. His shop smells of tar and salt.",
        greeting="What do you need. I have it or I don't.",
        inventory_types=("melee", "ranged", "ammo", "armor"),
        price_markup=1.05,
    ),
    # Corsair's Rest — no legitimate merchant (black market port)

    # === North Atlantic ===
    MerchantDef(
        id="sergeant_gruber",
        name="Sgt. Gruber",
        port_id="ironhaven",
        title="Arsenal Master",
        personality="gruff",
        description="A retired dragoon who sells military-grade equipment from a fortress-turned-shop.",
        greeting="State your business. I don't sell to tourists.",
        inventory_types=("melee", "armor", "ranged", "ammo"),
        price_markup=1.12,
    ),
    MerchantDef(
        id="widow_kael",
        name="Widow Kael",
        port_id="stormwall",
        title="Outfitter",
        personality="quiet",
        description="She inherited her husband's shop when he didn't come back from the ice. She knows every item by touch.",
        greeting="The wind's picking up. Buy what you need before it gets worse.",
        inventory_types=("armor", "melee", "ammo"),
        price_markup=1.08,
    ),
    MerchantDef(
        id="hamish_iron",
        name="Hamish",
        port_id="thornport",
        title="Bladesmith",
        personality="gruff",
        description="A Highland smith who forges axes and broadswords in a workshop built into the cliff face.",
        greeting="If it's sharp and it swings, I made it. If it's dull, someone else made it.",
        inventory_types=("melee", "ranged"),
        price_markup=1.10,
    ),

    # === West Africa ===
    MerchantDef(
        id="adaeze_arms",
        name="Adaeze",
        port_id="sun_harbor",
        title="Arms Dealer",
        personality="charming",
        description="A trader's daughter who turned her father's cloth stall into a weapons bazaar. She haggles like she breathes.",
        greeting="Welcome, captain! Everything you see is the best in the harbor. I should know — I tested it myself.",
        inventory_types=("melee", "armor", "ranged", "ammo"),
        price_markup=1.08,
    ),
    MerchantDef(
        id="kofi_leather",
        name="Kofi",
        port_id="palm_cove",
        title="Leatherworker",
        personality="quiet",
        description="He works crocodile hide into armor that turns blades. His fingers are scarred from the stitching awl.",
        greeting="Good leather takes time. I have what's ready.",
        inventory_types=("armor",),
        price_markup=1.05,
    ),
    # Iron Point — mining port, no dedicated merchant
    MerchantDef(
        id="yaa_sharpedge",
        name="Yaa",
        port_id="pearl_shallows",
        title="Blade Merchant",
        personality="shrewd",
        description="She sources knives and slings from inland villages and sells them to sailors at the dock.",
        greeting="Pearl Shallows has the best steel on the coast. Don't let anyone tell you otherwise.",
        inventory_types=("melee", "ranged"),
        price_markup=1.12,
    ),

    # === East Indies ===
    MerchantDef(
        id="chen_forge",
        name="Master Chen",
        port_id="jade_port",
        title="Master Smith",
        personality="quiet",
        description="Third generation bladesmith. His kris daggers are considered sacred objects in three kingdoms.",
        greeting="A captain who values craftsmanship. Please, examine my work.",
        inventory_types=("melee", "armor"),
        price_markup=1.15,
    ),
    MerchantDef(
        id="devi_arms",
        name="Devi",
        port_id="monsoon_reach",
        title="Armorer",
        personality="charming",
        description="She imports brigandine plates from the mainland and fits them in her harbor-side workshop.",
        greeting="Monsoon season is coming. You'll want something between you and the sea.",
        inventory_types=("armor", "ammo"),
        price_markup=1.10,
    ),
    MerchantDef(
        id="li_crossbow",
        name="Li Wei",
        port_id="silk_haven",
        title="Mechanist",
        personality="shrewd",
        description="A craftsman who builds hand crossbows from bamboo and horn. Quiet weapons for quiet work.",
        greeting="Silk Haven values discretion. So do my weapons.",
        inventory_types=("ranged", "ammo", "melee"),
        price_markup=1.12,
    ),
    # Crosswind Isle, Dragon's Gate, Spice Narrows — no weapon merchants (trade/pirate ports)

    # === South Seas ===
    MerchantDef(
        id="tane_warrior",
        name="Tane",
        port_id="coral_throne",
        title="Warrior Outfitter",
        personality="gruff",
        description="A former reef warrior who now outfits captains with the weapons of his people.",
        greeting="The reef teaches you to fight or it teaches you to drown. Which are you?",
        inventory_types=("melee", "ranged"),
        price_markup=1.08,
    ),
    MerchantDef(
        id="malia_provisions",
        name="Malia",
        port_id="typhoon_anchorage",
        title="Outfitter",
        personality="charming",
        description="She runs the only proper shop between the reefs. If she doesn't have it, you don't need it.",
        greeting="Typhoon Anchorage! Where the brave come to buy and the foolish come to sell.",
        inventory_types=("melee", "armor", "ammo"),
        price_markup=1.10,
    ),
    # Ember Isle — volcanic outpost, no merchant
]}


def get_merchants_at_port(port_id: str) -> list[MerchantDef]:
    """Get all merchants at a specific port."""
    return [m for m in MERCHANTS.values() if m.port_id == port_id]


def get_merchant(merchant_id: str) -> MerchantDef | None:
    """Get a merchant by ID."""
    return MERCHANTS.get(merchant_id)
