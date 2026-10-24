"""Startup — save-slot picker and new-captain entry (Item 4b).

Steals the Portlight save-picker grammar: on launch (when no save auto-loads)
the captain chooses which life to continue or starts a new one. Not the ocean
identity — just the interaction shape.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_-]+", "_", name.lower()).strip("_")
    return slug or "default"


class NewGameDialog(ModalScreen[str | None]):
    """Name a new captain."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Vertical(id="input-area"):
            yield Static(
                "[bold #f0c040]New captain[/bold #f0c040]\n\n"
                "  A disgraced pilot with a bad ship and no standing.\n"
                "  Name them."
            )
            yield Input(placeholder="Captain name", id="name-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        name = event.value.strip()
        if name:
            self.dismiss(name)
        else:
            self.notify("Enter a name.", severity="warning")

    def action_cancel(self) -> None:
        self.dismiss(None)


class SlotPickerScreen(ModalScreen[None]):
    """Choose a saved captain to continue, or start a new one."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__()
        self.session = session
        from portlight.app.session import list_star_freight_saves

        self.slots = list_star_freight_saves(session.base_path)

    def compose(self) -> ComposeResult:
        from portlight.content.star_freight import SLICE_STATIONS

        with Vertical(id="input-area"):
            lines = ["[bold #f0c040]Star Freight \u2014 choose a captain[/bold #f0c040]", ""]
            for i, s in enumerate(self.slots, 1):
                station = SLICE_STATIONS.get(s["station"])
                where = station.name if station else (s["station"] or "in transit")
                lines.append(
                    f"  [cyan]{i:2d}[/cyan]. [bold]{s['captain_name']}[/bold]  "
                    f"[dim]day {s['day']} \u00b7 {where} \u00b7 {s['credits']}\u20a1 \u00b7 ({s['slot']})[/dim]"
                )
            if not self.slots:
                lines.append("  [dim]No saved captains yet.[/dim]")
            lines.append("")
            lines.append("  [cyan] n[/cyan]. New captain")
            lines.append("")
            yield Static("\n".join(lines))
            yield Input(placeholder="Number, name, or 'n' for new", id="slot-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip().lower()
        if text in ("n", "new"):
            self._new_game()
            return
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(self.slots):
                self._load(self.slots[idx]["slot"])
                return
        for s in self.slots:
            if text and (text == s["slot"].lower() or s["captain_name"].lower().startswith(text)):
                self._load(s["slot"])
                return
        self.notify(f"Unknown: {text}", severity="warning")

    def _load(self, slot: str) -> None:
        self.session.switch_slot(slot)
        self.session.load()
        self.app.pop_screen()
        self._refresh()

    def _new_game(self) -> None:
        def on_name(name: str | None) -> None:
            if not name:
                return
            self.session.switch_slot(_slug(name))
            self.session.new(name)
            self.app.pop_screen()  # remove the slot picker (NewGameDialog already popped)
            self._refresh()

        self.app.push_screen(NewGameDialog(), on_name)

    def _refresh(self) -> None:
        if hasattr(self.app, "refresh_views"):
            self.app.refresh_views()
        if hasattr(self.app, "action_switch_tab"):
            self.app.action_switch_tab("dashboard")
