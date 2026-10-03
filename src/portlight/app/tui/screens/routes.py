"""Routes screen — pick a lane and travel, or idle a day at station."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class SailDialog(ModalScreen[str | None]):
    """Destination selection with danger and travel time."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, destinations: list[tuple[str, str, int, float, str, int]]) -> None:
        super().__init__()
        # (station_id, name, distance_days, danger, civ, est_days)
        self.destinations = destinations

    def compose(self) -> ComposeResult:
        from portlight.app.tui.theme import danger_indicator

        with Vertical(id="input-area"):
            lines = ["[bold #f0c040]Set course[/bold #f0c040]", ""]
            for i, (_pid, name, dist, danger, civ, days) in enumerate(self.destinations, 1):
                skull = danger_indicator(danger)
                lines.append(
                    f"  [cyan]{i:2d}[/cyan]. {name:18s} [dim]{civ}[/dim]  "
                    f"[cyan]{days}d[/cyan]  {skull}"
                )
            lines.append("")
            yield Static("\n".join(lines))
            yield Input(placeholder="Enter station name or number", id="dest-input")

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
    """Travel along an overlay lane."""
    state = session.sf_campaign
    if state is None:
        app.notify("No active game.", severity="warning")
        return
    if state.in_transit:
        app.notify("Already in transit. Resolve the encounter or wait.", severity="warning")
        return

    from portlight.content.star_freight import SLICE_STATIONS, SLICE_LANES
    from portlight.engine.sf_campaign import travel_to

    here = state.current_station
    destinations = []
    for lane in SLICE_LANES.values():
        other = None
        if lane.station_a == here:
            other = lane.station_b
        elif lane.station_b == here:
            other = lane.station_a
        if not other:
            continue
        dest = SLICE_STATIONS.get(other)
        if not dest:
            continue
        destinations.append((
            dest.id, dest.name, lane.distance_days, lane.danger,
            dest.civilization, lane.distance_days,
        ))

    if not destinations:
        app.notify("No lanes from this station.", severity="warning")
        return

    destinations.sort(key=lambda d: d[2])

    def on_dest(dest_id: str | None) -> None:
        if dest_id is None:
            return
        result = travel_to(state, dest_id)
        if result.get("error"):
            app.notify(result["error"], severity="error")
            session._save()
            app.refresh_views()
            return
        dest = SLICE_STATIONS.get(dest_id)
        dest_name = dest.name if dest else dest_id
        enc = result.get("encounter")
        if enc:
            app.notify(f"Interdicted en route to {dest_name}.", severity="warning")
            # C2: open the approach surface first — stakes, then negotiate /
            # flee / fight. The grid is only reached if the captain chooses Fight.
            from portlight.app.tui.screens.approach import ApproachScreen
            app.push_screen(ApproachScreen(session, enc))
            return
        else:
            app.notify(f"Arrived at {dest_name}.", severity="information", timeout=5)
        session._save()
        app.action_switch_tab("dashboard")
        app.refresh_views()

    app.push_screen(SailDialog(destinations), on_dest)


def execute_advance(app, session: "GameSession") -> None:
    """Idle one day at the current station."""
    state = session.sf_campaign
    if state is None:
        app.notify("No active game.", severity="warning")
        return

    from portlight.engine.sf_campaign import advance_docked

    result = advance_docked(state)
    if result.get("error"):
        app.notify(result["error"], severity="warning")
        return
    app.notify(f"Day {result['day']} at dock.", timeout=3)
    session._save()
    app.refresh_views()
