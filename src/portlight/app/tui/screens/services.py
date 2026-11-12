"""Station services — numbered picker (the Portlight Harbor analogue).

Docked services (repair, refuel, hire) as a numbered menu. Steals the Harbor
interaction shape from Portlight, not its ocean identity. Pick by number or
name; each choice runs the existing campaign service and writes back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


class ServicesDialog(ModalScreen[str | None]):
    """Numbered station-services menu. Returns the chosen service id."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, options: list[tuple[str, str]]) -> None:
        super().__init__()
        # (service_id, label)
        self.options = options

    def compose(self) -> ComposeResult:
        with Vertical(id="input-area"):
            lines = ["[bold #f0c040]Station Services[/bold #f0c040]", ""]
            for i, (_sid, label) in enumerate(self.options, 1):
                lines.append(f"  [cyan]{i:2d}[/cyan]. {label}")
            lines.append("")
            yield Static("\n".join(lines))
            yield Input(placeholder="Enter number", id="service-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip().lower()
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(self.options):
                self.dismiss(self.options[idx][0])
                return
        for sid, label in self.options:
            if text and (text == sid or label.lower().startswith(text)):
                self.dismiss(sid)
                return
        self.notify(f"Unknown: {text}", severity="warning")

    def action_cancel(self) -> None:
        self.dismiss(None)


def _build_options(state) -> list[tuple[str, str]]:
    from portlight.content.star_freight import (
        SLICE_STATIONS,
        STATION_HIRES,
        create_crew,
    )

    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return []

    options: list[tuple[str, str]] = []

    if "repair" in station.services or "drydock" in station.services:
        need = state.ship_hull_max - state.ship_hull
        if need > 0:
            options.append(
                ("repair", f"Repair hull \u2014 {station.repair_cost_per_point}\u20a1/pt, {need} needed")
            )

    if "fuel" in station.services:
        need = state.ship_fuel_max - state.ship_fuel
        if need > 0:
            options.append(
                ("refuel", f"Refuel \u2014 {station.fuel_cost_per_day}\u20a1/day, {need}d needed")
            )

    if "crew_hire" in station.services:
        for cid in STATION_HIRES.get(state.current_station, []):
            try:
                member = create_crew(cid)
            except Exception:
                continue
            if any(m.id == member.id for m in state.crew.members):
                continue
            options.append(
                (
                    f"hire:{cid}",
                    f"Hire {member.name} [{member.role.value}] \u2014 {member.pay_rate}\u20a1/mo",
                )
            )

    return options


def _run_service(app, session: "GameSession", choice: str) -> None:
    from portlight.content.star_freight import SLICE_STATIONS
    from portlight.engine.sf_campaign import repair_ship, refuel, hire_crew

    state = session.sf_campaign
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return

    if choice == "repair":
        cost_per = max(1, station.repair_cost_per_point)
        need = state.ship_hull_max - state.ship_hull
        pts = min(need, state.credits // cost_per)
        if pts <= 0:
            app.notify("Can't afford any repairs.", severity="warning")
            return
        result = repair_ship(state, pts)
        if result.get("error"):
            app.notify(result["error"], severity="warning")
            return
        app.notify(
            f"Repaired {result['repaired']} hull for {result['cost']}\u20a1.", timeout=4
        )
    elif choice == "refuel":
        cost_per = max(1, station.fuel_cost_per_day)
        need = state.ship_fuel_max - state.ship_fuel
        days = min(need, state.credits // cost_per)
        if days <= 0:
            app.notify("Can't afford fuel.", severity="warning")
            return
        result = refuel(state, days)
        if result.get("error"):
            app.notify(result["error"], severity="warning")
            return
        app.notify(f"Refueled {result['fueled']}d for {result['cost']}\u20a1.", timeout=4)
    elif choice.startswith("hire:"):
        crew_id = choice.split(":", 1)[1]
        result = hire_crew(state, crew_id)
        if result.get("error"):
            app.notify(result["error"], severity="warning")
            return
        app.notify(f"Hired {result['hired']} for {result['cost']}\u20a1.", timeout=4)
    else:
        return

    session._save()
    if hasattr(app, "refresh_views"):
        app.refresh_views()


def execute_services_flow(app, session: "GameSession") -> None:
    """Open the numbered station-services picker."""
    state = session.sf_campaign
    if state is None:
        app.notify("No active game.", severity="warning")
        return
    if state.in_transit:
        app.notify("In transit \u2014 dock first.", severity="warning")
        return

    from portlight.content.star_freight import SLICE_STATIONS

    if SLICE_STATIONS.get(state.current_station) is None:
        app.notify("Not at a station.", severity="warning")
        return

    options = _build_options(state)
    if not options:
        app.notify("No services available here right now.", severity="information")
        return

    def on_pick(choice: str | None) -> None:
        if choice:
            _run_service(app, session, choice)

    app.push_screen(ServicesDialog(options), on_pick)
