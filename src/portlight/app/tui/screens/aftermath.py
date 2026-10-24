"""Aftermath screen — campaign writeback made visible (C3).

Shown after a fight resolves. It presents the existing after-action summary
(every state delta, no hidden changes) over the persistent captain bar. Any
key dismisses it back to the dashboard — it is never a clean reset, only an
acknowledgement of what the fight cost.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from portlight.app.tui.screens.dashboard import CaptainBar

if TYPE_CHECKING:
    from portlight.app.session import GameSession
    from portlight.engine.grid_combat import CombatResult


class AftermathScreen(Screen):
    """Post-combat writeback overlay. Any key continues (C3: no clean reset)."""

    BINDINGS = [
        Binding("escape", "continue", "Continue", priority=True),
        Binding("enter", "continue", "Continue", priority=True),
        Binding("space", "continue", "Continue", priority=True),
    ]

    def __init__(self, session: "GameSession", result: "CombatResult") -> None:
        super().__init__()
        self.session = session
        self.result = result
        self._dismissed = False

    def compose(self) -> ComposeResult:
        yield CaptainBar(self.session)
        yield Static("", id="aftermath-body")
        yield Footer()

    def on_mount(self) -> None:
        from portlight.app import sf_views

        self.query_one("#aftermath-body", Static).update(
            sf_views.after_action_summary(self.result, self.session.sf_campaign)
        )
        try:
            self.query_one("#captain-bar", CaptainBar).refresh_status()
        except Exception:
            pass

    def action_continue(self) -> None:
        if self._dismissed:
            return
        self._dismissed = True
        self.app.pop_screen()
        if hasattr(self.app, "refresh_views"):
            self.app.refresh_views()
        if hasattr(self.app, "action_switch_tab"):
            self.app.action_switch_tab("dashboard")
