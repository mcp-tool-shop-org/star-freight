"""Star Freight content — the sci-fi world layer.

Every content unit proves at least one system truth:
- crew dependency
- combat consequence
- cultural logic
- investigation pressure

This replaces Portlight's maritime content. No medieval language,
no ocean references, no sailing terminology.

Slice scope: 5 stations, 8 lanes, 5 goods, 2 crew, 3 contracts, 3 ship classes.
Full scope: 20 stations, 40 lanes, 20 goods, 7 crew, 7+ contracts, 5 ship classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from portlight.engine.crew import (
    CrewMember,
    CrewRole,
    Civilization,
    LoyaltyTier,
    CrewStatus,
)
from portlight.engine.cultural_knowledge import (
    KethSeason,
)


# ---------------------------------------------------------------------------
# Stations
# ---------------------------------------------------------------------------

@dataclass
class StationService(str, Enum):
    """Services available at a station."""
    MARKET = "market"
    REPAIR = "repair"
    FUEL = "fuel"
    CREW_HIRE = "crew_hire"
    CONTRACTS = "contracts"
    SHIPYARD = "shipyard"
    BLACK_MARKET = "black_market"
    CULTURAL_EVENT = "cultural_event"


@dataclass
class Station:
    """A location in the Threshold.

    Every station proves at least one truth:
    - cultural: different social logic at each civ's station
    - economic: different goods, prices, services
    - crew: different recruitment options
    - investigation: different fragment sources
    """
    id: str
    name: str
    civilization: str                    # Civilization value
    description: str
    services: list[str] = field(default_factory=list)
    docking_fee: int = 10
    repair_cost_per_point: int = 2       # credits per hull point
    fuel_cost_per_day: int = 15          # credits per day of fuel

    # Cultural rules (proves cultural logic truth)
    cultural_greeting: str = ""          # what happens when you dock
    cultural_restriction: str = ""       # what you can't do here without knowledge
    cultural_opportunity: str = ""       # what opens with knowledge
    knowledge_required_for_restricted: int = 0  # level needed for restricted goods/areas

    # Market (proves economic truth)
    produces: list[str] = field(default_factory=list)  # good_ids this station exports (low price)
    demands: list[str] = field(default_factory=list)    # good_ids this station imports (high price)
    contraband: list[str] = field(default_factory=list) # good_ids illegal here

    # Investigation (proves plot truth)
    fragment_sources: list[str] = field(default_factory=list)  # fragment_ids discoverable here

    # Map position
    sector: str = ""
    x: int = 0
    y: int = 0


# --- Slice stations (1 per civilization) ---

SLICE_STATIONS: dict[str, Station] = {
    # Terran Compact — corporate trade hub
    "meridian_exchange": Station(
        id="meridian_exchange",
        name="Meridian Exchange",
        civilization="compact",
        description="The Compact's commercial face in the Threshold. Clean corridors, "
                    "regulated markets, bureaucratic friction. Your disgrace follows you here — "
                    "officials are cold, prices carry a surcharge, and military decks are off-limits.",
        services=["market", "repair", "fuel", "contracts", "shipyard"],
        docking_fee=25,
        repair_cost_per_point=3,
        fuel_cost_per_day=20,
        cultural_greeting="Automated docking clearance. Your file flags. An extra security scan.",
        cultural_restriction="Military contracts and premium cargo permits require rehabilitation.",
        cultural_opportunity="Cleared standing opens the most stable, highest-volume trade in the system.",
        knowledge_required_for_restricted=2,
        produces=["compact_alloys", "medical_supplies"],
        demands=["keth_biocrystal", "orryn_data"],
        contraband=["ancestor_tech", "reach_contraband"],
        fragment_sources=["med_dock_rumor"],
        sector="compact",
        x=2, y=3,
    ),

    # Keth Communion — seasonal market hub
    "communion_relay": Station(
        id="communion_relay",
        name="Communion Relay",
        civilization="keth",
        description="A living station — walls of grown coral-chitin, air thick with pheromone signals. "
                    "Trade here follows the biological calendar. During harvest, the market overflows. "
                    "During spawning, outsiders are confined to the outer ring.",
        services=["market", "repair", "fuel", "cultural_event", "crew_hire"],
        docking_fee=15,
        repair_cost_per_point=2,  # organic repair is cheaper
        fuel_cost_per_day=12,
        cultural_greeting="The docking elder tests your scent. Not hostile — curious.",
        cultural_restriction="Inner market access requires knowledge level 1. Spawning season "
                            "restricts all outsiders to outer ring regardless of standing.",
        cultural_opportunity="Harvest-season gifts can open elder council trade. Bio-crystal margins "
                            "peak during emergence when the Communion is generous.",
        knowledge_required_for_restricted=1,
        produces=["keth_biocrystal", "keth_organics"],
        demands=["compact_alloys", "veshan_minerals"],
        contraband=["keth_bioweapons"],
        fragment_sources=["med_price_anomaly", "med_seasonal_mismatch"],
        sector="keth",
        x=5, y=1,
    ),

    # Veshan Principalities — martial citadel
    "drashan_citadel": Station(
        id="drashan_citadel",
        name="Drashan Citadel",
        civilization="veshan",
        description="House Drashan's fortress-market. Every corridor echoes with the clang of "
                    "the training yards. Trade is conducted face-to-face, with eye contact, and "
                    "the Debt Ledger is displayed on the wall of the trade hall for all to see.",
        services=["market", "repair", "fuel", "contracts", "crew_hire"],
        docking_fee=20,
        repair_cost_per_point=2,
        fuel_cost_per_day=18,
        cultural_greeting="A Drashan guard meets you at the airlock. They size you up. "
                        "If you've fought recently, they nod. If not, they're unimpressed.",
        cultural_restriction="Weapons market restricted without house standing. Proxy war contracts "
                            "require Veshan knowledge level 2.",
        cultural_opportunity="Acknowledging the Debt Ledger publicly unlocks martial contracts. "
                            "Combat record opens House Drashan's respect — and their armory.",
        knowledge_required_for_restricted=1,
        produces=["veshan_weapons", "veshan_minerals"],
        demands=["keth_organics", "medical_supplies"],
        contraband=["unsealed_weapons"],
        fragment_sources=[],
        sector="veshan",
        x=7, y=4,
    ),

    # Orryn Drift — mobile broker haven
    "grand_drift": Station(
        id="grand_drift",
        name="Grand Drift",
        civilization="orryn",
        description="A station that moves. The Orryn Grand Drift orbits on a slow ellipse, "
                    "crossing trade lanes from every sector. Everyone comes here to deal — "
                    "but the Orryn take a cut of everything, and they remember who cut them out.",
        services=["market", "fuel", "contracts", "crew_hire", "black_market"],
        docking_fee=10,  # cheap — they make money on the spread
        repair_cost_per_point=4,  # expensive — they're brokers, not mechanics
        fuel_cost_per_day=10,
        cultural_greeting="An Orryn broker appears before your ramp is down. They already know "
                        "what you're carrying and what it's worth at three stations.",
        cultural_restriction="The Telling (Orryn negotiation ritual) requires knowledge level 1 "
                            "to attempt. Without it, you trade at their markup.",
        cultural_opportunity="The Telling at knowledge level 3 lets you frame truth for maximum "
                            "advantage. Orryn also broker intel — investigation fragments are for sale here.",
        knowledge_required_for_restricted=1,
        produces=["orryn_data", "orryn_brokered_goods"],
        demands=["compact_alloys", "veshan_weapons"],
        contraband=[],  # the Orryn don't restrict anything — everything is for sale
        fragment_sources=["med_intercepted_comms"],
        sector="orryn",
        x=4, y=5,
    ),

    # Sable Reach — pirate station
    "ironjaw_den": Station(
        id="ironjaw_den",
        name="Ironjaw Den",
        civilization="reach",
        description="The Ironjaw Syndicate's stronghold. Carved from a hollowed asteroid, "
                    "lit by stolen reactor glow. No law. No customs. No refunds. "
                    "The only rule: don't start what you can't finish.",
        services=["market", "repair", "fuel", "contracts", "black_market", "crew_hire"],
        docking_fee=5,  # cheap — they want you here
        repair_cost_per_point=1,  # cheapest repairs in the system (stolen parts)
        fuel_cost_per_day=8,
        cultural_greeting="Nobody greets you. A drone scans your hull. If you're armed, "
                        "it backs off. If not, someone will try to sell you a weapon before "
                        "you reach the market.",
        cultural_restriction="Faction dynamics are invisible without knowledge. At level 0, "
                            "you can't tell who's Ironjaw, who's Circuit, who's Cult.",
        cultural_opportunity="At knowledge level 2+, you can read faction tensions and play "
                            "them against each other. The Reach has the best bounty contracts "
                            "and the only Ancestor tech market.",
        knowledge_required_for_restricted=2,
        produces=["reach_contraband", "ancestor_tech"],
        demands=["medical_supplies", "keth_organics"],
        contraband=[],  # nothing is illegal here
        fragment_sources=["med_manifest"],
        sector="reach",
        x=1, y=6,
    ),
}


# ---------------------------------------------------------------------------
# Space lanes
# ---------------------------------------------------------------------------

@dataclass
class SpaceLane:
    """A navigable route between two stations.

    Every lane proves economic and tactical truth:
    - travel time creates opportunity cost
    - danger creates combat risk
    - faction control creates cultural/political risk
    """
    id: str
    station_a: str                       # station_id
    station_b: str                       # station_id
    distance_days: int                   # travel time
    danger: float                        # encounter chance per day (0.0-1.0)
    controlled_by: str                   # civilization that patrols this lane
    terrain: str = "open"                # open | asteroid_field | nebula | debris_field
    description: str = ""
    contraband_risk: float = 0.0         # chance of inspection per day


SLICE_LANES: dict[str, SpaceLane] = {
    # Compact ↔ Keth: safe trade corridor
    "meridian_communion": SpaceLane(
        id="meridian_communion",
        station_a="meridian_exchange",
        station_b="communion_relay",
        distance_days=3,
        danger=0.05,
        controlled_by="compact",
        description="The Compact-Keth trade corridor. Heavily patrolled, low risk, "
                    "low reward. Inspection chance if carrying Keth bioweapons.",
        contraband_risk=0.15,
    ),

    # Compact ↔ Veshan: tense border
    "meridian_drashan": SpaceLane(
        id="meridian_drashan",
        station_a="meridian_exchange",
        station_b="drashan_citadel",
        distance_days=4,
        danger=0.15,
        controlled_by="disputed",
        terrain="asteroid_field",
        description="The cold-war border. Compact and Veshan patrols both claim jurisdiction. "
                    "Asteroid fields provide cover — and ambush points.",
        contraband_risk=0.10,
    ),

    # Keth ↔ Veshan: uneasy trade
    "communion_drashan": SpaceLane(
        id="communion_drashan",
        station_a="communion_relay",
        station_b="drashan_citadel",
        distance_days=3,
        danger=0.10,
        controlled_by="veshan",
        description="Keth bio-goods flow to Veshan space along this route. Profitable but "
                    "politically loaded during disputes. Veshan patrols are honor-bound — "
                    "they challenge, not ambush.",
        contraband_risk=0.05,
    ),

    # Compact ↔ Orryn: tolerated
    "meridian_drift": SpaceLane(
        id="meridian_drift",
        station_a="meridian_exchange",
        station_b="grand_drift",
        distance_days=3,
        danger=0.08,
        controlled_by="orryn",
        description="The Compact tolerates the Orryn Drift's orbit through their space. "
                    "Low danger, moderate inspection risk — the Compact watches what "
                    "comes back from the Orryn.",
        contraband_risk=0.12,
    ),

    # Keth ↔ Orryn: friendly trade
    "communion_drift": SpaceLane(
        id="communion_drift",
        station_a="communion_relay",
        station_b="grand_drift",
        distance_days=2,
        danger=0.03,
        controlled_by="orryn",
        description="The safest lane in the system. Orryn and Keth respect each other's customs. "
                    "Low profit but a reliable fallback route.",
    ),

    # Veshan ↔ Reach: complicated
    "drashan_ironjaw": SpaceLane(
        id="drashan_ironjaw",
        station_a="drashan_citadel",
        station_b="ironjaw_den",
        distance_days=4,
        danger=0.25,
        controlled_by="reach",
        terrain="debris_field",
        description="Veshan houses hire Reach pirates as proxies. This lane is where those "
                    "contracts play out. Dangerous, profitable, politically explosive.",
    ),

    # Orryn ↔ Reach: business
    "drift_ironjaw": SpaceLane(
        id="drift_ironjaw",
        station_a="grand_drift",
        station_b="ironjaw_den",
        distance_days=3,
        danger=0.20,
        controlled_by="reach",
        terrain="nebula",
        description="The Orryn trade with everyone, including the Reach. Nebula cover "
                    "hides both parties from Compact surveillance. High danger, high margin.",
    ),

    # Compact ↔ Reach: hostile border
    "meridian_ironjaw": SpaceLane(
        id="meridian_ironjaw",
        station_a="meridian_exchange",
        station_b="ironjaw_den",
        distance_days=5,
        danger=0.30,
        controlled_by="disputed",
        terrain="asteroid_field",
        description="The smuggling run. The Compact enforces this border hard. "
                    "The Reach dares you to cross it. The most dangerous lane in the slice — "
                    "and the most profitable if you're carrying the right cargo.",
        contraband_risk=0.25,
    ),
}


# ---------------------------------------------------------------------------
# Trade goods
# ---------------------------------------------------------------------------

@dataclass
class TradeGood:
    """A tradeable commodity.

    Every good proves economic truth:
    - cultural goods require knowledge to access
    - contraband goods create risk
    - supply/demand creates route pressure
    """
    id: str
    name: str
    category: str                        # commodity | luxury | provision | contraband | military | tech
    base_price: int
    weight: float = 1.0
    origin_civ: str = ""                 # which civilization produces this
    cultural_restriction: str = ""       # knowledge requirement to buy
    contraband_in: list[str] = field(default_factory=list)  # civ_ids where this is illegal
    description: str = ""


SLICE_GOODS: dict[str, TradeGood] = {
    "compact_alloys": TradeGood(
        id="compact_alloys",
        name="Processed Alloys",
        category="commodity",
        base_price=80,
        origin_civ="compact",
        description="Standard industrial alloys. Every civilization needs them. Low margin, high volume.",
    ),
    "keth_biocrystal": TradeGood(
        id="keth_biocrystal",
        name="Keth Bio-Crystal",
        category="luxury",
        base_price=250,
        origin_civ="keth",
        cultural_restriction="Requires Keth knowledge level 1 to purchase at source.",
        description="Grown in Keth nurseries during harvest. Prized across the Threshold "
                    "for energy storage and medical applications. Culturally gated.",
    ),
    "keth_organics": TradeGood(
        id="keth_organics",
        name="Keth Organic Compounds",
        category="commodity",
        base_price=120,
        origin_civ="keth",
        description="Bio-engineered materials grown in Communion nurseries. Used in medicine, "
                    "food processing, and hull repair. Steady demand everywhere.",
    ),
    "veshan_weapons": TradeGood(
        id="veshan_weapons",
        name="Veshan Arms",
        category="military",
        base_price=200,
        origin_civ="veshan",
        cultural_restriction="Requires Veshan knowledge level 1 and house standing.",
        contraband_in=["compact"],
        description="House-sealed weaponry. Legal in Veshan space, contraband in Compact space "
                    "without a permit. High demand in the Reach.",
    ),
    "veshan_minerals": TradeGood(
        id="veshan_minerals",
        name="Deep-System Minerals",
        category="commodity",
        base_price=100,
        origin_civ="veshan",
        description="Rare minerals from Veshan deep-system mining operations. "
                    "Essential for alloy production and tech fabrication.",
    ),
    "orryn_data": TradeGood(
        id="orryn_data",
        name="Orryn Data Packages",
        category="luxury",
        base_price=180,
        origin_civ="orryn",
        description="Curated intelligence, market forecasts, and route analytics. "
                    "The Orryn trade in information. Valuable everywhere, "
                    "especially to the Compact's corporate sector.",
    ),
    "orryn_brokered_goods": TradeGood(
        id="orryn_brokered_goods",
        name="Brokered Goods",
        category="commodity",
        base_price=150,
        origin_civ="orryn",
        description="Cross-civilization goods bundled and certified by Orryn brokers. "
                    "Premium price, but they handle permits and customs. "
                    "Cutting out the Orryn saves money — at the cost of their goodwill.",
    ),
    "medical_supplies": TradeGood(
        id="medical_supplies",
        name="Medical Supplies",
        category="provision",
        base_price=60,
        description="Universal demand. Low margin but always needed. "
                    "Also the investigation trigger — medical cargo routed through Keth space "
                    "in off-season patterns is the first thread of the conspiracy.",
    ),
    "ancestor_tech": TradeGood(
        id="ancestor_tech",
        name="Ancestor Components",
        category="tech",
        base_price=500,
        origin_civ="reach",
        contraband_in=["compact", "keth"],
        cultural_restriction="Only available at Reach stations. Holding it generates "
                            "consequence engine events.",
        description="Salvaged technology from the extinct Ancestors. The most valuable "
                    "and most dangerous cargo in the system. Everyone wants it. "
                    "Carrying it makes you a target.",
    ),
    "reach_contraband": TradeGood(
        id="reach_contraband",
        name="Reach Salvage",
        category="contraband",
        base_price=300,
        origin_civ="reach",
        contraband_in=["compact"],
        description="Stripped components, unlicensed weapons, and questionable tech "
                    "from Reach operations. Illegal in Compact space, valuable everywhere else.",
    ),
    "keth_bioweapons": TradeGood(
        id="keth_bioweapons",
        name="Keth Bio-Agents",
        category="contraband",
        base_price=400,
        origin_civ="keth",
        contraband_in=["compact", "keth", "veshan"],
        cultural_restriction="The Communion considers these sacred — trafficking them is "
                            "a permanent reputation stain.",
        description="Weaponized biological compounds. The Communion outlaws their sale. "
                    "The Reach pays top price. Getting caught destroys Keth standing.",
    ),
    "unsealed_weapons": TradeGood(
        id="unsealed_weapons",
        name="Unsealed Arms",
        category="contraband",
        base_price=350,
        origin_civ="reach",
        contraband_in=["veshan"],
        description="Weapons without a Veshan house seal. Illegal in Veshan space — "
                    "carrying unsealed arms insults the houses. The Reach doesn't care.",
    ),
}


# ---------------------------------------------------------------------------
# Crew members (slice: 2)
# ---------------------------------------------------------------------------

def create_thal() -> CrewMember:
    """Thal — Keth engineer. Cultural bridge to the Communion.

    Proves:
    - Crew dependency: Thal is WHY you can access Keth markets
    - Cultural logic: Thal interprets seasonal protocols
    - Investigation: Thal's medical debt connects to the conspiracy
    - Combat: organic repair ability, ship repair skill
    """
    return CrewMember(
        id="thal_communion",
        name="Thal",
        civilization=Civilization.KETH,
        role=CrewRole.ENGINEER,
        hp=80,
        hp_max=80,
        speed=3,
        abilities=["organic_patch", "hull_bond", "keth_stabilize"],
        ship_skill="emergency_repair",
        morale=45,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=55,
        narrative_hooks=["keth_medical_debt", "communion_exile"],
        opinions={
            "violence": -5,
            "commerce": 3,
            "keth_customs": 8,
            "patience": 6,
            "deception": -7,
        },
    )


def create_varek() -> CrewMember:
    """Varek — Veshan gunner. Honor culture bridge.

    Proves:
    - Crew dependency: Varek is WHY you can navigate Veshan honor protocols
    - Cultural logic: Varek explains the Debt Ledger
    - Combat: heavy volley ability, gunner ship skill
    - Investigation: House Drashan connections
    """
    return CrewMember(
        id="varek_drashan",
        name="Varek",
        civilization=Civilization.VESHAN,
        role=CrewRole.GUNNER,
        hp=120,
        hp_max=120,
        speed=2,
        abilities=["aimed_shot", "suppressive_fire", "honor_strike"],
        ship_skill="heavy_volley",
        morale=50,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=70,
        narrative_hooks=["house_drashan_exile", "veshan_honor_debt"],
        opinions={
            "honor": 10,
            "directness": 8,
            "deception": -10,
            "cowardice": -8,
            "keth_customs": -2,
        },
    )


# ---------------------------------------------------------------------------
# Contract types (slice: 3)
# ---------------------------------------------------------------------------

@dataclass
class ContractTemplate:
    """A contract shape that generates specific job instances.

    Every contract proves at least one truth:
    - economic pressure
    - route choice
    - faction consequence
    - cultural engagement
    """
    id: str
    name: str
    family: str                          # delivery | escort | faction
    description: str
    payout_range: tuple[int, int]        # (min, max) credits
    deadline_days: int
    reputation_required: dict[str, int] = field(default_factory=dict)  # faction → min standing
    cultural_knowledge_required: dict[str, int] = field(default_factory=dict)  # civ → min level
    risk_type: str = "economic"          # economic | combat | political
    consequence_on_success: str = ""
    consequence_on_failure: str = ""
    proves: str = ""                     # which system truth this contract proves


SLICE_CONTRACTS: dict[str, ContractTemplate] = {
    "standard_delivery": ContractTemplate(
        id="standard_delivery",
        name="Standard Delivery",
        family="delivery",
        description="Haul cargo from A to B within deadline. The bread and butter. "
                    "Low risk, predictable payout, keeps the lights on.",
        payout_range=(100, 300),
        deadline_days=10,
        risk_type="economic",
        consequence_on_success="reputation_minor_positive",
        consequence_on_failure="reputation_minor_negative",
        proves="economic pressure — these keep you alive but don't make you rich",
    ),

    "cultural_cargo": ContractTemplate(
        id="cultural_cargo",
        name="Cultural Cargo Run",
        family="delivery",
        description="Deliver culturally sensitive goods. Higher payout but requires "
                    "cultural knowledge to avoid missteps at the destination. "
                    "A Keth bio-crystal shipment during dormancy requires knowing "
                    "not to push the delivery schedule.",
        payout_range=(250, 600),
        deadline_days=8,
        cultural_knowledge_required={"keth": 1},
        risk_type="political",
        consequence_on_success="reputation_cultural_positive",
        consequence_on_failure="reputation_cultural_negative",
        proves="cultural logic — knowledge changes the risk shape of the same cargo",
    ),

    "bounty_contract": ContractTemplate(
        id="bounty_contract",
        name="Bounty Hunt",
        family="faction",
        description="Track and engage a target. Could be a pirate, a smuggler, or "
                    "someone who defaulted on a Veshan debt. Combat is expected. "
                    "Crew composition determines whether you can even find the target.",
        payout_range=(400, 1000),
        deadline_days=15,
        reputation_required={"reach": -25},  # can't be too friendly with pirates
        risk_type="combat",
        consequence_on_success="reputation_combat_positive",
        consequence_on_failure="reputation_combat_negative",
        proves="combat consequence + crew dependency — who you bring determines "
               "what you can do when you find the target",
    ),
}


# ---------------------------------------------------------------------------
# Ship classes (replacing sailing ships)
# ---------------------------------------------------------------------------

@dataclass
class ShipClass:
    """A purchasable ship type.

    Replaces Portlight's sloop/cutter/brigantine/galleon/man_of_war.
    """
    id: str
    name: str
    tier: int                            # 1-5
    hull_max: int
    shield_max: int
    cargo_capacity: int
    speed: int                           # tiles per move in combat
    crew_quarters: int                   # quality tier 1-3
    weapon_power: int
    price: int
    description: str


SLICE_SHIPS: dict[str, ShipClass] = {
    "hauler": ShipClass(
        id="hauler",
        name="Threshold Hauler",
        tier=1,
        hull_max=2000,
        shield_max=250,
        cargo_capacity=8,
        speed=2,
        crew_quarters=1,
        weapon_power=100,
        price=0,  # starting ship
        description="Your starting ship. Functional, embarrassing, "
                    "and exactly what a disgraced pilot deserves.",
    ),
    "runner": ShipClass(
        id="runner",
        name="Orryn Runner",
        tier=2,
        hull_max=2500,
        shield_max=400,
        cargo_capacity=6,
        speed=3,
        crew_quarters=2,
        weapon_power=150,
        price=3000,
        description="Fast, light, and designed for evasion. "
                    "The Orryn build these for their own use — and sell the surplus.",
    ),
    "warbird": ShipClass(
        id="warbird",
        name="Veshan Warbird",
        tier=3,
        hull_max=5000,
        shield_max=600,
        cargo_capacity=5,
        speed=2,
        crew_quarters=2,
        weapon_power=300,
        price=8000,
        description="House Drashan's workhorse. Slow, heavily armed, built to close and hit hard. "
                    "Buying one from the Veshan requires standing — they don't sell to strangers.",
    ),
}


# ---------------------------------------------------------------------------
# Encounter archetypes
# ---------------------------------------------------------------------------

@dataclass
class EncounterArchetype:
    """A template for generating combat encounters.

    Every archetype proves combat and cultural truth:
    - who attacks and why
    - what cultural knowledge changes
    - what crew composition enables
    """
    id: str
    name: str
    civilization: str
    description: str
    ship_hull: int
    ship_shield: int
    ship_damage: int
    ship_speed: int
    behavior: str                        # aggressive | defensive | honor | swarm
    cultural_option: str = ""            # what cultural knowledge enables
    retreat_consequence: str = ""
    victory_consequence: str = ""
    defeat_consequence: str = ""


SLICE_ENCOUNTERS: dict[str, EncounterArchetype] = {
    "compact_patrol": EncounterArchetype(
        id="compact_patrol",
        name="Compact Patrol Interdiction",
        civilization="compact",
        description="A Compact patrol stops you for inspection. If you're carrying contraband, "
                    "this becomes a fight. If not, it's a reputation check.",
        ship_hull=3000,
        ship_shield=500,
        ship_damage=150,
        ship_speed=2,
        behavior="defensive",
        cultural_option="Compact knowledge level 2: present permits to avoid inspection entirely.",
        retreat_consequence="Fleeing a Compact patrol = wanted status. Compact standing drops hard.",
        victory_consequence="Defeating a patrol is pirate territory. Reach standing up, Compact down.",
        defeat_consequence="Cargo confiscated. Credits fined. Ship impounded temporarily.",
    ),

    "reach_pirate": EncounterArchetype(
        id="reach_pirate",
        name="Reach Pirate Ambush",
        civilization="reach",
        description="A Reach pirate attacks for your cargo. No negotiation without knowledge. "
                    "With knowledge, you might buy them off or invoke faction politics.",
        ship_hull=1500,
        ship_shield=200,
        ship_damage=180,
        ship_speed=3,
        behavior="aggressive",
        cultural_option="Reach knowledge level 1: identify their faction. Level 2: negotiate or bluff.",
        retreat_consequence="Jettison cargo to escape. Morale hit. Route marked as dangerous.",
        victory_consequence="Salvage credits. Reach reputation complex — some factions respect it.",
        defeat_consequence="All cargo seized. Ship damaged. Crew injuries likely.",
    ),

    "veshan_challenge": EncounterArchetype(
        id="veshan_challenge",
        name="Veshan Honor Challenge",
        civilization="veshan",
        description="A Veshan warrior challenges you. Refusing is catastrophic for Veshan standing. "
                    "Accepting is dangerous but earns respect. Debt Ledger may apply.",
        ship_hull=4000,
        ship_shield=300,
        ship_damage=250,
        ship_speed=2,
        behavior="honor",
        cultural_option="Veshan knowledge level 1: understand the challenge terms. "
                       "Level 2: invoke debt or formal honor greeting to shift terms.",
        retreat_consequence="Refused challenge = permanent Veshan dishonor. -15 standing all houses.",
        victory_consequence="Major respect. +5 Veshan standing. Possible debt created in your favor.",
        defeat_consequence="Respectful defeat. Minor standing loss. Cargo and ship intact if fought honorably.",
    ),
}


# ---------------------------------------------------------------------------
# Content validation helpers
# ---------------------------------------------------------------------------

def validate_slice_content() -> list[str]:
    """Validate that all slice content is internally consistent.

    Returns list of errors. Empty list = valid.
    """
    errors = []

    # All lane endpoints must be valid stations
    for lane_id, lane in SLICE_LANES.items():
        if lane.station_a not in SLICE_STATIONS:
            errors.append(f"Lane {lane_id}: station_a '{lane.station_a}' not found")
        if lane.station_b not in SLICE_STATIONS:
            errors.append(f"Lane {lane_id}: station_b '{lane.station_b}' not found")

    # All station produces/demands must be valid goods
    for station_id, station in SLICE_STATIONS.items():
        for good_id in station.produces + station.demands:
            if good_id not in SLICE_GOODS:
                errors.append(f"Station {station_id}: good '{good_id}' not found")

    # Each civ must have exactly 1 station in slice
    civs = [s.civilization for s in SLICE_STATIONS.values()]
    for civ in ["compact", "keth", "veshan", "orryn", "reach"]:
        count = civs.count(civ)
        if count != 1:
            errors.append(f"Civ {civ}: expected 1 station, got {count}")

    # Each station must have at least 1 produce and 1 demand
    for station_id, station in SLICE_STATIONS.items():
        if not station.produces:
            errors.append(f"Station {station_id}: no produces defined")
        if not station.demands:
            errors.append(f"Station {station_id}: no demands defined")

    # Lanes must connect to form a navigable graph (all stations reachable)
    connected = set()
    if SLICE_STATIONS:
        start = next(iter(SLICE_STATIONS))
        _flood_fill(start, SLICE_LANES, connected)
        for station_id in SLICE_STATIONS:
            if station_id not in connected:
                errors.append(f"Station {station_id}: not reachable from {start}")

    return errors


def _flood_fill(start: str, lanes: dict[str, SpaceLane], visited: set) -> None:
    """BFS to check graph connectivity."""
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for lane in lanes.values():
            if lane.station_a == current and lane.station_b not in visited:
                queue.append(lane.station_b)
            elif lane.station_b == current and lane.station_a not in visited:
                queue.append(lane.station_a)
