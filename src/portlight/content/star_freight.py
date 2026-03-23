"""Star Freight content — the sci-fi world layer.

Every content unit proves at least one system truth:
- crew dependency
- combat consequence
- cultural logic
- investigation pressure

This replaces Portlight's maritime content. No medieval language,
no ocean references, no sailing terminology.

Slice scope: 5 stations, 8 lanes, 5 goods, 2 crew, 3 contracts, 3 ship classes.
7A Working Lives: +1 station, +2 lanes, +2 goods, +1 crew, +2 contracts, +1 encounter, +1 thread.
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
        docking_fee=10,
        repair_cost_per_point=3,
        fuel_cost_per_day=12,
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
        docking_fee=5,
        repair_cost_per_point=2,  # organic repair is cheaper
        fuel_cost_per_day=8,
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
        docking_fee=10,
        repair_cost_per_point=2,
        fuel_cost_per_day=12,
        cultural_greeting="A Drashan guard meets you at the airlock. They size you up. "
                        "If you've fought recently, they nod. If not, they're unimpressed.",
        cultural_restriction="Weapons market restricted without house standing. Proxy war contracts "
                            "require Veshan knowledge level 2.",
        cultural_opportunity="Acknowledging the Debt Ledger publicly unlocks martial contracts. "
                            "Combat record opens House Drashan's respect — and their armory.",
        knowledge_required_for_restricted=1,
        produces=["veshan_weapons", "veshan_minerals", "black_seal_resin"],
        demands=["keth_organics", "medical_supplies", "orryn_brokered_goods"],
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
        docking_fee=5,  # cheap — they make money on the spread
        repair_cost_per_point=4,  # expensive — they're brokers, not mechanics
        fuel_cost_per_day=8,
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
        docking_fee=3,  # cheap — they want you here
        repair_cost_per_point=1,  # cheapest repairs in the system (stolen parts)
        fuel_cost_per_day=5,
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
        demands=["medical_supplies", "keth_organics", "black_seal_resin"],
        contraband=[],  # nothing is illegal here
        fragment_sources=["med_manifest"],
        sector="reach",
        x=1, y=6,
    ),

    # --- 7A: Working Lives ---

    "mourning_quay": Station(
        id="mourning_quay",
        name="Mourning Quay",
        civilization="keth",
        description="A hospice-port grown from living coral around a thermal vent. Ships arrive "
                    "damaged, crews arrive grieving, and commerce moves at the pace of recovery. "
                    "The market trades in harvest compounds, brood-silk, and memory tinctures — "
                    "goods that carry emotional weight the Communion takes seriously.",
        services=["market", "repair", "fuel", "cultural_event", "crew_hire"],
        docking_fee=5,
        repair_cost_per_point=1,  # cheapest repair in the system — care is the point
        fuel_cost_per_day=6,
        cultural_greeting="A healer-drone approaches your airlock before you've powered down. "
                        "It checks your hull scars, not your cargo manifest.",
        cultural_restriction="Impatient trading worsens prices. Pushing deals during convalescence "
                            "rituals is treated as cruelty, not rudeness. Inner hospice requires "
                            "Keth knowledge level 2.",
        cultural_opportunity="Patient captains who honor the cadence earn trust that opens elder "
                            "council markets. Injured crew recover faster here. Gifts of medical "
                            "supplies during harvest carry triple weight.",
        knowledge_required_for_restricted=2,
        produces=["keth_organics", "brood_silk"],
        demands=["compact_alloys", "medical_supplies"],
        contraband=["keth_bioweapons", "ancestor_tech"],
        fragment_sources=["ghost_tonnage_shortage", "med_seasonal_mismatch"],
        sector="keth",
        x=6, y=0,
    ),

    # --- 7B: Houses, Audits, and Seizures ---

    "registry_spindle": Station(
        id="registry_spindle",
        name="Registry Spindle",
        civilization="compact",
        description="Not a market. A jurisdiction. The Compact's administrative nerve center "
                    "where manifests are reconciled, claims are filed, emergency liens are "
                    "issued, and delayed cargo becomes political. Everything here is recorded. "
                    "Sloppy captains feel small. Prepared captains feel powerful.",
        services=["market", "fuel", "contracts"],
        docking_fee=12,  # administrative overhead
        repair_cost_per_point=4,  # expensive — this is not a shipyard
        fuel_cost_per_day=15,
        cultural_greeting="Automated docking. Your ship ID is logged before you're through the "
                        "airlock. A registry clerk appears with a manifest reconciliation request "
                        "before you've asked for anything.",
        cultural_restriction="Without Compact knowledge level 2, you cannot file or contest claims. "
                            "Without proper seals, bonded freight is flagged for hold. "
                            "Unresolved liens from any Compact station are enforced here.",
        cultural_opportunity="Sera or Nera crew make this station navigable. With the right documents, "
                            "you can clear liens, file counter-claims, establish bonded freight status, "
                            "or access priority contracts that pay well for legitimate captains.",
        knowledge_required_for_restricted=2,
        produces=["bond_plate", "compact_alloys"],
        demands=["reserve_grain", "medical_supplies"],
        contraband=["ancestor_tech", "reach_contraband", "unsealed_weapons", "keth_bioweapons"],
        fragment_sources=["paper_fleet_registry_flag"],
        sector="compact",
        x=3, y=2,
    ),

    # --- 7C: Shortages, Sanctions, and Convoys ---

    "queue_of_flags": Station(
        id="queue_of_flags",
        name="Queue of Flags",
        civilization="orryn",
        description="A relief-choked transfer port where ships wait under ration priority, "
                    "convoy assignment, and public shortage scrutiny. The Orryn manage it "
                    "because nobody trusts anyone else to be neutral. Every docking bay "
                    "has a queue number. Every queue number has a politics.",
        services=["market", "fuel", "contracts", "crew_hire"],
        docking_fee=8,
        repair_cost_per_point=3,
        fuel_cost_per_day=15,  # scarcity premium
        cultural_greeting="A queue drone assigns you a number. The display board shows "
                        "seventeen ships ahead of you. Some have been here for days. "
                        "The Orryn scheduler glances at your manifest before your hold.",
        cultural_restriction="Priority access requires Orryn knowledge level 1 or active relief "
                            "contract. Without it, you wait. Jumping queue is socially visible "
                            "and remembered by every captain watching.",
        cultural_opportunity="Ilen crew unlocks convoy scheduling insight. The Telling can be "
                            "used to negotiate priority. Relief contractors get immediate access "
                            "and better fuel rates.",
        knowledge_required_for_restricted=1,
        produces=["orryn_data", "orryn_brokered_goods"],
        demands=["ration_grain", "medical_supplies", "coolant_ampoules", "bond_plate"],
        contraband=["ancestor_tech"],
        fragment_sources=["dry_ledger_queue_delay"],
        sector="orryn",
        x=3, y=6,
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

    # --- 7A: Working Lives ---

    "pilgrims_ribbon": SpaceLane(
        id="pilgrims_ribbon",
        station_a="communion_relay",
        station_b="mourning_quay",
        distance_days=2,
        danger=0.02,
        controlled_by="keth",
        description="A ceremonial lane used by families, shrine delegations, and memorial "
                    "caravans. Safe, slow, and socially scrutinized. Fighting here carries "
                    "heavy long-tail consequences. Contraband is conspicuous.",
        contraband_risk=0.20,  # high scrutiny despite low danger
    ),

    "cinder_span": SpaceLane(
        id="cinder_span",
        station_a="drashan_citadel",
        station_b="mourning_quay",
        distance_days=3,
        danger=0.22,
        controlled_by="disputed",
        terrain="debris_field",
        description="A broken mineral lane full of debris shadow, salvage traps, and "
                    "opportunistic raiders. Faster than safe routes but hull-punishing. "
                    "Good for smuggling, salvage, and people who don't want to be found.",
        contraband_risk=0.03,  # low scrutiny — nobody's watching
    ),

    # --- 7B: Houses, Audits, and Seizures ---

    "white_corridor": SpaceLane(
        id="white_corridor",
        station_a="meridian_exchange",
        station_b="registry_spindle",
        distance_days=2,
        danger=0.02,
        controlled_by="compact",
        description="The priority route. Bonded freight, official delegations, and high-legitimacy "
                    "movement. Safer from pirates. Riskier for contraband, false manifests, or "
                    "unresolved claims. The danger here is being seen too clearly.",
        contraband_risk=0.30,  # highest inspection rate in the system
    ),

    "grain_eclipse": SpaceLane(
        id="grain_eclipse",
        station_a="registry_spindle",
        station_b="communion_relay",
        distance_days=3,
        danger=0.12,
        controlled_by="disputed",
        terrain="nebula",
        description="A semi-legal bypass used during shortages, sanctions, and unofficial "
                    "redistribution. Tempting margin. Ambiguous legitimacy. The danger is not "
                    "piracy alone — it's being caught between competing legal narratives about "
                    "who authorized what.",
        contraband_risk=0.08,
    ),

    # --- 7C: Shortages, Sanctions, and Convoys ---

    "mercy_track": SpaceLane(
        id="mercy_track",
        station_a="queue_of_flags",
        station_b="communion_relay",
        distance_days=2,
        danger=0.01,
        controlled_by="orryn",
        description="A convoy-protected relief lane. Orryn escorts and Keth medical drones "
                    "patrol it. Almost no pirate risk. Heavy schedule rigidity — you move "
                    "when the convoy moves. Contraband is suicidal here. Every hold is scanned.",
        contraband_risk=0.35,  # highest in the system
    ),

    "red_wake": SpaceLane(
        id="red_wake",
        station_a="queue_of_flags",
        station_b="ironjaw_den",
        distance_days=3,
        danger=0.25,
        controlled_by="reach",
        terrain="debris_field",
        description="An improvised bypass used by opportunists, smugglers, and captains "
                    "moving sanctioned goods under cover of shortage chaos. Not officially "
                    "a lane. Everyone knows it exists. Nobody polices it. The danger is "
                    "other captains with the same idea and fewer scruples.",
        contraband_risk=0.01,  # nobody watching
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

    # --- 7A: Working Lives ---

    "brood_silk": TradeGood(
        id="brood_silk",
        name="Brood Silk",
        category="luxury",
        base_price=220,
        origin_civ="keth",
        cultural_restriction="Requires Keth knowledge level 1. Mishandling or reselling at "
                            "non-Keth stations without context is remembered.",
        description="Keth ceremonial and medical textile grown from larval secretions. "
                    "Used in healing wraps, mourning shrouds, and kinship gifts. "
                    "Profitable but socially loaded — gifting it well earns deep trust, "
                    "selling it carelessly earns lasting contempt.",
    ),
    "black_seal_resin": TradeGood(
        id="black_seal_resin",
        name="Black Seal Resin",
        category="luxury",
        base_price=280,
        origin_civ="veshan",
        cultural_restriction="Requires Veshan knowledge level 1. Selling to non-Veshan buyers "
                            "without house authorization is a political act.",
        description="Veshan contract resin used in oath-marking, military maintenance, and "
                    "high-status house work. Buyers pay for status, not volume. Diverted "
                    "resin may imply military preparation or false-house operations.",
    ),

    # --- 7B: Houses, Audits, and Seizures ---

    "bond_plate": TradeGood(
        id="bond_plate",
        name="Bond Plate",
        category="commodity",
        base_price=90,
        origin_civ="compact",
        description="A legal certification plate embedded in bonded freight. Without it, "
                    "sensitive cargo is flagged at every Compact checkpoint. With it, you move "
                    "faster — but the plate is registered, tracked, and revocable. "
                    "Legitimacy made portable.",
    ),
    "reserve_grain": TradeGood(
        id="reserve_grain",
        name="Reserve Grain",
        category="provision",
        base_price=70,
        description="Politically sensitive relief cargo whose value changes with shortage, "
                    "standing, and route legitimacy. Not technically contraband anywhere, "
                    "but moving it during a shortage without authorization draws scrutiny. "
                    "Moving it with authorization during a shortage is incredibly profitable.",
    ),

    # --- 7C: Shortages, Sanctions, and Convoys ---

    "ration_grain": TradeGood(
        id="ration_grain",
        name="Ration Grain",
        category="provision",
        base_price=45,
        description="Basic survival cargo. Low base price, high political volatility. "
                    "During shortages, demand spikes and everyone watches who moves it. "
                    "Late delivery is worse than damaged delivery. Carrying it marks you "
                    "as either a relief worker or a profiteer — the difference depends on "
                    "who's asking.",
    ),
    "coolant_ampoules": TradeGood(
        id="coolant_ampoules",
        name="Coolant Ampoules",
        category="commodity",
        base_price=130,
        description="Critical infrastructure and medical cooling supply. Reactor maintenance, "
                    "bio-storage, and surgical cooling all depend on these. Shortages cascade: "
                    "stations without coolant shut down medical bays and reactor cycling. "
                    "Carrying them during a shortage changes your convoy priority and route value.",
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
        pay_rate=35,
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
        pay_rate=45,
        narrative_hooks=["house_drashan_exile", "veshan_honor_debt"],
        opinions={
            "honor": 10,
            "directness": 8,
            "deception": -10,
            "cowardice": -8,
            "keth_customs": -2,
        },
    )


# --- 7A: Working Lives ---

def create_sera() -> CrewMember:
    """Sera Vale — Compact quartermaster. Document expert and legal finesse.

    Proves:
    - Crew dependency: Sera is WHY you can read manifests and navigate customs
    - Cultural logic: Compact interactions become tactical instead of blunt
    - Investigation: opens document-based angles (Ghost Tonnage thread)
    - Combat: manifest scrub ability reduces scan exposure
    """
    return CrewMember(
        id="sera_vale",
        name="Sera",
        civilization=Civilization.COMPACT,
        role=CrewRole.BROKER,
        hp=70,
        hp_max=70,
        speed=2,
        abilities=["manifest_audit", "customs_protocol", "document_forge"],
        ship_skill="manifest_scrub",
        morale=50,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=40,
        narrative_hooks=["buried_ledger", "former_employer"],
        opinions={
            "honesty": 6,
            "carelessness": -8,
            "deception": -4,
            "professionalism": 7,
            "violence": -3,
        },
    )


# --- 7B: Houses, Audits, and Seizures ---

def create_nera() -> CrewMember:
    """Nera Quill — former house registrar. Institutional violence expert.

    Different from Sera: Sera is cargo law and manifest intelligence.
    Nera is institutional power in polite language. She knows how
    claims are filed, how seizures are authorized, how liens are
    weaponized, and how legitimate disappearance is documented.

    Proves:
    - Crew dependency: Nera is WHY you can parse or resist administrative coercion
    - Cultural logic: Compact interactions become about legitimacy, not just permits
    - Investigation: opens Paper Fleet thread (institutional disappearance)
    - Combat: Claim Freeze ability can delay or prevent seizures
    """
    return CrewMember(
        id="nera_quill",
        name="Nera",
        civilization=Civilization.COMPACT,
        role=CrewRole.FACE,
        hp=60,
        hp_max=60,
        speed=2,
        abilities=["claim_review", "seal_authentication", "lien_challenge"],
        ship_skill="claim_freeze",
        morale=55,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=50,  # expensive — institutional knowledge costs
        narrative_hooks=["falsified_seizure", "registry_ghost"],
        opinions={
            "precision": 9,
            "improvisation": -7,
            "carelessness": -9,
            "institutional_respect": 5,
            "violence": -4,
        },
    )


# --- 7C: Shortages, Sanctions, and Convoys ---

def create_ilen() -> CrewMember:
    """Ilen Marr — convoy scheduler and supply politics expert.

    Different from Sera (cargo law) and Nera (institutional power).
    Ilen understands supply politics: ration priority, emergency allotment
    logic, convoy scheduling, and who quietly gets rerouted around the rules.

    Proves:
    - Crew dependency: Ilen is WHY you can read convoy priority and supply politics
    - Cultural logic: Orryn logistics culture becomes navigable, not opaque
    - Investigation: opens Dry Ledger thread (manufactured scarcity)
    - Economy: changes what the player understands about shortage pricing
    """
    return CrewMember(
        id="ilen_marr",
        name="Ilen",
        civilization=Civilization.ORRYN,
        role=CrewRole.TECH,
        hp=65,
        hp_max=65,
        speed=3,
        abilities=["priority_read", "convoy_schedule", "shortage_forecast"],
        ship_skill="priority_override",
        morale=50,
        loyalty_tier=LoyaltyTier.STRANGER,
        loyalty_points=0,
        pay_rate=38,
        narrative_hooks=["supply_chain_guilt", "convoy_reroute_secret"],
        opinions={
            "fairness": 7,
            "profiteering": -8,
            "efficiency": 6,
            "waste": -6,
            "orryn_customs": 5,
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

    # --- 7A: Working Lives ---

    "witness_run": ContractTemplate(
        id="witness_run",
        name="Witness Run",
        family="escort",
        description="Transport a neutral observer to a disputed station or lane crossing. "
                    "Modest payout but high reputation leverage. Different civilizations "
                    "interpret 'neutral witness' differently. The witness may notice "
                    "something they should not.",
        payout_range=(150, 350),
        deadline_days=7,
        risk_type="political",
        consequence_on_success="reputation_diplomatic_positive",
        consequence_on_failure="reputation_diplomatic_catastrophe",
        proves="culture + plot — witness presence changes encounter grammar, "
               "observer may branch into investigation",
    ),

    "cold_lantern_freight": ContractTemplate(
        id="cold_lantern_freight",
        name="Cold Lantern Freight",
        family="delivery",
        description="Deliver fragile mourning lamps or memory vessels before a seasonal "
                    "observance closes. Time-pressured sacred cargo. Mishandling is worse "
                    "than normal failure — it's social catastrophe. Keth or culturally "
                    "adjacent crew improve outcomes.",
        payout_range=(200, 450),
        deadline_days=5,
        cultural_knowledge_required={"keth": 1},
        risk_type="political",
        consequence_on_success="reputation_sacred_positive",
        consequence_on_failure="reputation_sacred_catastrophe",
        proves="culture + economy — time pressure meets cultural obligation, "
               "crew changes whether sacred cargo survives the run",
    ),

    # --- 7B: Houses, Audits, and Seizures ---

    "bonded_relief_run": ContractTemplate(
        id="bonded_relief_run",
        name="Bonded Relief Run",
        family="delivery",
        description="Move shortage-sensitive supplies under partial immunity, but only if "
                    "delivered under seal and on time. Looks safe. Is actually full of "
                    "administrative fragility. One delay turns protected cargo into contested "
                    "cargo. One broken seal turns legitimacy into liability.",
        payout_range=(300, 600),
        deadline_days=6,
        reputation_required={"compact": 0},
        risk_type="political",
        consequence_on_success="reputation_bonded_positive",
        consequence_on_failure="reputation_bonded_violation",
        proves="economy + culture — administrative fragility creates drama from timing, "
               "not combat. Bond Plate cargo + deadline + seal integrity = real pressure",
    ),

    "claim_courier": ContractTemplate(
        id="claim_courier",
        name="Claim Courier",
        family="delivery",
        description="Deliver a sealed legal claim to a station before a rival filing lands. "
                    "The cargo is paper, not bulk. The stakes are enormous anyway. "
                    "Arrival order matters. Combat, delay, or cultural offense can alter "
                    "which claim becomes 'truth.' Nera Quill crew makes this dramatically safer.",
        payout_range=(350, 800),
        deadline_days=4,
        reputation_required={"compact": -10},  # even disgraced captains can courier claims
        risk_type="political",
        consequence_on_success="reputation_claim_filed",
        consequence_on_failure="reputation_claim_lost",
        proves="plot + economy — legal claims change who owns what. Late delivery means "
               "the wrong truth becomes official. Nera crew dependency is critical.",
    ),

    # --- 7C: Shortages, Sanctions, and Convoys ---

    "priority_relief": ContractTemplate(
        id="priority_relief",
        name="Priority Relief",
        family="delivery",
        description="Deliver ration-critical cargo under time pressure where lateness is "
                    "worse than damage. Convoy priority if you have it. Queue waiting if you "
                    "don't. Ilen crew makes scheduling navigable. Without supply politics "
                    "knowledge, you're guessing which lane and which timing won't strand you.",
        payout_range=(250, 500),
        deadline_days=4,
        risk_type="economic",
        consequence_on_success="reputation_relief_positive",
        consequence_on_failure="reputation_relief_failure",
        proves="economy + crew — time pressure meets supply politics. Ilen changes whether "
               "the deadline is survivable or a trap.",
    ),

    "embargo_slip": ContractTemplate(
        id="embargo_slip",
        name="Embargo Slip",
        family="delivery",
        description="Move something technically forbidden but socially necessary. The moral "
                    "case and the legal case diverge. A station needs coolant ampoules but "
                    "the embargo says no. Somebody hired you to make it happen anyway. "
                    "If caught: legal consequence. If completed: lives saved, standing complex.",
        payout_range=(400, 900),
        deadline_days=6,
        risk_type="political",
        consequence_on_success="reputation_embargo_delivered",
        consequence_on_failure="reputation_embargo_caught",
        proves="culture + economy + plot — the moral and legal cases diverge. "
               "Every system truth is in tension: crew interprets differently, "
               "combat changes if caught, cultural standing shifts unpredictably.",
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
        ship_hull=1200,
        ship_shield=200,
        ship_damage=120,
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
        ship_hull=800,
        ship_shield=100,
        ship_damage=130,
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
        ship_hull=1500,
        ship_shield=200,
        ship_damage=150,
        ship_speed=2,
        behavior="honor",
        cultural_option="Veshan knowledge level 1: understand the challenge terms. "
                       "Level 2: invoke debt or formal honor greeting to shift terms.",
        retreat_consequence="Refused challenge = permanent Veshan dishonor. -15 standing all houses.",
        victory_consequence="Major respect. +5 Veshan standing. Possible debt created in your favor.",
        defeat_consequence="Respectful defeat. Minor standing loss. Cargo and ship intact if fought honorably.",
    ),

    # --- 7A: Working Lives ---

    "hearth_right": EncounterArchetype(
        id="hearth_right",
        name="Hearth Right Challenge",
        civilization="veshan",
        description="A Veshan house escort accuses you of lane disrespect or improper passage. "
                    "This is not piracy — it is status, witness, insult, and expectation. "
                    "Can become duel, skirmish, negotiated withdrawal, or disaster depending "
                    "on cultural knowledge and crew.",
        ship_hull=1300,
        ship_shield=200,
        ship_damage=140,
        ship_speed=2,
        behavior="honor",
        cultural_option="Veshan knowledge level 1: understand the accusation terms. "
                       "Level 2: invoke witness protocol or offer formal compensation. "
                       "Veshan crew member can open honor-preserving resolution.",
        retreat_consequence="Short-term survival, long-term social damage. -10 Veshan standing. "
                          "Lane passage rights questioned at future crossings.",
        victory_consequence="Honor standing up. +3 Veshan standing. May create debt in your favor. "
                          "But wider faction heat possible if the house has allies.",
        defeat_consequence="Respectful if fought well — minor standing loss. If fled mid-fight, "
                         "treated as cowardice. Cargo may be claimed as 'compensation.'",
    ),

    # --- 7B: Houses, Audits, and Seizures ---

    "seizure_notice": EncounterArchetype(
        id="seizure_notice",
        name="Seizure Notice",
        civilization="compact",
        description="A patrol or house escort stops you not for contraband, but because your "
                    "cargo, ship, or route standing has been flagged for provisional hold. "
                    "This is institutional violence — paperwork that can escalate to force. "
                    "The right crew and documents can make it dissolve. The wrong reaction "
                    "converts a clerical problem into a criminal one.",
        ship_hull=1400,
        ship_shield=300,
        ship_damage=110,
        ship_speed=2,
        behavior="defensive",  # they don't attack first — they wait for you to resist
        cultural_option="Compact knowledge level 1: understand the claim. Level 2: contest it "
                       "formally. Nera crew: challenge the legal basis. Sera crew: present "
                       "counter-documentation. Without either: comply or flee.",
        retreat_consequence="Fleeing a seizure notice converts it to a warrant. Compact standing "
                          "drops hard. Ship flagged in every Compact-controlled lane. "
                          "The paperwork problem became a criminal one.",
        victory_consequence="Resisting seizure by force is possible but catastrophic diplomatically. "
                          "+2 Reach standing. -15 Compact standing. Wanted status likely.",
        defeat_consequence="Cargo seized. Credits fined. Ship held for 'inspection period' (days lost). "
                         "But standing damage is moderate — you cooperated, which is noted.",
    ),

    # --- 7C: Shortages, Sanctions, and Convoys ---

    "convoy_refusal": EncounterArchetype(
        id="convoy_refusal",
        name="Convoy Refusal",
        civilization="orryn",
        description="You're denied passage, bumped in priority, or accused of exploiting "
                    "shortage routing. Not an attack — a bureaucratic confrontation at "
                    "convoy speed. The escort won't fire first, but they won't move either. "
                    "Your schedule is bleeding. Your cargo may spoil. Other captains are watching.",
        ship_hull=1000,
        ship_shield=200,
        ship_damage=80,
        ship_speed=2,
        behavior="defensive",  # will not attack first
        cultural_option="Orryn knowledge level 1: understand the priority system. "
                       "Level 2: invoke The Telling to negotiate rescheduling. "
                       "Ilen crew: read the actual priority queue and find the gap. "
                       "Without any of these: wait, reroute, or force your way through.",
        retreat_consequence="Rerouting costs time and fuel. Ration cargo may spoil. "
                          "Other captains see you bumped — standing as reliable hauler drops.",
        victory_consequence="Forcing through a convoy refusal is technically possible but "
                          "marks you as a priority violator. Orryn standing drops. "
                          "Convoy access restricted for future runs.",
        defeat_consequence="You wait. Days pass. Cargo value drops. But your record stays clean "
                         "and the Orryn note your patience. Small standing gain for compliance.",
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

    # Each civ must have at least 1 station
    civs = [s.civilization for s in SLICE_STATIONS.values()]
    for civ in ["compact", "keth", "veshan", "orryn", "reach"]:
        count = civs.count(civ)
        if count < 1:
            errors.append(f"Civ {civ}: expected at least 1 station, got {count}")

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
