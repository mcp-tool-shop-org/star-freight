"""Sea culture engine — wires sea_culture content into the voyage system.

This module enriches voyage days with route-specific encounters, NPC sightings,
weather narratives, crew moods, and sea superstitions. It operates AFTER
advance_day() produces its base events, adding flavor events that make
every voyage feel unique.

Contract:
  enrich_voyage_day(world, route, events, rng) -> list[VoyageEvent]
    - Takes base events from advance_day()
    - Adds route encounters, NPC sightings, weather, crew mood
    - Returns enriched event list

  check_superstitions(world, cultural_state) -> list[SeaSuperstition]
    - Checks for one-time triggers
    - Returns newly fired superstitions
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from portlight.content.sea_culture import (
    get_npc_sightings,
    get_region_encounters,
    get_route_encounters,
    get_weather_narrative,
    SEA_SUPERSTITIONS,
    CREW_MOODS,
)
from portlight.engine.models import get_season
from portlight.engine.voyage import EventType, VoyageEvent

if TYPE_CHECKING:
    from portlight.content.sea_culture import (
        CrewMood,
        RouteEncounter,
        SeaSuperstition,
    )
    from portlight.engine.models import CulturalState, Route, WorldState


# ---------------------------------------------------------------------------
# Route-specific encounter injection
# ---------------------------------------------------------------------------

def _pick_route_encounter(
    route: "Route",
    dest_region: str,
    rng: random.Random,
) -> "RouteEncounter | None":
    """Pick a route-specific encounter if one exists, else try region default.

    ~25% chance of firing per day — route encounters are flavor, not every-day events.
    """
    if rng.random() > 0.25:
        return None

    table = None
    if route and route.lore_name:
        table = get_route_encounters(route.lore_name)

    if table is None:
        table = get_region_encounters(dest_region)

    if table is None or not table.encounters:
        return None

    return rng.choice(table.encounters)


# ---------------------------------------------------------------------------
# NPC sighting injection
# ---------------------------------------------------------------------------

def _pick_npc_sighting(
    dest_region: str,
    rng: random.Random,
) -> VoyageEvent | None:
    """Maybe spot a named NPC at sea. ~10% chance per day."""
    if rng.random() > 0.10:
        return None

    sightings = get_npc_sightings(dest_region)
    if not sightings:
        return None

    sighting = rng.choice(sightings)
    return VoyageEvent(
        event_type=EventType.FOREIGN_VESSEL,
        message=sighting.text,
        flavor=f"[{sighting.npc_name} from {sighting.port_id}]",
    )


# ---------------------------------------------------------------------------
# Weather narrative injection
# ---------------------------------------------------------------------------

def _pick_weather_flavor(
    dest_region: str,
    day: int,
    voyage_day: int,
    rng: random.Random,
) -> str:
    """Pick a weather flavor text based on region and season.

    Returns empty string if no narrative exists or dice don't fire (~30% chance).
    """
    if rng.random() > 0.30:
        return ""

    season = get_season(day)
    narrative = get_weather_narrative(dest_region, season.value)
    if narrative is None:
        return ""

    # Pick from mid-voyage texts (the most common)
    if narrative.mid_voyage_texts:
        return rng.choice(narrative.mid_voyage_texts)

    return ""


def get_departure_weather(region: str, day: int) -> str:
    """Get departure weather text for the start of a voyage."""
    season = get_season(day)
    narrative = get_weather_narrative(region, season.value)
    if narrative:
        return narrative.departure_text
    return ""


def get_arrival_weather(region: str, day: int, port_name: str = "") -> str:
    """Get arrival weather text for the end of a voyage."""
    season = get_season(day)
    narrative = get_weather_narrative(region, season.value)
    if narrative:
        text = narrative.arrival_text
        if port_name:
            # Replace generic subject at start of arrival text with port name
            for subject in [
                "The northern port", "The island port", "The port",
                "The island", "The harbor", "The lagoon",
            ]:
                if text.startswith(subject):
                    text = port_name + text[len(subject):]
                    break
        return text
    return ""


def get_night_weather(region: str, day: int) -> str:
    """Get night weather text."""
    season = get_season(day)
    narrative = get_weather_narrative(region, season.value)
    if narrative:
        return narrative.night_text
    return ""


# ---------------------------------------------------------------------------
# Crew mood injection
# ---------------------------------------------------------------------------

def _pick_crew_mood(
    world: "WorldState",
    rng: random.Random,
) -> str:
    """Check game state and return appropriate crew mood text, or empty string.

    ~20% chance of firing per day — crew commentary shouldn't overwhelm.
    """
    if rng.random() > 0.20:
        return ""

    captain = world.captain
    matching_moods: list[CrewMood] = []

    for mood in CREW_MOODS:
        # Check conditions against game state
        if mood.id == "prosperous" and captain.silver > 2000:
            matching_moods.append(mood)
        elif mood.id == "struggling" and captain.silver < 100:
            matching_moods.append(mood)
        elif mood.id == "first_voyage" and captain.day < 10:
            matching_moods.append(mood)
        elif mood.id == "veteran" and captain.day > 200:
            matching_moods.append(mood)
        elif mood.id == "carrying_contraband":
            has_contraband = any(
                c.good_id in ("opium", "black_powder", "stolen_cargo")
                for c in captain.cargo
            )
            if has_contraband:
                matching_moods.append(mood)
        elif mood.id == "calm_seas":
            # Check if the last event was calm or nothing
            pass  # This would need event context, skip for now
        elif mood.id == "new_ship":
            # Could track if ship was recently purchased
            pass

    if not matching_moods:
        return ""

    mood = rng.choice(matching_moods)
    return rng.choice(mood.flavor_texts)


# ---------------------------------------------------------------------------
# Sea superstition checking
# ---------------------------------------------------------------------------

def check_superstitions(
    world: "WorldState",
    cultural_state: "CulturalState",
    fired_superstitions: set[str],
) -> list["SeaSuperstition"]:
    """Check for superstition triggers. Returns newly fired ones.

    Each superstition fires once per game. The caller tracks which have fired
    via fired_superstitions set.
    """
    newly_fired: list[SeaSuperstition] = []
    captain = world.captain

    for sup in SEA_SUPERSTITIONS:
        if sup.id in fired_superstitions:
            continue

        fired = False

        # First-region entries
        if sup.trigger.startswith("first_region_"):
            target_region = sup.trigger.replace("first_region_", "")
            if target_region in cultural_state.regions_entered:
                # Check if this is a "recent" entry (entered this session)
                fired = True

        # Voyage event triggers
        elif sup.trigger == "survived_storm":
            # This would be checked after a storm event
            pass
        elif sup.trigger == "survived_pirates":
            pass

        # Cargo triggers
        elif sup.trigger == "carrying_sacred_good":
            from portlight.content.culture import REGION_CULTURES
            dest_port = world.ports.get(
                world.voyage.destination_id if world.voyage else ""
            )
            if dest_port:
                rc = REGION_CULTURES.get(dest_port.region)
                if rc:
                    for item in captain.cargo:
                        if item.good_id in rc.sacred_goods:
                            fired = True
                            break

        elif sup.trigger == "carrying_contraband":
            if any(c.good_id in ("opium", "black_powder", "stolen_cargo") for c in captain.cargo):
                fired = True

        # Milestone triggers
        elif sup.trigger == "day_100" and world.day == 100:
            fired = True
        elif sup.trigger == "visited_all_regions":
            if len(cultural_state.regions_entered) >= 5:
                fired = True

        if fired:
            newly_fired.append(sup)
            fired_superstitions.add(sup.id)

    return newly_fired


# ---------------------------------------------------------------------------
# Main enrichment function
# ---------------------------------------------------------------------------

def _is_recent(text: str, recent: list[str]) -> bool:
    """Check if text (or a close variant) was shown recently."""
    # Use first 60 chars as a fingerprint to catch same-text repeats
    fingerprint = text[:60].lower().strip()
    return any(fingerprint == r[:60].lower().strip() for r in recent)


def enrich_voyage_day(
    world: "WorldState",
    route: "Route | None",
    base_events: list[VoyageEvent],
    rng: random.Random,
) -> list[VoyageEvent]:
    """Enrich a day's voyage events with sea culture flavor.

    Call this AFTER advance_day() with the events it returned.
    Adds route encounters, NPC sightings, weather flavor, and crew mood
    as additional VoyageEvent entries.

    Returns the enriched list (original events + new flavor events).
    """
    enriched = list(base_events)
    recent = world.voyage.recent_events if world.voyage else []

    dest_port = world.ports.get(
        world.voyage.destination_id if world.voyage else ""
    )
    dest_region = dest_port.region if dest_port else "Mediterranean"
    voyage_day = world.voyage.days_elapsed if world.voyage else 0

    def _add_flavor(event: VoyageEvent) -> None:
        """Add a flavor event, skipping if text was shown recently."""
        if _is_recent(event.message, recent):
            return
        enriched.append(event)
        recent.append(event.message)
        # Keep only last 10 entries to prevent unbounded growth
        while len(recent) > 10:
            recent.pop(0)

    # 1. Route-specific encounter (~25% chance)
    route_enc = _pick_route_encounter(route, dest_region, rng)
    if route_enc:
        _add_flavor(VoyageEvent(
            event_type=EventType.NOTHING,
            message=route_enc.text,
            flavor=f"[{route_enc.category}]",
        ))

    # 2. NPC sighting (~10% chance)
    npc_event = _pick_npc_sighting(dest_region, rng)
    if npc_event:
        _add_flavor(npc_event)

    # 3. Weather flavor (~30% chance)
    weather_text = _pick_weather_flavor(dest_region, world.day, voyage_day, rng)
    if weather_text and not _is_recent(weather_text, recent):
        _add_flavor(VoyageEvent(
            event_type=EventType.NOTHING,
            message=weather_text,
            flavor="[weather]",
        ))

    # 4. Crew mood (~20% chance)
    mood_text = _pick_crew_mood(world, rng)
    if mood_text:
        _add_flavor(VoyageEvent(
            event_type=EventType.NOTHING,
            message=mood_text,
            flavor="[crew]",
        ))

    # 5. Consequence encounter (~15% chance, reads player history)
    from portlight.engine.consequences import apply_consequence, check_sea_consequences
    # Need ledger and board from session — passed via world if available
    try:
        # Consequences need ledger/board which aren't on WorldState
        # We check using a lightweight approach: just pass empty board/ledger
        # if not available (consequences that need them will simply not fire)
        from portlight.engine.contracts import ContractBoard
        from portlight.receipts.models import ReceiptLedger
        sea_consequences = check_sea_consequences(
            world, route, ReceiptLedger(), ContractBoard(), rng
        )
    except ImportError:
        sea_consequences = []

    for consequence in sea_consequences:
        apply_consequence(world, consequence)
        effect_note = ""
        if consequence.silver_delta > 0:
            effect_note = f" (+{consequence.silver_delta} silver)"
        elif consequence.silver_delta < 0:
            effect_note = f" ({consequence.silver_delta} silver)"
        elif consequence.heat_delta > 0:
            effect_note = f" (+{consequence.heat_delta} heat)"
        elif consequence.trust_delta < 0:
            effect_note = f" ({consequence.trust_delta} trust)"
        enriched.append(VoyageEvent(
            event_type=EventType.NOTHING,
            message=f"{consequence.text}{effect_note}",
            flavor=f"[consequence:{consequence.effect_type}]",
        ))

    return enriched
