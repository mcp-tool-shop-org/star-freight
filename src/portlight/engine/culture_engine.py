"""Culture engine — arrival flavor, festival management, cultural goods checks.

Pure functions that operate on cultural state and content data.
No side effects — callers decide what to mutate.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from portlight.content.culture import PORT_CULTURES, REGION_CULTURES
from portlight.engine.models import ActiveFestival, CulturalState, Festival


@dataclass
class ArrivalFlavor:
    """Cultural arrival text bundle returned to the session/view layer."""
    dock_scene: str
    greeting: str
    landmark: str
    cultural_note: str
    active_festival: Festival | None
    tavern_rumor: str


def generate_arrival_flavor(
    port_id: str,
    region: str,
    captain_standing: int,
    day: int,
    cultural_state: CulturalState,
) -> ArrivalFlavor | None:
    """Generate cultural arrival text for a port.

    Returns None if no culture data exists for this port.
    """
    pc = PORT_CULTURES.get(port_id)
    rc = REGION_CULTURES.get(region)
    if pc is None:
        return None

    # Standing-aware greeting
    if rc:
        if captain_standing >= 20:
            greeting = f"The harbor erupts in welcome. {rc.greeting}"
        elif captain_standing >= 10:
            greeting = rc.greeting
        elif captain_standing >= 0:
            greeting = f"A dock clerk nods curtly. {rc.greeting}"
        else:
            greeting = "The dockworkers eye you with suspicion. No greeting is offered."
    else:
        greeting = ""

    # Check for active festival
    active_fest = None
    for af in cultural_state.active_festivals:
        if af.port_id == port_id and af.start_day <= day <= af.end_day:
            # Find the Festival definition
            if rc:
                for f in rc.festivals:
                    if f.id == af.festival_id:
                        active_fest = f
                        break
            break

    cultural_note = pc.local_custom

    return ArrivalFlavor(
        dock_scene=pc.dock_scene,
        greeting=greeting,
        landmark=pc.landmark,
        cultural_note=cultural_note,
        active_festival=active_fest,
        tavern_rumor=pc.tavern_rumor,
    )


def check_festival_trigger(
    region: str,
    day: int,
    rng: random.Random,
    cultural_state: CulturalState,
) -> list[tuple[Festival, str]]:
    """Check if any festivals should trigger in this region.

    Returns list of (festival, port_id) pairs that should become active.
    Festival triggering is stochastic based on frequency_days.
    """
    rc = REGION_CULTURES.get(region)
    if rc is None:
        return []

    triggered: list[tuple[Festival, str]] = []
    for festival in rc.festivals:
        # Don't trigger if already active
        already_active = any(
            af.festival_id == festival.id
            for af in cultural_state.active_festivals
        )
        if already_active:
            continue

        # Stochastic trigger: probability = 1/frequency per day
        if rng.random() < (1.0 / festival.frequency_days):
            # Pick a port in this region for the festival
            from portlight.content.ports import PORTS
            region_ports = [p for p in PORTS.values() if p.region == region]
            if region_ports:
                port = rng.choice(region_ports)
                triggered.append((festival, port.id))

    return triggered


def activate_festival(
    festival: Festival,
    port_id: str,
    day: int,
    cultural_state: CulturalState,
) -> ActiveFestival:
    """Create and register an active festival."""
    af = ActiveFestival(
        festival_id=festival.id,
        port_id=port_id,
        start_day=day,
        end_day=day + festival.duration_days,
    )
    cultural_state.active_festivals.append(af)
    return af


def expire_festivals(day: int, cultural_state: CulturalState) -> list[ActiveFestival]:
    """Remove expired festivals. Returns list of expired ones."""
    expired = [af for af in cultural_state.active_festivals if day > af.end_day]
    cultural_state.active_festivals = [
        af for af in cultural_state.active_festivals if day <= af.end_day
    ]
    return expired


def record_port_visit(port_id: str, region: str, cultural_state: CulturalState) -> None:
    """Track a port visit and first-time region entry."""
    cultural_state.port_visits[port_id] = cultural_state.port_visits.get(port_id, 0) + 1
    if region not in cultural_state.regions_entered:
        cultural_state.regions_entered.append(region)


def record_cultural_encounter(cultural_state: CulturalState) -> None:
    """Increment cultural encounter counter."""
    cultural_state.cultural_encounters += 1


# ---------------------------------------------------------------------------
# Sacred / forbidden goods
# ---------------------------------------------------------------------------

def check_sacred_good_bonus(good_id: str, region: str) -> int:
    """Standing bonus for delivering a sacred good to its home region."""
    rc = REGION_CULTURES.get(region)
    if rc and good_id in rc.sacred_goods:
        return 2
    return 0


def check_forbidden_good_penalty(good_id: str, region: str) -> int:
    """Heat penalty for selling a forbidden good in a region."""
    rc = REGION_CULTURES.get(region)
    if rc and good_id in rc.forbidden_goods:
        return 3
    return 0


def get_cultural_good_note(good_id: str, region: str) -> str | None:
    """Cultural note about a good in a region, or None."""
    rc = REGION_CULTURES.get(region)
    if rc is None:
        return None
    if good_id in rc.sacred_goods:
        _SACRED_NOTES = {
            "grain": "sacred - never let a city starve",
            "medicines": "sacred - the north remembers its plagues",
            "pearls": "sacred - gift from the sea",
            "porcelain": "sacred - master craftsmen are revered",
            "silk": "sacred - a thousand years of weaving",
        }
        return _SACRED_NOTES.get(good_id, "sacred")
    if good_id in rc.forbidden_goods:
        _FORBIDDEN_NOTES = {
            "weapons": "forbidden - banned by decree",
        }
        return _FORBIDDEN_NOTES.get(good_id, "forbidden")
    if good_id in rc.prized_goods:
        return "prized"
    return None
