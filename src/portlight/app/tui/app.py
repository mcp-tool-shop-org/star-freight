"""PortlightApp — main Textual application.

Launches with GameSession, shows dashboard with status sidebar
and tab-switchable content area. Keyboard-driven navigation.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding

from portlight.app.session import GameSession
from portlight.app.tui.theme import APP_CSS


class PortlightApp(App):
    """Portlight interactive terminal UI."""

    TITLE = "Portlight"
    CSS = APP_CSS

    BINDINGS = [
        Binding("d", "switch_tab('dashboard')", "Dashboard", priority=True),
        Binding("m", "switch_tab('market')", "Market", priority=True),
        Binding("r", "switch_tab('routes')", "Routes", priority=True),
        Binding("c", "switch_tab('cargo')", "Cargo", priority=True),
        Binding("i", "switch_tab('inventory')", "Inventory", priority=True),
        Binding("f", "switch_tab('fleet')", "Fleet", priority=True),
        Binding("k", "switch_tab('contracts')", "Contracts", priority=True),
        Binding("p", "switch_tab('port')", "Port", priority=True),
        Binding("l", "switch_tab('ledger')", "Ledger", priority=True),
        Binding("w", "switch_tab('infrastructure')", "Infra", priority=True),
        Binding("v", "switch_tab('map')", "Map", priority=True),
        Binding("question_mark", "switch_tab('help')", "Help", priority=True),
        Binding("b", "buy", "Buy", priority=True),
        Binding("s", "sell", "Sell", priority=True),
        Binding("g", "sail", "Sail", priority=True),
        Binding("a", "advance", "Advance", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        # Encounter-specific keys (only active when EncounterScreen is pushed)
        Binding("n", "encounter_dispatch('negotiate')", show=False, priority=True),
        Binding("t", "encounter_dispatch('thrust')", show=False, priority=True),
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
        """Dispatch encounter-specific keys (n/t/z/x/o/e) to EncounterScreen."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key(key)

    def action_switch_tab(self, tab: str) -> None:
        """Switch the content area to a different tab."""
        enc = self._encounter_screen
        if enc:
            # f→fleet, c→cargo, r→routes: remap to encounter actions
            _remap = {"fleet": "flee", "cargo": "close", "routes": "rake"}
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
        """Open buy dialog. During encounter: b=broadside."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("broadside")
            return
        if not self.session.active:
            return
        from portlight.app.tui.screens.market import execute_buy_flow
        execute_buy_flow(self, self.session)

    def action_sell(self) -> None:
        """Open sell dialog. During encounter: s=spare."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("spare")
            return
        if not self.session.active:
            return
        from portlight.app.tui.screens.market import execute_sell_flow
        execute_sell_flow(self, self.session)

    def action_sail(self) -> None:
        """Open sail dialog. During encounter: g=fight."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("fight")
            return
        if not self.session.active:
            return
        from portlight.app.tui.screens.routes import execute_sail_flow
        execute_sail_flow(self, self.session)

    def action_advance(self) -> None:
        """Advance one day. During encounter: a=take_all."""
        enc = self._encounter_screen
        if enc:
            enc.action_encounter_key("take_all")
            return
        if not self.session.active:
            return
        if self.session.world.pirates.pending_duel is not None:
            self.notify("Resolve the encounter first!", severity="warning")
            return
        from portlight.app.tui.screens.routes import execute_advance
        execute_advance(self, self.session)

    def refresh_views(self) -> None:
        """Refresh all visible views after a state mutation."""
        dashboard = self.query_one("DashboardScreen", expect_type=None)
        if dashboard is not None:
            dashboard.refresh_all()
