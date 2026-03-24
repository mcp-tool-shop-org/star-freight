"""Dashboard screen — Star Freight captain pressure bar + tabbed content area.

Features:
- Persistent captain pressure bar (credits, hull, fuel, crew, day)
- Tab-switched content area routing to Star Freight views
- No maritime vocabulary, no ocean colors, no ship art
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.text import Text
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Footer, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession

from textual.app import ComposeResult


# ---------------------------------------------------------------------------
# Splash screen — shown when no game is active
# ---------------------------------------------------------------------------

SPLASH_TITLE = """\
[bold #f0c040]
  ____  _               _____         _       _     _
 / ___|| |_ __ _ _ __  |  ___| __ ___(_) __ _| |__ | |_
 \\___ \\| __/ _` | '__| | |_ | '__/ _ \\ |/ _` | '_ \\| __|
  ___) | || (_| | |    |  _|| | |  __/ | (_| | | | | |_
 |____/ \\__\\__,_|_|    |_|  |_|  \\___|_|\\__, |_| |_|\\__|
                                         |___/
[/bold #f0c040]
[dim]Disgraced pilot. Space merchant. Five civilizations. One life.[/dim]"""


# ---------------------------------------------------------------------------
# Captain Pressure Bar — persistent header
# ---------------------------------------------------------------------------

class CaptainBar(Widget):
    """Persistent pressure bar showing ship instrumentation."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__(id="captain-bar")
        self.session = session

    def compose(self) -> ComposeResult:
        yield Static("", id="captain-line1")
        yield Static("", id="captain-line2")

    def on_mount(self) -> None:
        self.refresh_status()

    def refresh_status(self) -> None:
        from portlight.app.tui.theme import render_mini_bar, credits_display
        from portlight.engine.crew import active_crew, fit_crew, calculate_crew_pay

        line1 = self.query_one("#captain-line1", Static)
        line2 = self.query_one("#captain-line2", Static)

        if not self.session.active:
            line1.update("[dim]No active game[/dim]")
            line2.update("")
            return

        state = self.session.sf_campaign

        # Line 1: credits, hull, fuel, crew fitness, day
        hull_bar = render_mini_bar(state.ship_hull, state.ship_hull_max, 8)
        crew_active = len(active_crew(state.crew))
        crew_fit = len(fit_crew(state.crew))
        parts1 = [
            credits_display(state.credits),
            f"Hull {hull_bar} {state.ship_hull}/{state.ship_hull_max}",
            f"Fuel [{'bold green' if state.ship_fuel > 3 else 'bold red'}]{state.ship_fuel}d[/{'bold green' if state.ship_fuel > 3 else 'bold red'}]",
            f"Crew {crew_fit}/{crew_active} fit",
            f"Day [bold #4090e0]{state.day}[/bold #4090e0]",
        ]
        line1.update("  \u2502  ".join(parts1))

        # Line 2: crew alerts, pay urgency, station
        alerts = []

        # Crew injury alerts
        from portlight.engine.crew import CrewStatus
        for m in state.crew.members:
            if m.status == CrewStatus.INJURED:
                alerts.append(f"[red]{m.name} injured[/red]")
            elif m.morale < 30:
                alerts.append(f"[yellow]{m.name} morale {m.morale}[/yellow]")

        # Pay urgency
        days_since_pay = state.day - state.last_pay_day
        if days_since_pay >= 27:
            days_until_pay = 30 - days_since_pay
            alerts.append(f"[bold red]\u26a0 Pay due in {days_until_pay}d[/bold red]")

        # Top reputation deltas
        rep_parts = []
        for faction, standing in sorted(state.reputation.items(), key=lambda x: abs(x[1]), reverse=True)[:2]:
            arrow = "\u25b2" if standing > 0 else "\u25bc" if standing < 0 else "\u2500"
            color = "green" if standing > 0 else "red" if standing < 0 else "dim"
            short_name = faction.split(".")[-1][:6]
            rep_parts.append(f"[{color}]{arrow}{short_name}[/{color}]")

        # Station
        from portlight.content.star_freight import SLICE_STATIONS
        station = SLICE_STATIONS.get(state.current_station)
        station_name = station.name if station else state.current_station or "???"

        parts2 = []
        if rep_parts:
            parts2.append(" ".join(rep_parts))
        if alerts:
            parts2.append("  ".join(alerts[:2]))
        parts2.append(f"[bold]{station_name}[/bold]")

        line2.update("  \u2502  ".join(parts2))


# ---------------------------------------------------------------------------
# Content Area — routes to Star Freight views
# ---------------------------------------------------------------------------

class ContentArea(Widget):
    """Switchable content area routing to Star Freight views."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__(id="content-area")
        self.session = session
        self._current_tab = "dashboard"
        self._static = Static("", classes="view-panel")

    def compose(self) -> ComposeResult:
        yield self._static

    def on_mount(self) -> None:
        self.switch_tab("dashboard")

    def switch_tab(self, tab: str) -> None:
        self._current_tab = tab
        self._render_tab()

    def _render_tab(self) -> None:
        if not self.session.active:
            self._static.update(SPLASH_TITLE)
            return
        self._static.update(self._get_view())

    def _get_view(self):
        from portlight.app import sf_views

        state = self.session.sf_campaign
        tab = self._current_tab

        if tab == "dashboard":
            return sf_views.dashboard(state)
        elif tab == "crew":
            return sf_views.crew_screen(state)
        elif tab == "routes":
            return sf_views.routes_screen(state)
        elif tab == "market":
            return sf_views.market_screen(state)
        elif tab == "station":
            return sf_views.station_screen(state)
        elif tab == "journal":
            return sf_views.journal_screen(state)
        elif tab == "faction":
            return sf_views.faction_screen(state)
        elif tab == "help":
            return self._help_view()
        return Text(f"Unknown tab: {tab}", style="red")

    def _help_view(self):
        """Star Freight keybinding reference."""
        lines = [
            "",
            "[bold #f0c040]Star Freight \u2014 Controls[/bold #f0c040]",
            "",
            "[bold #4090e0]Navigation[/bold #4090e0]",
            "  [bold cyan]D[/bold cyan] Dashboard    [bold cyan]C[/bold cyan] Crew       [bold cyan]R[/bold cyan] Routes",
            "  [bold cyan]M[/bold cyan] Market       [bold cyan]T[/bold cyan] Station    [bold cyan]J[/bold cyan] Journal",
            "  [bold cyan]F[/bold cyan] Faction      [bold cyan]?[/bold cyan] Help       [bold cyan]Q[/bold cyan] Quit",
            "",
            "[bold #4090e0]Actions[/bold #4090e0]",
            "  [bold #f0c040]B[/bold #f0c040] Buy goods    [bold #f0c040]S[/bold #f0c040] Sell goods",
            "  [bold #f0c040]G[/bold #f0c040] Travel       [bold #f0c040]A[/bold #f0c040] Advance day",
            "",
            "[bold #4090e0]Information[/bold #4090e0]",
            "  [dim]Credits (\u20a1) are your runway. Pay crew every 30 days.[/dim]",
            "  [dim]Crew abilities degrade when injured.[/dim]",
            "  [dim]Cultural knowledge unlocks restricted trade goods.[/dim]",
            "  [dim]Investigation fragments reveal what happened before you arrived.[/dim]",
            "",
        ]
        return Panel(
            "\n".join(lines),
            title="[bold #f0c040]Help[/bold #f0c040]",
            border_style="#1a1e2a",
        )


# ---------------------------------------------------------------------------
# Tab Bar — Star Freight navigation
# ---------------------------------------------------------------------------

class TabBar(Static):
    """Bottom tab bar with Star Freight screens."""

    TAB_LABELS = [
        ("D", "Dash"), ("C", "Crew"), ("R", "Routes"),
        ("M", "Market"), ("T", "Station"), ("J", "Journal"),
        ("F", "Faction"), ("?", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__("", id="tab-bar")
        self._active = "dashboard"

    def on_mount(self) -> None:
        self._render_tabs()

    def set_active(self, tab: str) -> None:
        self._active = tab
        self._render_tabs()

    def _render_tabs(self) -> None:
        tab_map = {
            "D": "dashboard", "C": "crew", "R": "routes",
            "M": "market", "T": "station", "J": "journal",
            "F": "faction", "?": "help",
        }
        parts = []
        for key, label in self.TAB_LABELS:
            tab_id = tab_map.get(key, label.lower())
            if tab_id == self._active:
                parts.append(f"[bold #f0c040 on #1a1e2a] {key}\u00b7{label} [/bold #f0c040 on #1a1e2a]")
            else:
                parts.append(f"[dim #606060] {key}[/dim #606060][#e8e8e8]\u00b7{label}[/#e8e8e8]")
        self.update(" ".join(parts))


# ---------------------------------------------------------------------------
# Dashboard Screen — main container
# ---------------------------------------------------------------------------

class DashboardScreen(Widget):
    """Main screen: captain pressure bar + content area + tab bar."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__()
        self.session = session
        self._captain_bar = CaptainBar(session)
        self._content = ContentArea(session)
        self._tabbar = TabBar()

    def compose(self) -> ComposeResult:
        yield self._captain_bar
        yield self._content
        yield self._tabbar
        yield Footer()

    def switch_tab(self, tab: str) -> None:
        self._content.switch_tab(tab)
        self._tabbar.set_active(tab)

    def refresh_all(self) -> None:
        self._captain_bar.refresh_status()
        self._content._render_tab()
