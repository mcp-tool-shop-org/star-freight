"""StarFreightApp — main Textual application.

Launches with GameSession, shows dashboard with captain pressure bar
and tab-switchable content area. Keyboard-driven navigation.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding

from portlight.app.session import GameSession
from portlight.app.tui.theme import APP_CSS


class StarFreightApp(App):
    """Star Freight interactive terminal UI."""

    TITLE = "Star Freight"
    CSS = APP_CSS

    BINDINGS = [
        # Navigation tabs — Star Freight screen set
        Binding("d", "switch_tab('dashboard')", "Dashboard", priority=True),
        Binding("c", "switch_tab('crew')", "Crew", priority=True),
        Binding("r", "switch_tab('routes')", "Routes", priority=True),
        Binding("m", "switch_tab('market')", "Market", priority=True),
        Binding("t", "switch_tab('station')", "Station", priority=True),
        Binding("j", "switch_tab('journal')", "Journal", priority=True),
        Binding("f", "switch_tab('faction')", "Faction", priority=True),
        Binding("question_mark", "switch_tab('help')", "Help", priority=True),
        # Actions
        Binding("b", "buy", "Buy", priority=True),
        Binding("s", "sell", "Sell", priority=True),
        Binding("g", "travel", "Travel", priority=True),
        Binding("a", "advance", "Advance", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        # Encounter-specific keys (only active when EncounterScreen is pushed)
        Binding("n", "encounter_dispatch('negotiate')", show=False, priority=True),
        Binding("z", "encounter_dispatch('slash')", show=False, priority=True),
        Binding("x", "encounter_dispatch('parry')", show=False, priority=True),
        Binding("o", "encounter_dispatch('shoot')", show=False, priority=True),
        Binding("e", "encounter_dispatch('evade')", show=False, priority=True),
    ]

    def __init__(self, session: GameSession | None = None) -> None:
        super().__init__()
        self.session = session or GameSession()
        self._current_tab = "dashboard"

    @property
    def _encounter_screen(self):
        """Return the active EncounterScreen if one is pushed, else None."""
        from portlight.app.tui.screens.encounter import EncounterScreen
        if isinstance(self.screen, EncounterScreen):
            return self.screen
        return None

    def compose(self) -> ComposeResult:
        from portlight.app.tui.screens.dashboard import DashboardScreen
        yield DashboardScreen(self.session)

    def on_mount(self) -> None:
        if not self.session.active:
            if not self.session.load():
                self.notify(
                    "No save found. Run 'portlight new <name>' first, then 'portlight tui'.",
                    severity="error",
                    timeout=8,
                )

    def action_encounter_dispatch(self, key: str) -> None:
        """Dispatch encounter-specific keys to EncounterScreen."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key(key)

    def action_switch_tab(self, tab: str) -> None:
        """Switch the content area to a different tab."""
        enc = self._encounter_screen
        if enc:
            # Remap tab keys to encounter actions during combat
            _remap = {
                "faction": "flee",       # f → flee
                "crew": "close",         # c → close range
                "routes": "rake",        # r → rake
                "station": "thrust",     # t → thrust
            }
            if tab in _remap:
                enc.action_encounter_key(_remap[tab])
            return  # Block all tab switches during encounter
        if not self.session.active:
            self.notify("No active game.", severity="warning")
            return
        self._current_tab = tab
        dashboard = self.query_one("DashboardScreen", expect_type=None)
        if dashboard is not None:
            dashboard.switch_tab(tab)

    def action_buy(self) -> None:
        """Open buy dialog. During encounter: dispatches to encounter."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("broadside")
            return
        if not self.session.active:
            return
        from portlight.app.tui.screens.market import execute_buy_flow
        execute_buy_flow(self, self.session)

    def action_sell(self) -> None:
        """Open sell dialog. During encounter: dispatches to encounter."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("spare")
            return
        if not self.session.active:
            return
        from portlight.app.tui.screens.market import execute_sell_flow
        execute_sell_flow(self, self.session)

    def action_travel(self) -> None:
        """Open travel/route selection. During encounter: dispatches fight."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("fight")
            return
        if not self.session.active:
            return
        if self.session.world and self.session.world.pirates.pending_duel is not None:
            self.notify("Resolve the encounter first!", severity="warning")
            return
        from portlight.app.tui.screens.routes import execute_sail_flow
        execute_sail_flow(self, self.session)

    def action_advance(self) -> None:
        """Advance one day. During encounter: dispatches to encounter."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("take_all")
            return
        if not self.session.active:
            return
        if self.session.world and self.session.world.pirates.pending_duel is not None:
            self.notify("Resolve the encounter first!", severity="warning")
            return
        from portlight.app.tui.screens.routes import execute_advance
        execute_advance(self, self.session)

    def refresh_views(self) -> None:
        """Refresh all visible views after a state mutation."""
        dashboard = self.query_one("DashboardScreen", expect_type=None)
        if dashboard is not None:
            dashboard.refresh_all()


# Backward-compatible alias for tests that still import the old name
PortlightApp = StarFreightApp
