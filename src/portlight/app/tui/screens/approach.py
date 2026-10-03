"""Approach screen — the encounter decision surface (C2).

Every interdiction opens here first: stakes (who, cargo, hull), then the three
approaches. Grid combat is only reached on Fight. A Veshan honor challenge
cannot skip the grid — Negotiate and Flee are closed.

Static keys (mirroring the ancestor encounter grammar): N negotiate, F flee,
G fight. The captain bar stays visible. This screen does not remap the
navigation tabs — D/C/R/M/T/J are no-ops while an interdiction is up (C1).
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


class ApproachScreen(Screen):
    """Stakes-first interdiction surface. Bindings match TUI_SURFACE_SPEC §5 / C2."""

    BINDINGS = [
        Binding("n", "negotiate", "Negotiate", priority=True),
        Binding("f", "flee", "Flee", priority=True),
        Binding("g", "fight", "Fight", priority=True),
        Binding("escape", "prompt", "Choose", show=False, priority=True),
    ]

    def __init__(self, session: "GameSession", encounter: dict) -> None:
        super().__init__()
        self.session = session
        self.encounter = encounter
        self._resolved = False
        from portlight.engine.sf_campaign import approach_encounter

        self.info = approach_encounter(session.sf_campaign, encounter)

    def compose(self) -> ComposeResult:
        yield CaptainBar(self.session)
        yield Static("", id="approach-body")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_body()

    def _refresh_body(self) -> None:
        from portlight.app import sf_views

        self.query_one("#approach-body", Static).update(
            sf_views.approach_panel(self.info)
        )
        try:
            self.query_one("#captain-bar", CaptainBar).refresh_status()
        except Exception:
            pass

    # ------------------------------------------------------------------ actions

    def action_prompt(self) -> None:
        """Esc does not dismiss an interdiction — you must choose."""
        if self._resolved:
            return
        self.app.notify(
            "You cannot ignore an interdiction. Choose: [N]egotiate, [F]lee, or [G] Fight.",
            severity="warning",
        )

    def action_negotiate(self) -> None:
        if self._resolved:
            return
        from portlight.engine.sf_campaign import negotiate_encounter

        result = negotiate_encounter(self.session.sf_campaign, self.encounter)
        if not result.get("resolved"):
            self.app.notify(result.get("error", "Cannot negotiate."), severity="warning")
            return
        self._resolved = True
        self._finish_social(result)

    def action_flee(self) -> None:
        if self._resolved:
            return
        from portlight.engine.sf_campaign import flee_encounter

        result = flee_encounter(self.session.sf_campaign, self.encounter)
        if not result.get("resolved"):
            self.app.notify(result.get("error", "Cannot flee."), severity="warning")
            return
        self._resolved = True
        self._finish_social(result)

    def action_fight(self) -> None:
        if self._resolved:
            return
        self._resolved = True
        from portlight.engine.sf_campaign import begin_combat
        from portlight.app.tui.screens.combat import CombatScreen

        combat = begin_combat(self.session.sf_campaign, self.encounter)
        # Replace this screen so combat sits directly on the dashboard and
        # pops back to it when it finishes (not back onto the approach).
        self.app.switch_screen(CombatScreen(self.session, combat, self.encounter))

    # ------------------------------------------------------------------ finish

    def _finish_social(self, result: dict) -> None:
        """Resolve a non-combat approach: save, toast the contrastive line, exit."""
        self.session._save()

        line = result.get("line", "")
        if result.get("outcome") == "negotiated":
            dest = result.get("destination_name")
            if dest:
                line = f"{line}  Docked {dest}."
        elif result.get("outcome") == "fled":
            lost = result.get("cargo_lost") or []
            if not lost:
                line = f"{line}  Voyage aborted."
            else:
                line = f"{line}  Voyage aborted."

        self.app.notify(line, timeout=8)
        self.app.pop_screen()
        if hasattr(self.app, "refresh_views"):
            self.app.refresh_views()
        if hasattr(self.app, "action_switch_tab"):
            self.app.action_switch_tab("dashboard")
