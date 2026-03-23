"""Port arrival engine — generates the full arrival experience.

When a captain docks at a port, they should meet the harbor master, see
the dock scene, hear the local custom, get a festival banner if one is
active, and feel the port's institutional personality.

Contract:
  generate_arrival(world, port_id) -> PortArrivalExperience
    - Uses institutional profiles for NPC greetings
    - Uses culture data for dock scene and customs
    - Uses sea_culture_engine for arrival weather
    - Checks captain standing for greeting tone
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portlight.engine.models import WorldState


@dataclass
class PortArrivalExperience:
    """Complete arrival experience bundle — everything the player sees when docking."""
    port_id: str
    port_name: str
    region: str
    # Atmospheric
    dock_scene: str = ""
    arrival_weather: str = ""
    # NPC greetings
    harbor_master_greeting: str = ""
    harbor_master_name: str = ""
    exchange_greeting: str = ""
    exchange_name: str = ""
    tavern_greeting: str = ""
    tavern_name: str = ""
    # Cultural
    local_custom: str = ""
    landmark: str = ""
    tavern_rumor: str = ""
    cultural_group: str = ""
    # Political
    political_flavor: str = ""
    port_grudge: str = ""
    # Festival
    active_festival_name: str = ""
    active_festival_description: str = ""
    # Mentor (if this is the captain's home port and they have a mentor)
    mentor_greeting: str = ""
    mentor_name: str = ""


def _get_standing_tier(standing: int) -> str:
    """Classify standing into greeting tier."""
    if standing >= 15:
        return "friendly"
    elif standing >= 0:
        return "neutral"
    else:
        return "hostile"


def generate_arrival(world: "WorldState", port_id: str) -> PortArrivalExperience:
    """Generate the full arrival experience for a port.

    Pulls from:
    - Port institutional profiles (NPC greetings)
    - Port culture (dock scene, customs, landmarks)
    - Port politics (political flavor, grudge)
    - Sea culture engine (arrival weather)
    - Captain template (mentor connection)
    """
    port = world.ports.get(port_id)
    if port is None:
        return PortArrivalExperience(port_id=port_id, port_name="Unknown", region="Unknown")

    experience = PortArrivalExperience(
        port_id=port_id,
        port_name=port.name,
        region=port.region,
    )

    # --- Standing tier for greeting selection ---
    captain = world.captain
    regional_standing = captain.standing.regional_standing.get(port.region, 0)
    port_standing = captain.standing.port_standing.get(port_id, 0)
    effective_standing = max(regional_standing, port_standing)
    tier = _get_standing_tier(effective_standing)

    # --- Culture data ---
    try:
        from portlight.content.culture import PORT_CULTURES
        pc = PORT_CULTURES.get(port_id)
        if pc:
            experience.dock_scene = pc.dock_scene
            experience.local_custom = pc.local_custom
            experience.landmark = pc.landmark
            experience.tavern_rumor = pc.tavern_rumor
            experience.cultural_group = pc.cultural_group
    except ImportError:
        pass

    # --- Institutional profiles ---
    try:
        from portlight.content.port_institutions import PORT_INSTITUTIONAL_PROFILES
        profile = PORT_INSTITUTIONAL_PROFILES.get(port_id)
        if profile:
            for npc in profile.npcs:
                greeting = {
                    "friendly": npc.greeting_friendly,
                    "neutral": npc.greeting_neutral,
                    "hostile": npc.greeting_hostile,
                }.get(tier, npc.greeting_neutral)

                if npc.institution == "harbor_master":
                    experience.harbor_master_greeting = greeting
                    experience.harbor_master_name = npc.name
                elif npc.institution == "exchange":
                    experience.exchange_greeting = greeting
                    experience.exchange_name = npc.name
                elif npc.institution == "tavern":
                    experience.tavern_greeting = greeting
                    experience.tavern_name = npc.name
    except ImportError:
        pass

    # --- Port politics ---
    try:
        from portlight.content.port_politics import PORT_POLITICS
        politics = PORT_POLITICS.get(port_id)
        if politics:
            experience.political_flavor = politics.political_flavor
            experience.port_grudge = politics.port_grudge
    except ImportError:
        pass

    # --- Arrival weather ---
    try:
        from portlight.engine.sea_culture_engine import get_arrival_weather
        weather = get_arrival_weather(port.region, world.day)
        if weather:
            experience.arrival_weather = weather
    except ImportError:
        pass

    # --- Active festival ---
    for af in world.culture.active_festivals:
        if af.port_id == port_id and af.start_day <= world.day <= af.end_day:
            try:
                from portlight.content.culture import REGION_CULTURES
                rc = REGION_CULTURES.get(port.region)
                if rc:
                    for f in rc.festivals:
                        if f.id == af.festival_id:
                            experience.active_festival_name = f.name
                            experience.active_festival_description = f.description
                            break
            except ImportError:
                pass
            break

    # --- Mentor greeting (if this is captain's home port) ---
    try:
        from portlight.engine.captain_identity import CAPTAIN_TEMPLATES, CaptainType
        ct = CaptainType(captain.captain_type)
        template = CAPTAIN_TEMPLATES.get(ct)
        if template and template.mentor_npc_id and template.home_port_id == port_id:
            from portlight.content.port_institutions import ALL_NPCS
            mentor = ALL_NPCS.get(template.mentor_npc_id)
            if mentor:
                experience.mentor_name = mentor.name
                experience.mentor_greeting = {
                    "friendly": mentor.greeting_friendly,
                    "neutral": mentor.greeting_neutral,
                    "hostile": mentor.greeting_hostile,
                }.get(tier, mentor.greeting_friendly)
    except (ImportError, ValueError, KeyError):
        pass

    return experience


def format_arrival_text(exp: PortArrivalExperience) -> list[str]:
    """Format the arrival experience into displayable text lines.

    Returns a list of strings ready for Rich console output.
    """
    lines: list[str] = []

    lines.append(f"[bold]You arrive at {exp.port_name}.[/bold]")
    lines.append("")

    if exp.arrival_weather:
        lines.append(exp.arrival_weather)
        lines.append("")

    if exp.dock_scene:
        lines.append(exp.dock_scene)
        lines.append("")

    if exp.harbor_master_greeting:
        lines.append(f"[bold]{exp.harbor_master_name}:[/bold] {exp.harbor_master_greeting}")

    if exp.mentor_greeting and exp.mentor_name != exp.harbor_master_name:
        lines.append(f"[bold]{exp.mentor_name}:[/bold] {exp.mentor_greeting}")

    if exp.active_festival_name:
        lines.append("")
        lines.append(f"[bold yellow]FESTIVAL: {exp.active_festival_name}[/bold yellow]")
        lines.append(exp.active_festival_description)

    if exp.landmark:
        lines.append("")
        lines.append(f"[dim]Landmark: {exp.landmark}[/dim]")

    if exp.local_custom:
        lines.append(f"[dim]Custom: {exp.local_custom}[/dim]")

    return lines
