"""Core data models for Portlight.

Every game-state object is a plain dataclass. No ORM, no framework magic.
The engine operates on these; the app renders them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Goods
# ---------------------------------------------------------------------------

class GoodCategory(str, Enum):
    """Broad good classification — affects event interactions."""
    COMMODITY = "commodity"      # grain, timber, iron, cotton, dyes
    LUXURY = "luxury"           # silk, spice, porcelain, pearls, tea
    PROVISION = "provision"     # food, water, rum, tobacco
    CONTRABAND = "contraband"   # opium, black powder
    MILITARY = "military"       # weapons, gunpowder
    MEDICINE = "medicine"       # medicines, herbs


@dataclass
class Good:
    """Static definition of a tradeable good."""
    id: str                          # e.g. "grain", "silk"
    name: str
    category: GoodCategory
    base_price: int                  # reference price (silver)
    weight_per_unit: float = 1.0     # cargo hold units per qty


# ---------------------------------------------------------------------------
# Market slot (per-port, per-good)
# ---------------------------------------------------------------------------

@dataclass
class MarketSlot:
    """One good's market state at one port. Mutated by the economy engine."""
    good_id: str
    stock_current: int
    stock_target: int
    restock_rate: float              # units restored per day toward target
    local_affinity: float = 1.0      # >1 = port produces, <1 = port consumes
    spread: float = 0.15             # buy/sell spread fraction (prevents round-trip)
    buy_price: int = 0               # computed by economy engine
    sell_price: int = 0              # computed by economy engine
    flood_penalty: float = 0.0       # 0-1, rises when player dumps repeatedly, decays over time


# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------

class PortFeature(str, Enum):
    """Special port capabilities."""
    SHIPYARD = "shipyard"
    BLACK_MARKET = "black_market"
    SAFE_HARBOR = "safe_harbor"


@dataclass
class Port:
    """Static port definition + mutable market state."""
    id: str                          # e.g. "porto_novo"
    name: str
    description: str
    region: str                      # flavor grouping
    features: list[PortFeature] = field(default_factory=list)
    market: list[MarketSlot] = field(default_factory=list)
    port_fee: int = 5                # fixed docking cost
    provision_cost: int = 2          # silver per day of provisions
    repair_cost: int = 3             # silver per hull point
    crew_cost: int = 5               # silver per crew hire
    map_x: int = 0                   # abstract map x coordinate
    map_y: int = 0                   # abstract map y coordinate


# ---------------------------------------------------------------------------
# Ships
# ---------------------------------------------------------------------------

class ShipClass(str, Enum):
    """Ship tier — determines upgrade path."""
    SLOOP = "sloop"
    CUTTER = "cutter"
    BRIGANTINE = "brigantine"
    GALLEON = "galleon"
    MAN_OF_WAR = "man_of_war"


class UpgradeCategory(str, Enum):
    """Ship upgrade slot categories."""
    SAILS = "sails"
    HULL_PLATING = "hull_plating"
    ARMAMENT = "armament"
    CARGO = "cargo"
    NAVIGATION = "navigation"
    CREW_QUARTERS = "crew_quarters"


@dataclass
class UpgradeTemplate:
    """Static blueprint for a ship upgrade component."""
    id: str
    name: str
    category: UpgradeCategory
    price: int                           # silver cost to install
    speed_bonus: float = 0.0
    hull_max_bonus: int = 0
    cargo_bonus: int = 0
    cannon_bonus: int = 0
    maneuver_bonus: float = 0.0
    storm_resist_bonus: float = 0.0
    crew_max_bonus: int = 0
    speed_penalty: float = 0.0          # subtracted from speed
    special: str = ""                    # e.g. "contraband_immune", "chain_shot"


@dataclass
class InstalledUpgrade:
    """An upgrade installed on a specific ship."""
    upgrade_id: str
    installed_day: int = 0


# Upgrade slots per ship class
UPGRADE_SLOTS: dict[ShipClass, int] = {
    ShipClass.SLOOP: 2,
    ShipClass.CUTTER: 3,
    ShipClass.BRIGANTINE: 4,
    ShipClass.GALLEON: 5,
    ShipClass.MAN_OF_WAR: 6,
}


@dataclass
class ShipTemplate:
    """Static ship blueprint. Players buy from shipyards."""
    id: str
    name: str
    ship_class: ShipClass
    cargo_capacity: int              # max cargo weight units
    speed: float                     # distance per day
    hull_max: int                    # hit points
    crew_min: int                    # minimum crew to sail
    crew_max: int                    # optimal crew
    price: int                       # purchase cost in silver
    daily_wage: int = 1              # silver per crew per day at sea
    storm_resist: float = 0.0        # fraction of storm damage absorbed (0-1)
    cannons: int = 0                 # cannon positions (0 for sloop — board only)
    maneuver: float = 0.5            # turning ability (0-1, higher = nimbler)


@dataclass
class Ship:
    """Player's active ship instance."""
    template_id: str
    name: str
    hull: int                        # current HP
    hull_max: int
    cargo_capacity: int
    speed: float
    crew: int
    crew_max: int
    cannons: int = 0                 # from template
    maneuver: float = 0.5            # from template
    upgrades: list[InstalledUpgrade] = field(default_factory=list)
    upgrade_slots: int = 2           # set from UPGRADE_SLOTS at creation
    roster: "CrewRoster" = field(default_factory=lambda: CrewRoster())
    morale: int = 50                 # crew morale (0-100)
    officers: list["Officer"] = field(default_factory=list)

    def sync_crew(self) -> None:
        """Keep crew field in sync with roster total."""
        self.crew = self.roster.total


class CrewRole(str, Enum):
    """Crew specialization roles."""
    SAILOR = "sailor"
    GUNNER = "gunner"
    NAVIGATOR = "navigator"
    SURGEON = "surgeon"
    MARINE = "marine"
    QUARTERMASTER = "quartermaster"


@dataclass
class CrewRoster:
    """Breakdown of crew by role. Source of truth for crew count."""
    sailors: int = 0
    gunners: int = 0
    navigators: int = 0
    surgeons: int = 0
    marines: int = 0
    quartermasters: int = 0

    @property
    def total(self) -> int:
        return (self.sailors + self.gunners + self.navigators
                + self.surgeons + self.marines + self.quartermasters)


@dataclass
class Officer:
    """A named crew member with personality. Officers are specialists with identity."""
    name: str
    role: "CrewRole"
    experience: int = 0          # days served
    origin_port: str = ""        # where they were hired
    trait: str = ""              # personality trait (e.g. "loyal", "greedy", "superstitious")


@dataclass
class OwnedShip:
    """A ship in the player's fleet (docked at a port, not the flagship)."""
    ship: Ship
    docked_port_id: str              # port where this ship is docked
    cargo: list["CargoItem"] = field(default_factory=list)


def max_fleet_size(commercial_trust: int) -> int:
    """Maximum fleet size (including flagship) based on commercial trust."""
    if commercial_trust >= 26:
        return 5
    if commercial_trust >= 11:
        return 3
    return 2


# ---------------------------------------------------------------------------
# Reputation (multi-axis access model)
# ---------------------------------------------------------------------------

@dataclass
class ReputationIncident:
    """One recorded reputation-affecting event."""
    day: int
    port_id: str
    region: str
    incident_type: str       # "trade", "inspection", "seizure", "arrival", "contract"
    description: str
    heat_delta: int = 0
    standing_delta: int = 0
    trust_delta: int = 0


@dataclass
class ReputationState:
    """Tracks the player's standing across regions, ports, and institutions.

    This is not a single number. It's a topology that opens and closes doors.
    """
    # Regional standing (how established you are in each region)
    regional_standing: dict[str, int] = field(default_factory=lambda: {
        "Mediterranean": 0, "North Atlantic": 0, "West Africa": 0,
        "East Indies": 0, "South Seas": 0,
    })
    # Port-specific standing (major ports only, affects local services)
    port_standing: dict[str, int] = field(default_factory=dict)
    # Customs heat (anti-abuse pressure, rises from suspicious behavior)
    customs_heat: dict[str, int] = field(default_factory=lambda: {
        "Mediterranean": 0, "North Atlantic": 0, "West Africa": 0,
        "East Indies": 0, "South Seas": 0,
    })
    # Commercial trust (does the market believe you can deliver?)
    commercial_trust: int = 0
    # Recent incidents (capped at 20, newest first)
    recent_incidents: list[ReputationIncident] = field(default_factory=list)
    # Underworld standing (per pirate faction)
    underworld_standing: dict[str, int] = field(default_factory=dict)  # faction_id -> 0-100
    underworld_heat: int = 0  # snitch factor — rises from betraying pirates


# ---------------------------------------------------------------------------
# Captain (player state)
# ---------------------------------------------------------------------------

@dataclass
class CargoItem:
    """One stack of goods in the hold with provenance tracking."""
    good_id: str
    quantity: int
    cost_basis: int = 0              # total purchase cost (for P&L tracking)
    acquired_port: str = ""          # port where this cargo was bought
    acquired_region: str = ""        # region where acquired
    acquired_day: int = 0            # game day of acquisition


@dataclass
class ActiveInjury:
    """A persistent injury sustained in combat."""
    injury_id: str
    acquired_day: int = 0
    heal_remaining: int | None = None  # None = permanent, else days to heal
    treated: bool = False              # visited a doctor at port


@dataclass
class CombatGear:
    """Weapons, armor, and ammunition carried by the captain."""
    firearm: str | None = None         # weapon id (matchlock_pistol, etc.)
    firearm_ammo: int = 0
    throwing_weapons: dict[str, int] = field(default_factory=dict)  # weapon_id -> count
    mechanical_weapon: str | None = None  # hand_crossbow, etc.
    mechanical_ammo: int = 0
    armor: str | None = None           # armor id (leather_vest, chain_shirt, etc.)
    melee_weapon: str | None = None    # melee weapon id (cutlass, rapier, etc.)
    weapon_upgrades: dict[str, list[str]] = field(default_factory=dict)  # weapon_id -> upgrade_ids
    # Quality tracking: weapon_id -> quality tier string
    weapon_quality: dict[str, str] = field(default_factory=dict)  # e.g. {"cutlass": "standard"}
    # Usage counters for degradation: weapon_id -> uses since last maintenance
    weapon_usage: dict[str, int] = field(default_factory=dict)  # e.g. {"cutlass": 7}
    weapon_provenance: dict = field(default_factory=dict)  # weapon_id -> WeaponProvenance (serialized)


@dataclass
class Captain:
    """The player character."""
    name: str = "Captain"
    captain_type: str = "merchant"   # CaptainType value string
    silver: int = 500                # starting capital
    reputation: int = 0              # legacy field (kept for compat)
    ship: Ship | None = None
    cargo: list[CargoItem] = field(default_factory=list)
    provisions: int = 30             # days of food/water
    day: int = 1                     # current game day
    standing: ReputationState = field(default_factory=ReputationState)
    # Combat system (Phase 5+)
    learned_styles: list[str] = field(default_factory=list)
    active_style: str | None = None
    combat_gear: CombatGear = field(default_factory=CombatGear)
    injuries: list[ActiveInjury] = field(default_factory=list)
    # Skills
    skills: dict[str, int] = field(default_factory=dict)  # skill_id -> level (0-3)
    # Companions
    party: dict = field(default_factory=lambda: {"companions": [], "max_size": 2, "departed": []})
    # Fleet (Phase 7+)
    fleet: list[OwnedShip] = field(default_factory=list)
    # Anti-soft-lock: deferred fees and breach tracking
    deferred_fees: list[dict] = field(default_factory=list)  # emergency loans, deferred port fees
    breach_records: list[dict] = field(default_factory=list)  # contract breach incidents
    wanted_level: int = 0  # 0=clean, 1=watched, 2=wanted, 3=hunted
    active_bounties: list[str] = field(default_factory=list)  # bounty target captain_ids


# ---------------------------------------------------------------------------
# Voyage
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Seasons
# ---------------------------------------------------------------------------

class Season(str, Enum):
    """Four seasons derived from game day. Each cycle = 360 days."""
    SPRING = "spring"       # days 1-90: calm, trade reopens
    SUMMER = "summer"       # days 91-180: monsoon in east, peak activity
    AUTUMN = "autumn"       # days 181-270: harvest, storms build
    WINTER = "winter"       # days 271-360: harsh, North Atlantic deadly


@dataclass
class SeasonalProfile:
    """How a season affects a specific region."""
    season: Season
    region: str
    danger_mult: float = 1.0         # multiplier on route danger
    speed_mult: float = 1.0          # multiplier on travel speed
    market_effects: dict[str, float] = field(default_factory=dict)  # good_id -> demand mult
    weather_flavor: list[str] = field(default_factory=list)
    travel_warning: str = ""         # shown before departure


def get_season(day: int) -> Season:
    """Derive current season from game day (360-day cycle)."""
    day_in_year = ((day - 1) % 360) + 1
    if day_in_year <= 90:
        return Season.SPRING
    elif day_in_year <= 180:
        return Season.SUMMER
    elif day_in_year <= 270:
        return Season.AUTUMN
    else:
        return Season.WINTER


# ---------------------------------------------------------------------------
# Pirate encounters
# ---------------------------------------------------------------------------

@dataclass
class PirateEncounterRecord:
    """Record of an encounter with a named pirate captain."""
    captain_id: str
    faction_id: str
    day: int
    outcome: str                     # "attack", "trade", "alliance", "fled", "duel_win", "duel_loss"
    region: str = ""


@dataclass
class DuelRound:
    """One round of a sword duel."""
    player_stance: str               # thrust/slash/parry
    opponent_stance: str
    damage_to_opponent: int = 0
    damage_to_player: int = 0
    flavor: str = ""


@dataclass
class DuelResult:
    """Outcome of a completed duel."""
    opponent_id: str
    opponent_name: str
    player_won: bool
    draw: bool = False
    rounds: list[DuelRound] = field(default_factory=list)
    silver_delta: int = 0
    standing_delta: int = 0


@dataclass
class PendingDuel:
    """A pirate captain has challenged the player to a duel."""
    captain_id: str
    captain_name: str
    faction_id: str
    personality: str
    strength: int
    region: str = ""


@dataclass
class PirateState:
    """Tracks pirate encounters, nemesis, and duel history."""
    encounters: list[PirateEncounterRecord] = field(default_factory=list)
    nemesis_id: str | None = None
    duels_won: int = 0
    duels_lost: int = 0
    pending_duel: PendingDuel | None = None
    naval_victories: int = 0
    naval_defeats: int = 0
    captain_memories: dict = field(default_factory=dict)  # captain_id -> CaptainMemory (engine layer)
    bounty_board: list[dict] = field(default_factory=list)  # serialized bounty targets
    encounter_phase: str = ""  # persisted encounter phase (approach/naval/boarding/duel/"" = none)
    encounter_state: dict = field(default_factory=dict)  # serialized encounter combat state


@dataclass
class EncounterState:
    """Active pirate encounter — multi-phase state machine.

    Phases: approach -> naval -> boarding -> duel -> resolved
    """
    enemy_captain_id: str = ""
    enemy_captain_name: str = ""
    enemy_faction_id: str = ""
    enemy_personality: str = "balanced"
    enemy_strength: int = 5
    enemy_region: str = ""
    # Ship state
    enemy_ship_hull: int = 0
    enemy_ship_hull_max: int = 0
    enemy_ship_cannons: int = 0
    enemy_ship_maneuver: float = 0.5
    enemy_ship_speed: float = 6.0
    enemy_ship_crew: int = 10
    enemy_ship_crew_max: int = 15
    # Phase tracking
    phase: str = "approach"     # approach | naval | boarding | duel | resolved
    boarding_progress: int = 0
    boarding_threshold: int = 3
    naval_turns: int = 0
    duel_turns: int = 0


# ---------------------------------------------------------------------------
# Naval combat
# ---------------------------------------------------------------------------

@dataclass
class EnemyShip:
    """A pirate captain's ship — generated from faction + strength."""
    name: str
    hull: int
    hull_max: int
    cannons: int
    maneuver: float
    speed: float
    crew: int
    crew_max: int


@dataclass
class NavalRound:
    """One turn of ship-to-ship combat."""
    turn: int
    player_action: str               # broadside/close/evade/rake
    enemy_action: str
    player_hull_delta: int = 0
    enemy_hull_delta: int = 0
    player_crew_delta: int = 0
    enemy_crew_delta: int = 0
    boarding_progress: int = 0       # cumulative boarding counter
    flavor: str = ""


@dataclass
class NavalResult:
    """Outcome of a completed ship-to-ship engagement."""
    rounds: list[NavalRound] = field(default_factory=list)
    player_ship_sunk: bool = False
    enemy_ship_sunk: bool = False
    boarding_triggered: bool = False
    player_fled: bool = False
    enemy_fled: bool = False
    player_crew_remaining: int = 0
    enemy_crew_remaining: int = 0
    player_hull_remaining: int = 0
    enemy_hull_remaining: int = 0


class VoyageStatus(str, Enum):
    IN_PORT = "in_port"
    AT_SEA = "at_sea"
    ARRIVED = "arrived"


@dataclass
class VoyageState:
    """Tracks an active voyage between two ports."""
    origin_id: str
    destination_id: str
    distance: int                    # total distance units
    progress: int = 0                # distance covered so far
    days_elapsed: int = 0
    status: VoyageStatus = VoyageStatus.IN_PORT
    recent_events: list[str] = field(default_factory=list)  # last 5 event types for dedup


# ---------------------------------------------------------------------------
# Route map
# ---------------------------------------------------------------------------

@dataclass
class Route:
    """A navigable connection between two ports."""
    port_a: str
    port_b: str
    distance: int
    danger: float = 0.1             # base event probability per day
    min_ship_class: str = "sloop"   # minimum ship class to attempt this route
    lore_name: str = ""             # named trade route (e.g. "The Grain Road")
    lore: str = ""                  # historical flavor text


# ---------------------------------------------------------------------------
# World state (top-level game state)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Culture (static reference data + mutable festival state)
# ---------------------------------------------------------------------------

@dataclass
class Festival:
    """A recurring cultural event that affects port economics."""
    id: str
    name: str
    description: str
    region: str
    frequency_days: int              # roughly how often (stochastic trigger)
    market_effects: dict[str, float] = field(default_factory=dict)  # good_id -> demand mult
    duration_days: int = 3
    standing_bonus: int = 0          # bonus standing for trading during festival


@dataclass
class RegionCulture:
    """Cultural identity of a trade region — static reference data."""
    id: str                          # "mediterranean", "north_atlantic", etc.
    region_name: str                 # canonical: "Mediterranean"
    cultural_name: str               # flavor: "The Middle Sea"
    ethos: str                       # 1-2 sentence cultural philosophy
    trade_philosophy: str            # how this culture views commerce
    sacred_goods: list[str] = field(default_factory=list)    # culturally revered
    forbidden_goods: list[str] = field(default_factory=list) # taboo/restricted
    prized_goods: list[str] = field(default_factory=list)    # socially valued
    greeting: str = ""               # merchant greeting on arrival
    farewell: str = ""               # parting words
    proverb: str = ""                # trade proverb
    festivals: list[Festival] = field(default_factory=list)
    weather_flavor: list[str] = field(default_factory=list)  # atmospheric text


@dataclass
class PortCulture:
    """Cultural flavor for a specific port — static reference data."""
    port_id: str
    landmark: str                    # a named cultural landmark
    local_custom: str                # a custom that colors trade here
    atmosphere: str                  # sensory: what it feels/smells/sounds like
    dock_scene: str                  # what you see when you arrive
    tavern_rumor: str                # a rumor you overhear
    cultural_group: str = ""         # local faction/guild name
    cultural_group_description: str = ""


@dataclass
class ActiveFestival:
    """A festival currently in progress."""
    festival_id: str
    port_id: str
    start_day: int
    end_day: int


@dataclass
class CulturalState:
    """Tracks cultural engagement — persisted in save files."""
    active_festivals: list[ActiveFestival] = field(default_factory=list)
    regions_entered: list[str] = field(default_factory=list)
    cultural_encounters: int = 0
    port_visits: dict[str, int] = field(default_factory=dict)  # port_id -> count
    festivals_visited: int = 0  # lifetime count of festival port arrivals


# ---------------------------------------------------------------------------
# World state (top-level game state)
# ---------------------------------------------------------------------------

@dataclass
class WorldState:
    """Complete game state — serialized for save/load."""
    captain: Captain = field(default_factory=Captain)
    ports: dict[str, Port] = field(default_factory=dict)
    routes: list[Route] = field(default_factory=list)
    voyage: VoyageState | None = None
    day: int = 1
    seed: int = 0                    # RNG seed for reproducibility
    culture: CulturalState = field(default_factory=CulturalState)
    pirates: PirateState = field(default_factory=PirateState)
