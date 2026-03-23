"""Routes and voyage screens — maritime-themed navigation.

Features:
- Danger skulls in route selection
- Region badges in destination list
- Voyage event classification with icons
- Day advance with atmospheric notifications
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class SailDialog(ModalScreen[str | None]):
    """Destination selection with danger indicators and travel time."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, destinations: list[tuple[str, str, int, float, str, int]]) -> None:
        super().__init__()
        # (port_id, port_name, distance, danger, region, est_days)
        self.destinations = destinations

    def compose(self) -> ComposeResult:
        from portlight.app.tui.theme import danger_indicator, REGION_BADGES

        with Vertical(id="input-area"):
            lines = ["[bold #e9c46a]\u2693 Set Course[/bold #e9c46a]", ""]
            for i, (pid, name, dist, danger, region, days) in enumerate(self.destinations, 1):
                badge = REGION_BADGES.get(region, "")
                skull = danger_indicator(danger)
                lines.append(
                    f"  [cyan]{i:2d}[/cyan]. {name:18s} {badge} "
                    f"[dim]{dist} lg[/dim]  [cyan]{days}d[/cyan]  {skull}"
                )
            lines.append("")
            yield Static("\n".join(lines))
            yield Input(placeholder="Enter port name or number", id="dest-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip().lower()
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(self.destinations):
                self.dismiss(self.destinations[idx][0])
                return
        for pid, name, *_ in self.destinations:
            if text == pid or text == name.lower():
                self.dismiss(pid)
                return
        for pid, name, *_ in self.destinations:
            if name.lower().startswith(text):
                self.dismiss(pid)
                return
        self.notify(f"Unknown: {text}", severity="warning")

    def action_cancel(self) -> None:
        self.dismiss(None)


def execute_sail_flow(app, session: "GameSession") -> None:
    """Launch the sail flow with maritime-themed destination picker."""
    if session.at_sea:
        app.notify("\u2693 Already at sea. Press A to advance.", severity="warning")
        return
    port = session.current_port
    if not port:
        app.notify("\u2693 Not docked at a port.", severity="warning")
        return

    w = session.world
    speed = w.captain.ship.speed if w.captain.ship else 5
    destinations = []
    for route in w.routes:
        if route.port_a == port.id:
            dest = w.ports.get(route.port_b)
            if dest:
                region = dest.region if hasattr(dest, "region") else ""
                days = max(1, round(route.distance / speed))
                destinations.append((dest.id, dest.name, route.distance, route.danger, region, days))
        elif route.port_b == port.id:
            dest = w.ports.get(route.port_a)
            if dest:
                region = dest.region if hasattr(dest, "region") else ""
                days = max(1, round(route.distance / speed))
                destinations.append((dest.id, dest.name, route.distance, route.danger, region, days))

    if not destinations:
        app.notify("No routes from this port.", severity="warning")
        return

    destinations.sort(key=lambda d: d[2])

    def on_dest(dest_id: str | None) -> None:
        if dest_id is None:
            return
        err = session.sail(dest_id)
        if err:
            app.notify(f"\u2717 {err}", severity="error")
        else:
            dest = w.ports.get(dest_id)
            dest_name = dest.name if dest else dest_id
            app.notify(
                f"\u2693 Set sail for {dest_name}! Fair winds, Captain.",
                severity="information",
                timeout=5,
            )
            app.action_switch_tab("dashboard")
            app.refresh_views()

    app.push_screen(SailDialog(destinations), on_dest)


# Voyage event icons
_EVENT_ICONS = {
    "arrival": "\u2693",      # anchor
    "pirate": "\u2620",       # skull
    "storm": "\u26c8",        # thunder
    "inspection": "\u2696",   # scales
    "market_tick": "\u25cf",  # dot
    "calm": "\u263c",         # sun
    "fog": "\u2601",          # cloud
    "wind": "\u2708",         # wind/plane
}


def execute_advance(app, session: "GameSession") -> None:
    """Advance one day with atmospheric event notifications."""
    if not session.active:
        app.notify("No active game.", severity="warning")
        return

    was_at_sea = session.at_sea

    events = session.advance()

    if events:
        for ev in events:
            severity = "information"
            icon = "\u25cf"

            if hasattr(ev, "event_type"):
                from portlight.engine.voyage import EventType
                etype = ev.event_type
                if etype == EventType.PIRATES:
                    severity = "error"
                    icon = "\u2620"
                elif etype == EventType.STORM:
                    severity = "warning"
                    icon = "\u26c8"
                elif etype == EventType.INSPECTION:
                    severity = "warning"
                    icon = "\u2696"
                else:
                    icon = _EVENT_ICONS.get(etype.value, "\u25cf") if hasattr(etype, "value") else "\u25cf"

            desc = str(ev.description) if hasattr(ev, "description") else str(ev)
            app.notify(f"{icon} {desc}", severity=severity, timeout=6)
    else:
        if session.at_sea:
            app.notify(
                f"\u263c Day {session.world.day} — calm seas, steady progress.",
                timeout=3,
            )
        else:
            app.notify(
                f"\u2693 Day {session.world.day} — idle in port.",
                timeout=3,
            )

    # Check for pirate encounter
    if events:
        for ev in events:
            if hasattr(ev, "_pending_duel") and ev._pending_duel is not None:
                from portlight.engine.encounter import create_encounter
                enc = create_encounter(
                    session.world.ports,
                    session.world.voyage.destination_id if session.world.voyage else "porto_novo",
                    session._rng,
                )
                if enc:
                    pd = ev._pending_duel
                    enc.enemy_captain_id = pd.captain_id
                    enc.enemy_captain_name = pd.captain_name
                    enc.enemy_faction_id = pd.faction_id
                    enc.enemy_personality = pd.personality
                    enc.enemy_strength = pd.strength
                    enc.enemy_region = pd.region

                    from portlight.app.tui.screens.encounter import EncounterScreen
                    app.push_screen(EncounterScreen(session, enc))
                    return  # Encounter takes over

    # Auto-switch to dashboard on arrival
    if was_at_sea and not session.at_sea:
        app.action_switch_tab("dashboard")

    app.refresh_views()
