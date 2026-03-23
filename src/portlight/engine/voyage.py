"""Voyage engine - travel state machine, provision consumption, route events.

Phase 2 additions:
  - Ship class requirements on routes (warn or block)
  - Crew wages paid daily at sea
  - Storm damage reduced by ship storm_resist
  - Cargo-aware events (pirates target valuable cargo)
  - Opportunity events (flotsam, merchant encounter)
  - Undermanned penalty (speed reduction)

Phase 3A additions:
  - Captain identity modifiers (provision burn, speed, storm resist, cargo damage)
  - Inspection profile (frequency, seizure risk, fine multiplier)
  - Port fee multiplier from captain type
  - Reputation mutations from trade and inspection events

Contract:
  - depart(world, destination_id) -> VoyageState | error string
  - advance_day(world, rng) -> list[VoyageEvent]  (may include arrival)
  - arrive(world) -> settles captain in destination port
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from portlight.engine.models import Route, VoyageState, VoyageStatus

if TYPE_CHECKING:
    from portlight.engine.captain_identity import CaptainTemplate
    from portlight.engine.models import Captain, Ship, WorldState


def _get_captain_mods(captain: "Captain") -> "CaptainTemplate | None":
    """Load captain template from captain_type string. Returns None for unknown types."""
    try:
        from portlight.engine.captain_identity import CAPTAIN_TEMPLATES, CaptainType
        ct = CaptainType(captain.captain_type)
        return CAPTAIN_TEMPLATES[ct]
    except (ValueError, KeyError):
        return None


class EventType(str, Enum):
    STORM = "storm"
    PIRATES = "pirates"
    INSPECTION = "inspection"
    CALM_SEAS = "calm_seas"
    FAVORABLE_WIND = "favorable_wind"
    PROVISIONS_SPOILED = "provisions_spoiled"
    CARGO_DAMAGED = "cargo_damaged"
    MERCHANT_ENCOUNTER = "merchant_encounter"
    FLOTSAM = "flotsam"
    NOTHING = "nothing"
    # Cultural events (replace boredom, not danger)
    FOREIGN_VESSEL = "foreign_vessel"
    CULTURAL_WATERS = "cultural_waters"
    SEA_CEREMONY = "sea_ceremony"
    WHALE_SIGHTING = "whale_sighting"
    LIGHTHOUSE = "lighthouse"
    MUSICIAN_ABOARD = "musician_aboard"
    DRIFTING_OFFERING = "drifting_offering"
    STAR_NAVIGATION = "star_navigation"


@dataclass
class VoyageEvent:
    """One thing that happened during a day at sea."""
    event_type: EventType
    message: str
    hull_delta: int = 0
    provision_delta: int = 0
    silver_delta: int = 0
    crew_delta: int = 0
    speed_modifier: float = 1.0
    cargo_lost: dict[str, int] | None = None  # good_id -> qty lost
    flavor: str = ""                           # atmospheric color text
    _pending_duel: object = None               # PendingDuel when pirate issues challenge


# ---------------------------------------------------------------------------
# Ship class ordering for route checks
# ---------------------------------------------------------------------------

_SHIP_CLASS_RANK = {"sloop": 0, "cutter": 1, "brigantine": 2, "galleon": 3, "man_of_war": 4}


def ship_class_rank(template_id: str) -> int:
    """Get numeric rank from template_id."""
    for cls_name, rank in _SHIP_CLASS_RANK.items():
        if cls_name in template_id:
            return rank
    return 0


# ---------------------------------------------------------------------------
# Event table (Phase 2)
# ---------------------------------------------------------------------------

_EVENT_WEIGHTS: list[tuple[EventType, float]] = [
    (EventType.NOTHING, 0.23),
    (EventType.CALM_SEAS, 0.10),
    (EventType.FAVORABLE_WIND, 0.11),
    (EventType.STORM, 0.10),
    (EventType.PIRATES, 0.12),
    (EventType.INSPECTION, 0.05),
    (EventType.PROVISIONS_SPOILED, 0.04),
    (EventType.CARGO_DAMAGED, 0.03),
    (EventType.MERCHANT_ENCOUNTER, 0.06),
    (EventType.FLOTSAM, 0.05),
    # Cultural events (12% total — atmosphere, not punishment)
    (EventType.FOREIGN_VESSEL, 0.015),
    (EventType.CULTURAL_WATERS, 0.015),
    (EventType.SEA_CEREMONY, 0.01),
    (EventType.WHALE_SIGHTING, 0.015),
    (EventType.LIGHTHOUSE, 0.015),
    (EventType.MUSICIAN_ABOARD, 0.015),
    (EventType.DRIFTING_OFFERING, 0.01),
    (EventType.STAR_NAVIGATION, 0.015),
]


def _pick_event(
    danger: float, rng: random.Random,
    inspection_mult: float = 1.0,
    recent_events: list[str] | None = None,
) -> EventType:
    """Weighted random event, danger level scales hostile events.

    Events that appeared recently have their weight reduced by 80% to avoid
    repetitive gameplay.
    """
    recent = set(recent_events or [])
    weights = []
    for etype, base_w in _EVENT_WEIGHTS:
        w = base_w
        if etype in (EventType.STORM, EventType.PIRATES, EventType.CARGO_DAMAGED):
            w *= (1 + danger * 2)
        elif etype in (EventType.MERCHANT_ENCOUNTER, EventType.FLOTSAM):
            w *= max(0.5, 1 - danger)  # less likely on dangerous routes
        elif etype == EventType.INSPECTION:
            w *= inspection_mult  # captain identity affects inspection frequency
        # Reduce weight of recently seen events
        if etype.value in recent:
            w *= 0.2
        weights.append(w)
    return rng.choices([e for e, _ in _EVENT_WEIGHTS], weights=weights, k=1)[0]


def _resolve_event(
    event_type: EventType, rng: random.Random,
    captain: "Captain", ship: "Ship",
    world: "WorldState | None" = None,
    voyage: "VoyageState | None" = None,
) -> VoyageEvent:
    """Generate concrete effects for an event type, aware of ship and cargo."""
    from portlight.content.ships import SHIPS
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolve_storm_resist
    template = SHIPS.get(ship.template_id)
    if template:
        storm_resist = resolve_storm_resist(ship, template, UPGRADES)
    else:
        storm_resist = 0.0

    # Captain identity modifiers
    cap_mods = _get_captain_mods(captain)
    if cap_mods:
        storm_resist = min(0.9, storm_resist + cap_mods.voyage.storm_resist_bonus)
        cargo_dmg_mult = cap_mods.voyage.cargo_damage_mult
        insp = cap_mods.inspection
    else:
        cargo_dmg_mult = 1.0
        insp = None

    match event_type:
        case EventType.STORM:
            raw_dmg = rng.randint(5, 18)
            dmg = max(1, int(raw_dmg * (1 - storm_resist)))
            if storm_resist > 0.3:
                msg = f"A storm batters the ship. Your hull absorbs the worst of it. (-{dmg} hull)"
            else:
                msg = f"A violent storm batters the ship! (-{dmg} hull)"
            return VoyageEvent(EventType.STORM, msg, hull_delta=-dmg, speed_modifier=0.5)

        case EventType.PIRATES:
            # Pirates target valuable cargo — chance of named captain duel
            from portlight.content.factions import FACTIONS, get_captains_for_faction, get_faction_for_region
            from portlight.engine.models import PendingDuel

            # 40% chance a named pirate captain issues a duel challenge
            duel_roll = rng.random()
            if duel_roll < 0.40 and world is not None and voyage is not None:
                # Pick a faction active in this area
                dest_port = world.ports.get(voyage.destination_id)
                region = dest_port.region if dest_port else "Mediterranean"
                active_factions = get_faction_for_region(region)
                if not active_factions:
                    active_factions = list(FACTIONS.values())[:1]
                faction = rng.choice(active_factions)
                faction_captains = get_captains_for_faction(faction.id)
                pirate_captain = rng.choice(faction_captains) if faction_captains else None

                if pirate_captain is not None:
                    pending = PendingDuel(
                        captain_id=pirate_captain.id,
                        captain_name=pirate_captain.name,
                        faction_id=faction.id,
                        personality=pirate_captain.personality,
                        strength=pirate_captain.strength,
                        region=region,
                    )
                    return VoyageEvent(
                        EventType.PIRATES,
                        f"{pirate_captain.name} of the {faction.name} blocks your path and demands a duel! "
                        f"Use [bold]portlight duel <stance>[/bold] to fight (thrust/slash/parry, 5 rounds).",
                        flavor=f"Strength {pirate_captain.strength}, {pirate_captain.personality} fighter.",
                        _pending_duel=pending,
                    )

            # No duel — standard pirate raid
            cargo_value = sum(c.quantity * 10 for c in captain.cargo)  # rough estimate
            base_loss = rng.randint(10, 40)
            silver_loss = min(base_loss + cargo_value // 10, captain.silver)
            dmg = rng.randint(3, 12)
            dmg = max(1, int(dmg * (1 - storm_resist * 0.5)))
            return VoyageEvent(
                EventType.PIRATES,
                f"Pirates attack! You fight them off but lose {silver_loss} silver. (-{dmg} hull)",
                hull_delta=-dmg, silver_delta=-silver_loss,
            )

        case EventType.INSPECTION:
            fee = rng.randint(5, 25)
            fine_mult = insp.fine_mult if insp else 1.0
            # Heat-based fine amplification from reputation
            max_heat = 0
            if hasattr(captain, 'standing') and captain.standing.customs_heat:
                max_heat = max(captain.standing.customs_heat.values())
                if max_heat >= 30:
                    fine_mult *= 1.5
                elif max_heat >= 15:
                    fine_mult *= 1.2
            fee = max(1, int(fee * fine_mult))

            seized_goods: dict[str, int] | None = None
            seizure_msg = ""

            # Contraband detection — catastrophic if found
            contraband_items = [c for c in captain.cargo if c.good_id in ("opium", "black_powder", "stolen_cargo")]
            if contraband_items:
                # Detection: 40% base + 10% per heat above 15, -15% for smuggler
                detect_chance = 0.40 + max(0, (max_heat - 15) * 0.10)
                is_smuggler = captain.captain_type == "smuggler"
                if is_smuggler:
                    detect_chance -= 0.15
                detect_chance = max(0.1, min(0.9, detect_chance))
                if rng.random() < detect_chance:
                    # ALL contraband seized, heavy fine
                    seized_goods = {}
                    contraband_value = 0
                    for item in contraband_items:
                        seized_goods[item.good_id] = item.quantity
                        contraband_value += item.quantity * 30  # rough value for fine calc
                    fine = contraband_value * 3
                    fee += fine
                    seizure_msg = (
                        " CONTRABAND FOUND! The inspectors seize everything illegal in your hold. "
                        f"Fine: {fine} silver. Your reputation takes a devastating hit."
                    )
                    return VoyageEvent(
                        EventType.INSPECTION, f"A patrol boards your ship.{seizure_msg}",
                        silver_delta=-fee, cargo_lost=seized_goods,
                        flavor="The silence after a contraband seizure is the loudest sound at sea.",
                    )

            # Normal seizure risk (smuggler penalty — non-contraband)
            if insp and insp.seizure_risk > 0 and captain.cargo:
                if rng.random() < insp.seizure_risk:
                    # Only seize non-contraband here (contraband handled above)
                    legal_cargo = [c for c in captain.cargo if c.good_id not in ("opium", "black_powder", "stolen_cargo")]
                    if legal_cargo:
                        target = rng.choice(legal_cargo)
                        seized = min(target.quantity, rng.randint(1, 3))
                        seized_goods = {target.good_id: seized}
                        seizure_msg = f" They confiscate {seized} units of {target.good_id}!"
            actual_fee = min(fee, captain.silver)
            if actual_fee < fee:
                msg = f"A patrol inspects your cargo and levies a {fee} silver fee (only {actual_fee} collected).{seizure_msg}"
            else:
                msg = f"A patrol inspects your cargo and levies a {fee} silver fee.{seizure_msg}"
            return VoyageEvent(EventType.INSPECTION, msg,
                               silver_delta=-actual_fee, cargo_lost=seized_goods)

        case EventType.FAVORABLE_WIND:
            return VoyageEvent(EventType.FAVORABLE_WIND,
                "Strong tailwinds speed your journey!", speed_modifier=1.5)

        case EventType.PROVISIONS_SPOILED:
            spoil = rng.randint(2, 6)
            return VoyageEvent(EventType.PROVISIONS_SPOILED,
                f"Some provisions have spoiled. (-{spoil} days)", provision_delta=-spoil)

        case EventType.CALM_SEAS:
            return VoyageEvent(EventType.CALM_SEAS,
                "Calm seas. Good for rest, bad for progress.", speed_modifier=0.6)

        case EventType.CARGO_DAMAGED:
            # Damage random cargo in hold (captain modifier reduces loss)
            if captain.cargo:
                target = rng.choice(captain.cargo)
                raw_lost = rng.randint(1, 3)
                lost = max(1, int(raw_lost * cargo_dmg_mult))
                lost = min(target.quantity, lost)
                return VoyageEvent(
                    EventType.CARGO_DAMAGED,
                    f"Rough seas damaged {lost} units of {target.good_id} in the hold.",
                    cargo_lost={target.good_id: lost},
                )
            return VoyageEvent(EventType.NOTHING, "An uneventful day at sea.")

        case EventType.MERCHANT_ENCOUNTER:
            gain = rng.randint(5, 20)
            return VoyageEvent(EventType.MERCHANT_ENCOUNTER,
                f"A passing merchant offers information and a small gift. (+{gain} silver)",
                silver_delta=gain)

        case EventType.FLOTSAM:
            prov = rng.randint(1, 4)
            return VoyageEvent(EventType.FLOTSAM,
                f"Floating wreckage yields salvageable supplies. (+{prov} provisions)",
                provision_delta=prov)

        # ---------------------------------------------------------------
        # Cultural events — atmosphere over mechanics
        # ---------------------------------------------------------------
        case EventType.FOREIGN_VESSEL:
            return _resolve_foreign_vessel(rng, captain)

        case EventType.CULTURAL_WATERS:
            return _resolve_cultural_waters(rng, captain)

        case EventType.SEA_CEREMONY:
            return VoyageEvent(
                EventType.SEA_CEREMONY,
                "The crew gathers at dusk. The bosun pours rum into the sea — "
                "an old offering for safe passage.",
                provision_delta=-1,
                flavor="Some rituals are older than the ships that carry them.",
            )

        case EventType.WHALE_SIGHTING:
            return VoyageEvent(
                EventType.WHALE_SIGHTING,
                "A pod of whales surfaces alongside the ship. "
                "The crew watches in silence.",
                flavor="Some things are bigger than commerce.",
            )

        case EventType.LIGHTHOUSE:
            return _resolve_lighthouse(rng, captain)

        case EventType.MUSICIAN_ABOARD:
            return _resolve_musician(rng, captain)

        case EventType.DRIFTING_OFFERING:
            return _resolve_drifting_offering(rng, captain)

        case EventType.STAR_NAVIGATION:
            return _resolve_star_navigation(rng, captain)

        case _:
            return VoyageEvent(EventType.NOTHING, "An uneventful day at sea.")


# ---------------------------------------------------------------------------
# Cultural event helpers
# ---------------------------------------------------------------------------

_REGION_VESSEL_FLAVOR: dict[str, list[str]] = {
    "Mediterranean": [
        "A merchant galley with striped sails crosses your bow, its deck stacked with amphoras.",
        "A felucca glides past, its triangular sail catching the coastal wind. The crew waves.",
    ],
    "North Atlantic": [
        "A heavy iron-hulled freighter steams past, smoke trailing from its stack. Northern build.",
        "A grey warship cuts through the swell, pennants snapping. The North Atlantic patrol.",
    ],
    "West Africa": [
        "A carved fishing boat with outriggers crosses your wake. The crew sings as they work.",
        "A cotton trader's vessel passes, bales stacked so high the deck is barely visible.",
    ],
    "East Indies": [
        "A junk with crimson sails and incense burners at the prow glides past in silence.",
        "A fleet of sampans appears from behind an island, loaded with silk-wrapped cargo.",
    ],
    "South Seas": [
        "A war canoe with painted warriors paddles past. They watch you but do not stop.",
        "An outrigger with pearl divers skims across the reef. They move like the water itself.",
    ],
}


def _resolve_foreign_vessel(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """Encounter a vessel from the destination region's culture."""
    regions = list(_REGION_VESSEL_FLAVOR.keys())
    region = rng.choice(regions)
    flavors = _REGION_VESSEL_FLAVOR[region]
    msg = rng.choice(flavors)
    return VoyageEvent(EventType.FOREIGN_VESSEL, msg, flavor="The sea is shared.")


_REGION_CROSSING_FLAVOR: dict[str, str] = {
    "Mediterranean": "The water changes here — warmer, bluer. The Middle Sea welcomes you.",
    "North Atlantic": "Grey waves and cold spray. You feel the weight of the Iron Coast ahead.",
    "West Africa": "The current warms. Palm-fringed shores appear on the horizon. The Gold Coast.",
    "East Indies": "Jade-green water and the distant scent of spice. The Silk Waters begin here.",
    "South Seas": "Turquoise shallows and coral beneath the hull. The Reef Kingdoms lie ahead.",
}


def _resolve_cultural_waters(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """Crossing into a new region's waters."""
    regions = list(_REGION_CROSSING_FLAVOR.keys())
    region = rng.choice(regions)
    msg = _REGION_CROSSING_FLAVOR[region]
    return VoyageEvent(
        EventType.CULTURAL_WATERS, msg,
        flavor="Every border on the sea is drawn by culture, not by stone.",
    )


def _resolve_lighthouse(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """Sighting a famous beacon — confirms you're on course."""
    beacons = [
        "The beacon of Porto Novo breaks through the haze. You're on course.",
        "Ironhaven's Great Foundry chimney glows red on the horizon — a landmark for miles.",
        "The Wind Temple pagoda catches the sunset. Monsoon Reach is near.",
        "Ember Peak's volcanic glow marks the horizon. The South Seas await.",
        "The Whale Arch of Thornport stands white against the grey sky.",
    ]
    msg = rng.choice(beacons)
    return VoyageEvent(
        EventType.LIGHTHOUSE, msg, speed_modifier=1.1,
        flavor="Known waters. The charts don't lie.",
    )


_REGION_MUSIC: dict[str, str] = {
    "Mediterranean": "A sailor plays a reed flute — an old Mediterranean melody about grain ships and fair winds.",
    "North Atlantic": "A northern ballad, deep and slow, about iron and ice and the lights in winter skies.",
    "West Africa": "Drums and singing from the crew — rhythms of the Gold Coast that make the work feel lighter.",
    "East Indies": "A string instrument hums from below deck — eastern scales that the crew learned in Jade Port.",
    "South Seas": "Shell horns and chanting — songs the crew picked up at Coral Throne. Haunting and beautiful.",
}


def _resolve_musician(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """A sailor plays music from their home region."""
    regions = list(_REGION_MUSIC.keys())
    region = rng.choice(regions)
    msg = _REGION_MUSIC[region]
    return VoyageEvent(
        EventType.MUSICIAN_ABOARD, msg,
        flavor="For a moment, the sea feels smaller.",
    )


def _resolve_drifting_offering(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """Floating shrine or cultural offering in the water."""
    offerings = [
        "Floating flowers and a small wooden shrine drift past — an offering for safe passage.",
        "A garland of marigolds on a leaf boat. Someone prayed for a ship that never came home.",
        "A sealed clay jar bobs in the waves, marked with symbols of good fortune.",
        "Driftwood carved with old prayers. The crew leaves it undisturbed.",
    ]
    msg = rng.choice(offerings)
    return VoyageEvent(
        EventType.DRIFTING_OFFERING, msg,
        flavor="The sea remembers everyone who sails it.",
    )


def _resolve_star_navigation(rng: "random.Random", captain: "Captain") -> VoyageEvent:
    """Navigator reads the stars — bonus speed, extra for navigator captains."""
    cap_mods = _get_captain_mods(captain)
    is_navigator = cap_mods and captain.captain_type == "navigator"
    if is_navigator:
        speed = 1.2
        msg = (
            "You read the stars yourself and correct course. "
            "The old constellations guide you true — no one reads them better."
        )
    else:
        speed = 1.05
        msg = (
            "The navigator reads the stars and adjusts course. "
            "Ancient constellations confirm your heading."
        )
    return VoyageEvent(
        EventType.STAR_NAVIGATION, msg, speed_modifier=speed,
        flavor="The sky is the oldest chart.",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_route(world: "WorldState", origin_id: str, dest_id: str) -> Route | None:
    """Find a route between two ports (bidirectional)."""
    for r in world.routes:
        if (r.port_a == origin_id and r.port_b == dest_id) or \
           (r.port_a == dest_id and r.port_b == origin_id):
            return r
    return None


def check_route_suitability(route: Route, ship: "Ship") -> str | None:
    """Check if ship meets route requirements. Returns warning or None."""
    route_rank = _SHIP_CLASS_RANK.get(route.min_ship_class, 0)
    ship_rank = ship_class_rank(ship.template_id)
    if ship_rank < route_rank:
        if route_rank - ship_rank >= 2:
            return f"BLOCKED: This route requires at least a {route.min_ship_class}. Your {ship.name} cannot attempt it."
        return (f"WARNING: This route recommends a {route.min_ship_class}. "
                f"Your {ship.name} will face increased danger.")
    return None


def _bounty_hunter_event(captain: "Captain", rng: random.Random) -> VoyageEvent:
    """Generate a bounty hunter encounter for wanted captains."""
    from portlight.engine.models import PendingDuel

    # Named bounty hunters
    hunters = [
        ("marshal_kael", "Marshal Kael", "northern_pact", "balanced", 8),
        ("iron_hound", "The Iron Hound", "northern_pact", "aggressive", 9),
        ("silent_mora", "Silent Mora", "northern_pact", "defensive", 7),
    ]
    hunter = rng.choice(hunters)
    hid, hname, hfaction, hpersonality, hstrength = hunter

    # Calculate debt owed
    total_debt = sum(f["amount"] for f in captain.deferred_fees if f.get("type") == "emergency_loan")
    breach_penalty = len(captain.breach_records) * 50
    demand = total_debt + breach_penalty

    pending = PendingDuel(
        captain_id=hid,
        captain_name=hname,
        faction_id=hfaction,
        personality=hpersonality,
        strength=hstrength,
        region="",
    )
    msg = (
        f"A fast ship flying Pact colors cuts across your bow. {hname} stands at the rail, "
        f"commission papers in hand. \"You owe debts, Captain. {demand} silver, or we settle this "
        f"with steel.\"\n\n"
        f"Use [bold]portlight encounter <negotiate|flee|fight>[/bold] to respond."
    )
    return VoyageEvent(
        EventType.PIRATES,
        msg,
        flavor=f"Bounty hunter — strength {hstrength}, {hpersonality} fighter. Demands {demand} silver.",
        _pending_duel=pending,
    )


def depart(world: "WorldState", destination_id: str, defer_fee: bool = False) -> VoyageState | str:
    """Begin a voyage from current port to destination."""
    captain = world.captain
    if captain.ship is None:
        return "No ship"
    if world.voyage and world.voyage.status == VoyageStatus.AT_SEA:
        return "Already at sea"

    current_port_id = world.voyage.destination_id if world.voyage else None
    if current_port_id is None:
        return "Not docked at any port"
    if current_port_id == destination_id:
        return "Already at this port"

    route = find_route(world, current_port_id, destination_id)
    if route is None:
        return f"No route from {current_port_id} to {destination_id}"

    # Ship class check
    suitability = check_route_suitability(route, captain.ship)
    if suitability and suitability.startswith("BLOCKED"):
        return suitability

    # Crew minimum check
    from portlight.content.ships import SHIPS
    template = SHIPS.get(captain.ship.template_id)
    crew_min = template.crew_min if template else 1
    if captain.ship.crew < crew_min:
        return f"Need at least {crew_min} crew to sail, have {captain.ship.crew}. Hire crew first."

    # Pay port fee (captain modifier applies)
    port = world.ports.get(current_port_id)
    if port:
        cap_mods = _get_captain_mods(captain)
        fee_mult = cap_mods.pricing.port_fee_mult if cap_mods else 1.0
        fee = max(1, int(port.port_fee * fee_mult))
        if fee > captain.silver:
            if defer_fee:
                # Defer the fee: double amount charged on next arrival
                captain.deferred_fees.append({
                    "type": "port_fee",
                    "amount": fee * 2,
                    "day": captain.day,
                })
            else:
                return f"Need {fee} silver for port fee, have {captain.silver}"
        else:
            captain.silver -= fee

    # Convoy: fleet ships at this port join the voyage
    for owned in captain.fleet:
        if owned.docked_port_id == current_port_id:
            owned.docked_port_id = ""  # in transit

    voyage = VoyageState(
        origin_id=current_port_id,
        destination_id=destination_id,
        distance=route.distance,
        status=VoyageStatus.AT_SEA,
    )
    world.voyage = voyage
    return voyage


def advance_day(world: "WorldState", rng: random.Random | None = None) -> list[VoyageEvent]:
    """Advance one day at sea. Returns events that occurred."""
    rng = rng or random.Random()
    voyage = world.voyage
    captain = world.captain

    if voyage is None or voyage.status != VoyageStatus.AT_SEA:
        return []
    if captain.ship is None:
        return []

    # Block advancement if a pirate encounter is pending resolution
    if world.pirates.pending_duel is not None:
        return []

    events: list[VoyageEvent] = []

    # Captain modifiers
    cap_mods = _get_captain_mods(captain)
    provision_burn = cap_mods.voyage.provision_burn if cap_mods else 1.0
    speed_bonus = cap_mods.voyage.speed_bonus if cap_mods else 0.0
    inspection_mult = cap_mods.inspection.inspection_chance_mult if cap_mods else 1.0

    # Heat-based inspection amplification (reputation access effect)
    if hasattr(captain, 'standing'):
        from portlight.engine.reputation import get_inspection_modifier
        dest_port = world.ports.get(voyage.destination_id)
        region = dest_port.region if dest_port else "Mediterranean"
        inspection_mult *= get_inspection_modifier(captain.standing, region)

    # Wanted level increases inspection frequency
    if captain.wanted_level >= 2:
        inspection_mult *= 1.5  # 50% more inspections
    elif captain.wanted_level >= 1:
        inspection_mult *= 1.2  # 20% more inspections

    # Consume provisions (captain modifier affects burn rate)
    # provision_burn < 1.0 means some days you don't consume
    if provision_burn >= 1.0 or rng.random() < provision_burn:
        captain.provisions -= 1
    if captain.provisions < 0:
        captain.provisions = 0
        events.append(VoyageEvent(EventType.NOTHING,
            "No provisions! The crew suffers.", crew_delta=-1))

    # Crew wages (paid daily at sea — flagship roster + docked fleet)
    from portlight.content.ships import SHIPS
    from portlight.engine.ship_stats import compute_daily_wages
    template = SHIPS.get(captain.ship.template_id)
    # Use roster-based wages if roster has crew, else fallback to flat rate
    if captain.ship.roster.total > 0:
        daily_wage = template.daily_wage if template else 1
        wage_cost = compute_daily_wages(captain.ship.roster, daily_wage)
    else:
        daily_wage = template.daily_wage if template else 1
        wage_cost = daily_wage * captain.ship.crew
    # Add docked fleet crew wages
    from portlight.engine.fleet import fleet_daily_wages
    wage_cost += fleet_daily_wages(captain)
    wages_paid = True
    if wage_cost > 0 and captain.silver >= wage_cost:
        captain.silver -= wage_cost
    elif wage_cost > 0:
        wages_paid = False
        # Can't pay crew - morale hit
        events.append(VoyageEvent(EventType.NOTHING,
            "Can't pay crew wages! Morale drops.", crew_delta=-1))

    # Tick crew morale
    from portlight.engine.ship_stats import tick_morale_at_sea, morale_speed_modifier
    provisions_ok = captain.provisions > 0
    captain.ship.morale = tick_morale_at_sea(
        captain.ship, wages_paid, provisions_ok, voyage.days_elapsed,
    )

    # Route event
    route = find_route(world, voyage.origin_id, voyage.destination_id)
    danger = route.danger if route else 0.1

    # Danger penalty for undersized ship
    if route:
        route_rank = _SHIP_CLASS_RANK.get(route.min_ship_class, 0)
        ship_rank = ship_class_rank(captain.ship.template_id)
        if ship_rank < route_rank:
            danger *= 1.5  # 50% more danger with unsuitable ship

    # Seasonal danger modifier
    dest_port = world.ports.get(voyage.destination_id)
    _dest_region = dest_port.region if dest_port else "Mediterranean"
    from portlight.content.seasons import get_seasonal_profile
    _season_profile = get_seasonal_profile(_dest_region, world.day)
    if _season_profile:
        danger *= _season_profile.danger_mult

    event_type = _pick_event(danger, rng, inspection_mult, voyage.recent_events)
    event = _resolve_event(event_type, rng, captain, captain.ship, world, voyage)
    events.append(event)

    # Track recent events for dedup (cap at 5)
    voyage.recent_events.append(event_type.value)
    if len(voyage.recent_events) > 5:
        voyage.recent_events = voyage.recent_events[-5:]

    # Handle pending duel from pirate encounter
    if event._pending_duel is not None:
        world.pirates.pending_duel = event._pending_duel

    # Bounty hunter encounter for wanted captains (level 3 = hunted)
    if captain.wanted_level >= 3 and event._pending_duel is None:
        if rng.random() < 0.15:  # 15% chance per day at sea
            bh_event = _bounty_hunter_event(captain, rng)
            events.append(bh_event)
            if bh_event._pending_duel is not None:
                world.pirates.pending_duel = bh_event._pending_duel

    # Apply event effects
    captain.ship.hull = max(0, captain.ship.hull + event.hull_delta)
    captain.provisions = max(0, captain.provisions + event.provision_delta)
    captain.silver = max(0, captain.silver + event.silver_delta)
    captain.ship.crew = max(0, captain.ship.crew + event.crew_delta)

    # Apply storm damage to convoy ships
    convoy_ships = [o for o in captain.fleet if o.docked_port_id == ""]
    if convoy_ships and event.hull_delta < 0:
        from portlight.content.upgrades import UPGRADES as _CONV_UPG
        from portlight.engine.ship_stats import resolve_storm_resist
        for owned in convoy_ships:
            escort_template = SHIPS.get(owned.ship.template_id)
            if escort_template:
                sr = resolve_storm_resist(owned.ship, escort_template, _CONV_UPG)
            else:
                sr = 0.0
            # Convoy ships take proportional damage (reduced by their own storm resist)
            raw_dmg = abs(event.hull_delta)
            dmg = max(1, int(raw_dmg * (1 - sr)))
            owned.ship.hull = max(0, owned.ship.hull - dmg)

    # Apply cargo damage
    if event.cargo_lost:
        for good_id, lost in event.cargo_lost.items():
            for item in captain.cargo:
                if item.good_id == good_id:
                    item.quantity = max(0, item.quantity - lost)
                    if item.quantity == 0:
                        captain.cargo.remove(item)
                    break

    # Progress (undermanned penalty + captain speed bonus + crew navigator + convoy + seasonal)
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolve_speed, navigator_speed_bonus
    resolved_speed = resolve_speed(captain.ship, UPGRADES)
    nav_bonus = navigator_speed_bonus(captain.ship.roster)
    base_speed = resolved_speed + speed_bonus + nav_bonus
    crew_min = template.crew_min if template else 1
    if captain.ship.crew < crew_min:
        base_speed *= 0.5  # half speed when undermanned
    elif captain.ship.crew < captain.ship.crew_max:
        # Slight penalty when not fully crewed
        crew_ratio = captain.ship.crew / captain.ship.crew_max
        base_speed *= (0.7 + 0.3 * crew_ratio)

    # Convoy speed: limited by slowest ship in convoy
    convoy_ships = [o for o in captain.fleet if o.docked_port_id == ""]
    if convoy_ships:
        for owned in convoy_ships:
            ship_speed = resolve_speed(owned.ship, UPGRADES)
            base_speed = min(base_speed, ship_speed)

    # Morale speed modifier
    base_speed *= morale_speed_modifier(captain.ship.morale)

    # Seasonal speed modifier
    if _season_profile:
        base_speed *= _season_profile.speed_mult

    day_progress = int(base_speed * event.speed_modifier)
    voyage.progress += day_progress
    voyage.days_elapsed += 1
    world.day += 1
    captain.day += 1

    # Hull degradation: every 20 days at sea, hull_max drops by 1 (wear and tear)
    if voyage.days_elapsed > 0 and voyage.days_elapsed % 20 == 0:
        if captain.ship.hull_max > 20:  # floor at 20 hull_max
            captain.ship.hull_max -= 1
            captain.ship.hull = min(captain.ship.hull, captain.ship.hull_max)
        # Convoy ships degrade too
        for owned in [o for o in captain.fleet if o.docked_port_id == ""]:
            if owned.ship.hull_max > 20:
                owned.ship.hull_max -= 1
                owned.ship.hull = min(owned.ship.hull, owned.ship.hull_max)

    # Check arrival
    if voyage.progress >= voyage.distance:
        voyage.status = VoyageStatus.ARRIVED

    return events


def arrive(world: "WorldState") -> str | None:
    """Complete arrival at destination port. Returns None on success, error on failure."""
    voyage = world.voyage
    if voyage is None or voyage.status != VoyageStatus.ARRIVED:
        return "Not arrived yet"
    voyage.status = VoyageStatus.IN_PORT

    # Morale boost on port arrival
    from portlight.engine.ship_stats import tick_morale_at_port, has_special
    from portlight.content.upgrades import UPGRADES as _UPG
    has_cabin = has_special(world.captain.ship, "morale_bonus", _UPG)
    world.captain.ship.morale = tick_morale_at_port(world.captain.ship, has_cabin)

    # Convoy: dock in-transit fleet ships at destination
    for owned in world.captain.fleet:
        if owned.docked_port_id == "":  # in transit
            owned.docked_port_id = voyage.destination_id

    # Collect deferred fees on arrival
    captain = world.captain
    if captain.deferred_fees:
        collected = 0
        remaining = []
        for fee in captain.deferred_fees:
            if captain.silver >= fee["amount"]:
                captain.silver -= fee["amount"]
                collected += fee["amount"]
            else:
                remaining.append(fee)
        captain.deferred_fees = remaining

    return None
