"""Captain identity system — eight archetypes + custom that reshape the game.

Each captain type changes:
  - pricing (buy/sell modifiers, luxury handling)
  - voyage (provision burn, speed, storm resilience, inspection profile)
  - reputation (trust growth, heat growth, starting standing)
  - contracts (bias toward certain contract families)
  - world relationships (bloc alignment, faction standing, NPC connections)

These are not passive +5% perks. They change route choice, capital timing,
risk profile, and viable trade styles from the opening hours. Each character
has a backstory connecting them to the 134 NPCs in the Known World.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CaptainType(str, Enum):
    """Playable captain archetypes."""
    MERCHANT = "merchant"
    SMUGGLER = "smuggler"
    NAVIGATOR = "navigator"
    PRIVATEER = "privateer"
    CORSAIR = "corsair"
    SCHOLAR = "scholar"
    MERCHANT_PRINCE = "merchant_prince"
    DOCKHAND = "dockhand"
    BOUNTY_HUNTER = "bounty_hunter"
    CUSTOM = "custom"


@dataclass(frozen=True)
class PricingModifiers:
    """How this captain affects market prices."""
    buy_price_mult: float = 1.0       # < 1 = cheaper buys
    sell_price_mult: float = 1.0      # > 1 = better sells
    luxury_sell_bonus: float = 0.0    # extra sell multiplier for luxury goods
    port_fee_mult: float = 1.0       # multiplier on port docking fees


@dataclass(frozen=True)
class VoyageModifiers:
    """How this captain affects life at sea."""
    provision_burn: float = 1.0       # daily provision consumption rate
    speed_bonus: float = 0.0          # flat addition to ship speed
    storm_resist_bonus: float = 0.0   # added to ship's storm_resist
    cargo_damage_mult: float = 1.0    # multiplier on cargo damage qty


@dataclass(frozen=True)
class InspectionProfile:
    """How authorities treat this captain."""
    inspection_chance_mult: float = 1.0   # multiplier on inspection event weight
    seizure_risk: float = 0.0             # base chance of cargo seizure during inspection
    fine_mult: float = 1.0               # multiplier on inspection fines


@dataclass(frozen=True)
class ReputationSeed:
    """Starting reputation values for this archetype."""
    commercial_trust: int = 0
    customs_heat: int = 0
    # Per-region starting standing
    mediterranean: int = 0
    north_atlantic: int = 0
    west_africa: int = 0
    east_indies: int = 0
    south_seas: int = 0
    # Underworld faction standing (faction_id -> starting value)
    underworld: dict[str, int] | None = None


@dataclass(frozen=True)
class CaptainTemplate:
    """Full archetype definition. Immutable reference data."""
    id: CaptainType
    name: str
    title: str                           # e.g. "Licensed Merchant"
    description: str
    home_region: str
    home_port_id: str
    starting_silver: int
    starting_ship_id: str
    starting_provisions: int
    pricing: PricingModifiers = field(default_factory=PricingModifiers)
    voyage: VoyageModifiers = field(default_factory=VoyageModifiers)
    inspection: InspectionProfile = field(default_factory=InspectionProfile)
    reputation_seed: ReputationSeed = field(default_factory=ReputationSeed)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    backstory: str = ""                  # narrative backstory text
    mentor_npc_id: str = ""              # NPC who mentored this captain
    bloc_alignment: str = ""             # trade bloc affiliation
    faction_alignment: dict[str, int] = field(default_factory=dict)  # pirate faction starting standing


# ---------------------------------------------------------------------------
# The three captains
# ---------------------------------------------------------------------------

CAPTAIN_TEMPLATES: dict[CaptainType, CaptainTemplate] = {
    CaptainType.MERCHANT: CaptainTemplate(
        id=CaptainType.MERCHANT,
        name="The Merchant",
        title="Licensed Trader",
        description=(
            "A legitimate operator with standing in the major ports. "
            "Your licenses open doors, your reputation keeps them open. "
            "Steady commerce and reliable delivery are your weapons."
        ),
        home_region="Mediterranean",
        home_port_id="porto_novo",
        starting_silver=550,             # slightly more capital
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=0.92,         # 8% cheaper buys (trusted buyer)
            sell_price_mult=1.05,        # 5% better sells (known supplier)
            luxury_sell_bonus=0.0,       # no special luxury edge
            port_fee_mult=0.7,           # 30% cheaper port fees (licensed)
        ),
        voyage=VoyageModifiers(
            provision_burn=1.0,          # normal consumption
            speed_bonus=0.0,             # no speed edge
            storm_resist_bonus=0.0,      # no storm edge
            cargo_damage_mult=1.0,       # normal cargo risk
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=0.5,  # 50% fewer inspections (known trader)
            seizure_risk=0.0,            # clean record
            fine_mult=0.6,               # lower fines (good standing)
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=15,
            customs_heat=0,
            mediterranean=10,
        ),
        strengths=[
            "Better buy/sell prices at all ports",
            "Cheaper port fees (licensed operator)",
            "Fewer inspections, lower fines",
            "Starts with commercial trust and Med standing",
        ],
        weaknesses=[
            "No voyage advantages",
            "No luxury trade edge",
            "Must build reputation the hard way in distant regions",
        ],
        backstory=(
            "Born into Porto Novo's trading families. The Exchange Guild trained you. "
            "Your ledger is clean, your contracts are honored, and Senhora Costa "
            "herself signed your trading license. Marta Soares vouches for you at the "
            "Exchange. Fernanda Reis prioritizes your contracts."
        ),
        mentor_npc_id="pn_marta",
        bloc_alignment="exchange_alliance",
    ),

    CaptainType.SMUGGLER: CaptainTemplate(
        id=CaptainType.SMUGGLER,
        name="The Smuggler",
        title="Shadow Trader",
        description=(
            "You trade where others won't and sell what others can't. "
            "Luxury margins are your bread and butter, but the law is always "
            "one bad inspection away. High risk, high reward."
        ),
        home_region="West Africa",
        home_port_id="palm_cove",        # remote, low scrutiny
        starting_silver=500,             # slightly less than merchant, but resourceful
        starting_ship_id="coastal_sloop",
        starting_provisions=35,          # knows how to stock up
        pricing=PricingModifiers(
            buy_price_mult=1.0,          # no general buy edge
            sell_price_mult=0.98,        # 2% worse on staples (no network)
            luxury_sell_bonus=0.28,      # 28% bonus selling luxury goods
            port_fee_mult=0.9,           # 10% cheaper port fees (knows the docks)
        ),
        voyage=VoyageModifiers(
            provision_burn=0.85,         # 15% less provision use (resourceful)
            speed_bonus=0.0,
            storm_resist_bonus=0.0,
            cargo_damage_mult=0.8,       # 20% less cargo damage (careful packer)
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=1.3,  # 30% more inspections (suspicious profile)
            seizure_risk=0.05,           # 5% chance of cargo seizure on inspection
            fine_mult=1.2,               # slightly higher fines
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=0,
            customs_heat=8,
            west_africa=5,
        ),
        strengths=[
            "30% bonus selling luxury goods (silk, spice, porcelain)",
            "5% cheaper buys and 10% cheaper port fees",
            "Less provision burn and cargo damage at sea",
            "Thrives on volatile markets and shortages",
        ],
        weaknesses=[
            "30% more inspections, higher fines",
            "5% chance of cargo seizure during inspection",
            "Slightly worse sell prices on staple goods",
            "Starts with customs heat, no commercial trust",
        ],
        backstory=(
            "You grew up in Palm Cove where Mama Joy's rum house was your school "
            "and the Seven Houses taught you that rules are suggestions. Captain Abel "
            "showed you how to read a harbor without manifests. The legitimate world "
            "has doors you'll never open. You found the windows."
        ),
        mentor_npc_id="pc_mama_joy",
        bloc_alignment="gold_coast",
    ),

    CaptainType.NAVIGATOR: CaptainTemplate(
        id=CaptainType.NAVIGATOR,
        name="The Navigator",
        title="Route Specialist",
        description=(
            "You read the winds better than anyone and your crew trusts your charts. "
            "Long hauls that break other captains are your bread run. "
            "Distant markets open to you before anyone else can reach them."
        ),
        home_region="Mediterranean",
        home_port_id="silva_bay",        # shipyard port, timber-rich
        starting_silver=450,
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=1.05,         # 5% more expensive buys (not a negotiator)
            sell_price_mult=1.0,         # normal sell prices
            luxury_sell_bonus=0.0,
            port_fee_mult=1.0,
        ),
        voyage=VoyageModifiers(
            provision_burn=0.7,          # 30% less provision use (efficient routing)
            speed_bonus=1.5,             # +1.5 flat speed (reads the winds)
            storm_resist_bonus=0.15,     # 15% extra storm resistance
            cargo_damage_mult=0.7,       # 30% less cargo damage (good stowage)
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=1.0,
            seizure_risk=0.0,
            fine_mult=1.0,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=5,
            customs_heat=0,
            mediterranean=5,
            east_indies=5,
        ),
        strengths=[
            "30% less provision consumption at sea",
            "+1.5 speed bonus (faster voyages)",
            "Extra storm resistance and less cargo damage",
            "Starting familiarity with East Indies",
        ],
        weaknesses=[
            "5% more expensive buys (worse negotiator)",
            "No special sell price advantages",
            "Slower commercial reputation growth in settled markets",
        ],
        backstory=(
            "The Shipwrights' Brotherhood raised you. Elena Madeira taught you to "
            "read a hull. Rosa Carvalho fed you at the Dry Dock. You don't trade "
            "well — you SAIL well. The long routes are yours. Every horizon is an "
            "invitation."
        ),
        mentor_npc_id="sb_elena",
        bloc_alignment="exchange_alliance",
    ),

    # =========================================================================
    # NEW ARCHETYPES
    # =========================================================================

    CaptainType.PRIVATEER: CaptainTemplate(
        id=CaptainType.PRIVATEER,
        name="The Privateer",
        title="Licensed Hunter",
        description=(
            "Commander Vogt gave you a letter of marque and a cutter. Your job: "
            "patrol the North Atlantic, intercept smugglers, and deliver seized "
            "goods to Stormwall. What you confiscate is yours to sell. The line "
            "between law enforcement and piracy is wherever Vogt draws it."
        ),
        home_region="North Atlantic",
        home_port_id="stormwall",
        starting_silver=475,
        starting_ship_id="swift_cutter",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=0.95,
            sell_price_mult=1.02,
            luxury_sell_bonus=0.10,
            port_fee_mult=0.6,
        ),
        voyage=VoyageModifiers(
            provision_burn=0.9,
            speed_bonus=0.5,
            storm_resist_bonus=0.05,
            cargo_damage_mult=0.9,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=0.3,
            seizure_risk=0.0,
            fine_mult=0.5,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=8,
            customs_heat=0,
            north_atlantic=8,
            mediterranean=3,
            underworld={"iron_wolves": -5},
        ),
        strengths=[
            "Nearly inspection-proof (Pact commission)",
            "Starts with a Cutter (faster than sloop)",
            "Low port fees at Pact ports",
            "Strong North Atlantic standing",
        ],
        weaknesses=[
            "Iron Wolves are hostile from day 1",
            "Limited underworld access initially",
            "Lower starting silver",
            "Vogt expects results — the commission can be revoked",
        ],
        backstory=(
            "Commander Vogt gave you a letter of marque and a cutter. Your job: "
            "patrol the North Atlantic, intercept smugglers, and deliver seized "
            "goods to Stormwall. Inspector Berg trusts your manifests. Astrid "
            "Vekhren watches your progress. The Iron Wolves know your face — "
            "and they haven't forgiven the ships you've taken."
        ),
        mentor_npc_id="sw_commander_vogt",
        bloc_alignment="iron_pact",
        faction_alignment={"iron_wolves": -5},
    ),

    CaptainType.CORSAIR: CaptainTemplate(
        id=CaptainType.CORSAIR,
        name="The Corsair",
        title="Crimson Tide Captain",
        description=(
            "A pirate captain who answers to the Crimson Tide. The cove is home. "
            "The legitimate world doesn't want you. You don't want it back. "
            "Your crimson pennant opens shadow ports and closes everything else."
        ),
        home_region="Mediterranean",
        home_port_id="corsairs_rest",
        starting_silver=500,
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=1.05,
            sell_price_mult=0.95,
            luxury_sell_bonus=0.15,
            port_fee_mult=0.5,
        ),
        voyage=VoyageModifiers(
            provision_burn=0.9,
            speed_bonus=0.3,
            storm_resist_bonus=0.0,
            cargo_damage_mult=0.85,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=1.5,
            seizure_risk=0.08,
            fine_mult=1.5,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=0,
            customs_heat=12,
            mediterranean=-5,
            underworld={"crimson_tide": 25},
        ),
        strengths=[
            "Starts with Crimson Tide standing (trade partner)",
            "Shadow port discounts",
            "Luxury sell bonus from pirate connections",
            "Contraband access from day 1",
        ],
        weaknesses=[
            "Highest customs heat at start",
            "Worst legitimate standing",
            "Most inspected, highest seizure risk",
            "Deep Reef Brotherhood is hostile",
        ],
        backstory=(
            "One-Eye Basso waved you through the cove mouth when you were sixteen. "
            "Mama Lucia fed you. Ghost taught you to move cargo in the dark. "
            "No One gave you the Tide's crimson pennant and a territory to patrol. "
            "The legitimate world doesn't want you. You don't want it back."
        ),
        mentor_npc_id="cr_no_one",
        bloc_alignment="shadow_ports",
        faction_alignment={"crimson_tide": 25, "deep_reef": -5},
    ),

    CaptainType.SCHOLAR: CaptainTemplate(
        id=CaptainType.SCHOLAR,
        name="The Scholar",
        title="Wind Temple Student",
        description=(
            "A Wind Temple student who left to learn what books can't teach. "
            "Brother Anand taught you to read the wind. You carry a monsoon chart, "
            "a medicine kit, and a notebook full of observations the monks say "
            "will be important someday."
        ),
        home_region="East Indies",
        home_port_id="monsoon_reach",
        starting_silver=400,
        starting_ship_id="coastal_sloop",
        starting_provisions=35,
        pricing=PricingModifiers(
            buy_price_mult=1.0,
            sell_price_mult=1.0,
            luxury_sell_bonus=0.0,
            port_fee_mult=0.85,
        ),
        voyage=VoyageModifiers(
            provision_burn=0.75,
            speed_bonus=1.0,
            storm_resist_bonus=0.10,
            cargo_damage_mult=0.8,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=0.7,
            seizure_risk=0.0,
            fine_mult=0.8,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=5,
            customs_heat=0,
            mediterranean=2,
            north_atlantic=2,
            west_africa=2,
            east_indies=8,
            south_seas=2,
        ),
        strengths=[
            "Excellent weather reading (+1.0 speed, storm resist)",
            "Best provision efficiency (temple training)",
            "Trusted everywhere (scholar's respect)",
            "Strong East Indies connections",
        ],
        weaknesses=[
            "No trade advantages at all",
            "Low starting silver",
            "No combat or underworld edge",
            "Jack of all regions, master of none commercially",
        ],
        backstory=(
            "Brother Anand taught you to read the wind. Shipwright Devi taught you "
            "hull science. You left the Temple not because you stopped believing, "
            "but because the wind told you to go. Tea Master Huang pours you the "
            "good leaves whenever you return. The monks say your notebook will be "
            "important someday."
        ),
        mentor_npc_id="mr_brother_anand",
        bloc_alignment="free_ports",
    ),

    CaptainType.MERCHANT_PRINCE: CaptainTemplate(
        id=CaptainType.MERCHANT_PRINCE,
        name="The Merchant Prince",
        title="Khoury Dynasty Scion",
        description=(
            "Born into the Khoury dynasty's orbit. Old money, old connections, "
            "old expectations. You have every advantage — silver, trust, connections "
            "— and every expectation. The dynasty invested in you. They expect returns."
        ),
        home_region="Mediterranean",
        home_port_id="al_manar",
        starting_silver=700,
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=0.90,
            sell_price_mult=1.08,
            luxury_sell_bonus=0.12,
            port_fee_mult=0.65,
        ),
        voyage=VoyageModifiers(
            provision_burn=1.0,
            speed_bonus=0.0,
            storm_resist_bonus=0.0,
            cargo_damage_mult=1.0,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=0.4,
            seizure_risk=0.0,
            fine_mult=0.4,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=18,
            customs_heat=0,
            mediterranean=12,
            east_indies=5,
        ),
        strengths=[
            "Best buy/sell prices (dynasty connections)",
            "Most starting silver (700)",
            "Highest trust (18), lowest inspections",
            "Prestige in Mediterranean and East Indies",
        ],
        weaknesses=[
            "Zero exploration advantage",
            "Zero combat or underworld edge",
            "The dynasty expects results — failure is political",
            "Pampered: normal provision burn, no storm resistance",
        ],
        backstory=(
            "You grew up in the Khoury Palace, learning trade from Nadia herself. "
            "Yasmin the Spice Mother taught you to judge quality. Tariq Sayed "
            "brokers your contracts. You have every advantage — silver, trust, "
            "connections — and every expectation. The dynasty invested in you. "
            "They expect returns."
        ),
        mentor_npc_id="am_senhora_nadia",
        bloc_alignment="exchange_alliance",
    ),

    CaptainType.DOCKHAND: CaptainTemplate(
        id=CaptainType.DOCKHAND,
        name="The Dockhand",
        title="Self-Made Captain",
        description=(
            "Nobody. You started with nothing at the Free Port and worked your way "
            "onto a ship. Nobody knows your name. Nobody owes you anything. Nobody "
            "is hunting you. You are perfectly, terrifyingly free."
        ),
        home_region="East Indies",
        home_port_id="crosswind_isle",
        starting_silver=300,
        starting_ship_id="coastal_sloop",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=1.0,
            sell_price_mult=1.0,
            luxury_sell_bonus=0.0,
            port_fee_mult=1.0,
        ),
        voyage=VoyageModifiers(
            provision_burn=0.85,
            speed_bonus=0.0,
            storm_resist_bonus=0.0,
            cargo_damage_mult=0.9,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=1.0,
            seizure_risk=0.0,
            fine_mult=1.0,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=0,
            customs_heat=0,
        ),
        strengths=[
            "No enemies — complete neutrality",
            "No heat, no baggage, total freedom",
            "Provision efficiency from real hardship",
            "The truest underdog story in the game",
        ],
        weaknesses=[
            "Least starting silver (300) — hard mode",
            "No trust, no standing, no connections",
            "No trade, combat, or exploration advantages",
            "Everything must be earned from zero",
        ],
        backstory=(
            "You arrived at Crosswind Isle on a cargo ship — as cargo. Dock Master "
            "Tao gave you work. Mother Ko gave you meals. Hassan taught you to count "
            "currency. You earned enough to buy the worst sloop in the harbor. "
            "Nobody knows your name. Nobody owes you anything. Nobody is hunting you. "
            "You are perfectly, terrifyingly free."
        ),
        mentor_npc_id="ci_dock_master_tao",
        bloc_alignment="free_ports",
    ),

    CaptainType.BOUNTY_HUNTER: CaptainTemplate(
        id=CaptainType.BOUNTY_HUNTER,
        name="The Bounty Hunter",
        title="Licensed Hunter",
        description=(
            "Former port marshal turned freelance hunter. The Pact gave you a "
            "commission and a fast ship. Your job: track down contract-breakers, "
            "pirate captains, and anyone with a price on their head. The bounty "
            "board is your trade route. Combat is your cargo."
        ),
        home_region="North Atlantic",
        home_port_id="crosswind_isle",
        starting_silver=425,
        starting_ship_id="swift_cutter",
        starting_provisions=30,
        pricing=PricingModifiers(
            buy_price_mult=1.05,           # worse trader — combat focus
            sell_price_mult=0.98,
            luxury_sell_bonus=0.0,         # no luxury knowledge
            port_fee_mult=0.7,            # authority-aligned, cheaper fees
        ),
        voyage=VoyageModifiers(
            provision_burn=0.9,
            speed_bonus=0.5,              # fast pursuit ship
            storm_resist_bonus=0.05,
            cargo_damage_mult=1.0,
        ),
        inspection=InspectionProfile(
            inspection_chance_mult=0.6,    # authorities respect you
            seizure_risk=0.0,
            fine_mult=0.5,
        ),
        reputation_seed=ReputationSeed(
            commercial_trust=3,           # modest starting trust
            customs_heat=0,
            north_atlantic=8,
            mediterranean=3,
        ),
        strengths=[
            "Starts with a Cutter (fast pursuit vessel)",
            "Bounty board access — earn silver by defeating named pirates",
            "Nearly inspection-proof (authority commission)",
            "Low port fees at Pact-aligned ports",
            "Combat trust from day one",
        ],
        weaknesses=[
            "Poor trader — 5% markup on buys, 2% less on sells",
            "No luxury knowledge — no bonus on silk/spice/porcelain",
            "Iron Wolves and Crimson Tide may be hostile",
            "Must deliver bounties to earn — trade alone won't sustain you",
        ],
        backstory=(
            "You served five years as port marshal at Crosswind Isle, enforcing "
            "trade law and hunting smugglers through the archipelago. When the "
            "Pact needed someone to track down contract-breakers and rogue captains, "
            "you volunteered. They gave you a commission, a cutter, and a list of "
            "names. The bounty board is always full. The sea is full of people who "
            "owe debts they'd rather forget."
        ),
        mentor_npc_id="ci_dock_master_tao",
        bloc_alignment="northern_pact",
        faction_alignment={"northern_pact": 10},
    ),
}


# ---------------------------------------------------------------------------
# Selection screen metadata
# ---------------------------------------------------------------------------

# Ordered list for roster display (narrative arc: safe → risky → exotic → hard)
CAPTAIN_ORDER: list[CaptainType] = [
    CaptainType.MERCHANT,
    CaptainType.SMUGGLER,
    CaptainType.NAVIGATOR,
    CaptainType.PRIVATEER,
    CaptainType.CORSAIR,
    CaptainType.SCHOLAR,
    CaptainType.MERCHANT_PRINCE,
    CaptainType.DOCKHAND,
    CaptainType.BOUNTY_HUNTER,
]

# One-line personality hooks distilled from backstory
CAPTAIN_QUOTES: dict[CaptainType, str] = {
    CaptainType.MERCHANT:       "Your ledger is clean, your contracts are honored.",
    CaptainType.SMUGGLER:       "Rules are suggestions.",
    CaptainType.NAVIGATOR:      "Every horizon is an invitation.",
    CaptainType.PRIVATEER:      "The line between law and piracy is wherever Vogt draws it.",
    CaptainType.CORSAIR:        "The legitimate world doesn't want you. You don't want it back.",
    CaptainType.SCHOLAR:        "The wind told you to go.",
    CaptainType.MERCHANT_PRINCE: "They invested in you. They expect returns.",
    CaptainType.DOCKHAND:       "You are perfectly, terrifyingly free.",
    CaptainType.BOUNTY_HUNTER:  "The bounty board is always full.",
}

# Signature border color per captain
CAPTAIN_COLORS: dict[CaptainType, str] = {
    CaptainType.MERCHANT:       "green",
    CaptainType.SMUGGLER:       "magenta",
    CaptainType.NAVIGATOR:      "cyan",
    CaptainType.PRIVATEER:      "blue",
    CaptainType.CORSAIR:        "red",
    CaptainType.SCHOLAR:        "yellow",
    CaptainType.MERCHANT_PRINCE: "bright_green",
    CaptainType.DOCKHAND:       "white",
    CaptainType.BOUNTY_HUNTER:  "dark_orange",
}


def get_captain_template(captain_type: CaptainType) -> CaptainTemplate:
    """Get template for a captain type. Raises KeyError if unknown."""
    return CAPTAIN_TEMPLATES[captain_type]


# ---------------------------------------------------------------------------
# Authoritative effects reference — all captain identity modifiers in one place
# ---------------------------------------------------------------------------
# Scattered across: economy.py (pricing), voyage.py (voyage mods),
# reputation.py (inspection/trust), captain_identity.py (templates).
# This index exists so there's ONE place to audit what each type does.

CAPTAIN_EFFECTS_REFERENCE: dict[str, dict[str, str]] = {
    ct.value: {
        "home": CAPTAIN_TEMPLATES[ct].home_port_id,
        "silver": str(CAPTAIN_TEMPLATES[ct].starting_silver),
        "ship": CAPTAIN_TEMPLATES[ct].starting_ship_id,
        "bloc": CAPTAIN_TEMPLATES[ct].bloc_alignment or "none",
        "mentor": CAPTAIN_TEMPLATES[ct].mentor_npc_id or "none",
    }
    for ct in CaptainType
    if ct in CAPTAIN_TEMPLATES
}
