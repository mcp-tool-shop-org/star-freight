"""Ship upgrade catalog — 18 components across 6 categories.

Upgrades customize within a tier. They don't replace the ship class
progression — they let you specialize the ship you have.

Price curve: 50-150 cheap, 200-400 mid, 500+ top-tier.
This ensures upgrades are mid-game purchases, not starter buys.
"""

from portlight.engine.models import UpgradeCategory, UpgradeTemplate

UPGRADES: dict[str, UpgradeTemplate] = {u.id: u for u in [
    # --- Sails (speed) ---
    UpgradeTemplate(
        id="lateen_rigging",
        name="Lateen Rigging",
        category=UpgradeCategory.SAILS,
        price=120,
        speed_bonus=0.5,
    ),
    UpgradeTemplate(
        id="square_sails",
        name="Square Sails",
        category=UpgradeCategory.SAILS,
        price=300,
        speed_bonus=1.0,
    ),
    UpgradeTemplate(
        id="storm_canvas",
        name="Storm Canvas",
        category=UpgradeCategory.SAILS,
        price=250,
        speed_bonus=0.3,
        storm_resist_bonus=0.1,
    ),

    # --- Hull Plating (durability) ---
    UpgradeTemplate(
        id="iron_strapping",
        name="Iron Strapping",
        category=UpgradeCategory.HULL_PLATING,
        price=100,
        hull_max_bonus=15,
    ),
    UpgradeTemplate(
        id="copper_sheathing",
        name="Copper Sheathing",
        category=UpgradeCategory.HULL_PLATING,
        price=350,
        hull_max_bonus=25,
        speed_penalty=0.1,
    ),
    UpgradeTemplate(
        id="lead_lined",
        name="Lead-Lined Hull",
        category=UpgradeCategory.HULL_PLATING,
        price=500,
        hull_max_bonus=40,
        speed_penalty=0.3,
    ),

    # --- Armament (firepower) ---
    UpgradeTemplate(
        id="extra_gun_ports",
        name="Extra Gun Ports",
        category=UpgradeCategory.ARMAMENT,
        price=200,
        cannon_bonus=2,
    ),
    UpgradeTemplate(
        id="chain_shot_racks",
        name="Chain Shot Racks",
        category=UpgradeCategory.ARMAMENT,
        price=350,
        cannon_bonus=1,
        special="chain_shot",
    ),
    UpgradeTemplate(
        id="swivel_guns",
        name="Swivel Guns",
        category=UpgradeCategory.ARMAMENT,
        price=150,
        cannon_bonus=1,
        maneuver_bonus=0.05,
    ),

    # --- Cargo (capacity) ---
    UpgradeTemplate(
        id="extended_hold",
        name="Extended Hold",
        category=UpgradeCategory.CARGO,
        price=80,
        cargo_bonus=10,
    ),
    UpgradeTemplate(
        id="reinforced_bulkheads",
        name="Reinforced Bulkheads",
        category=UpgradeCategory.CARGO,
        price=250,
        cargo_bonus=20,
        speed_penalty=0.1,
    ),
    UpgradeTemplate(
        id="hidden_compartments",
        name="Hidden Compartments",
        category=UpgradeCategory.CARGO,
        price=400,
        cargo_bonus=5,
        special="contraband_immune",
    ),

    # --- Navigation (maneuver / safety) ---
    UpgradeTemplate(
        id="improved_rudder",
        name="Improved Rudder",
        category=UpgradeCategory.NAVIGATION,
        price=100,
        maneuver_bonus=0.1,
    ),
    UpgradeTemplate(
        id="crows_nest",
        name="Crow's Nest",
        category=UpgradeCategory.NAVIGATION,
        price=150,
        maneuver_bonus=0.05,
        special="danger_reduction",
    ),
    UpgradeTemplate(
        id="compass_rose",
        name="Compass Rose",
        category=UpgradeCategory.NAVIGATION,
        price=200,
        storm_resist_bonus=0.1,
    ),

    # --- Crew Quarters (crew capacity) ---
    UpgradeTemplate(
        id="hammock_deck",
        name="Hammock Deck",
        category=UpgradeCategory.CREW_QUARTERS,
        price=60,
        crew_max_bonus=5,
    ),
    UpgradeTemplate(
        id="officers_cabin",
        name="Officer's Cabin",
        category=UpgradeCategory.CREW_QUARTERS,
        price=200,
        crew_max_bonus=3,
        special="morale_bonus",
    ),
    UpgradeTemplate(
        id="surgeons_bay",
        name="Surgeon's Bay",
        category=UpgradeCategory.CREW_QUARTERS,
        price=350,
        special="injury_heal",
    ),
]}
