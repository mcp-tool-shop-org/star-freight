"""Dashboard screen — maritime-themed status sidebar + tabbed content area.

Features:
- ASCII ship art in sidebar header
- Visual HP/cargo/hull bars with block characters
- Region badges with color coding
- Animated wave at sidebar bottom
- Compass rose in routes view
- Splash screen on first launch
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.containers import Horizontal
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Footer, Static

if TYPE_CHECKING:
    from portlight.app.session import GameSession

from textual.app import ComposeResult


# ---------------------------------------------------------------------------
# Splash screen — shown briefly on launch
# ---------------------------------------------------------------------------

SPLASH_ART = """\
[dim blue]
              ~         ~
        ~          ~         ~
   ~         ~          ~
[/dim blue][bold cyan]
                |\\
                | \\
                |  \\
               _|___\\__
              /________\\
[/bold cyan][dim blue]
   ~~~~~~~~~~~/~~~~~~~~~~\\~~~~~~~~~~~
  ~~~~~~~~~~/    ~   ~    \\~~~~~~~~~~
 ~~~~~~~~~/        ~       \\~~~~~~~~~
[/dim blue]"""

SPLASH_TITLE = """\
[bold #e9c46a]
  ____            _   _ _       _     _
 |  _ \\ ___  _ __| |_| (_) __ _| |__ | |_
 | |_) / _ \\| '__| __| | |/ _` | '_ \\| __|
 |  __/ (_) | |  | |_| | | (_| | | | | |_
 |_|   \\___/|_|   \\__|_|_|\\__, |_| |_|\\__|
                           |___/
[/bold #e9c46a]"""


# ---------------------------------------------------------------------------
# Status Sidebar — the ship's log panel
# ---------------------------------------------------------------------------

class StatusSidebar(Widget):
    """Maritime-themed captain status sidebar with ship art and visual bars."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__(id="status-sidebar")
        self.session = session
        self._wave_frame = 0
        self._wave_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Static("", id="sidebar-ship-art")
        yield Static("", id="sidebar-captain")
        yield Static("", id="sidebar-ship")
        yield Static("", id="sidebar-location")
        yield Static("", id="sidebar-wave")

    def on_mount(self) -> None:
        self.refresh_status()
        self._wave_timer = self.set_interval(0.8, self._animate_wave)

    def _animate_wave(self) -> None:
        from portlight.app.tui.theme import WAVE_FRAMES
        self._wave_frame = (self._wave_frame + 1) % len(WAVE_FRAMES)
        wave = self.query_one("#sidebar-wave", Static)
        wave.update(WAVE_FRAMES[self._wave_frame])

    def refresh_status(self) -> None:
        from portlight.app.tui.theme import (
            SHIP_ART, REGION_BADGES, WAVE_FRAMES,
            render_mini_bar, silver_display,
        )

        ship_art = self.query_one("#sidebar-ship-art", Static)
        captain_w = self.query_one("#sidebar-captain", Static)
        ship_w = self.query_one("#sidebar-ship", Static)
        location_w = self.query_one("#sidebar-location", Static)
        wave_w = self.query_one("#sidebar-wave", Static)

        if not self.session.active:
            ship_art.update(SHIP_ART)
            captain_w.update("[dim]No active game[/dim]")
            ship_w.update("")
            location_w.update("")
            wave_w.update(WAVE_FRAMES[0])
            return

        w = self.session.world
        cap = w.captain
        ship = cap.ship

        # Ship art
        ship_art.update(SHIP_ART)

        # Captain section
        cap_lines = [
            f"[bold #e9c46a]{cap.name}[/bold #e9c46a]",
            f"[dim]Day[/dim] [bold cyan]{w.day}[/bold cyan]",
            "",
            f"[dim]Silver[/dim] {silver_display(cap.silver)}",
            f"[dim]Prov.[/dim]  {_prov_display(cap.provisions)}",
        ]
        captain_w.update("\n".join(cap_lines))

        # Ship section
        if ship:
            from portlight.content.upgrades import UPGRADES as _UPG
            from portlight.engine.ship_stats import resolve_cargo_capacity, resolve_hull_max
            eff_cargo = resolve_cargo_capacity(ship, _UPG)
            eff_hull = resolve_hull_max(ship, _UPG)
            cargo_used = sum(c.quantity for c in cap.cargo)

            ship_lines = [
                f"[bold]{ship.name}[/bold]",
                f"[dim]{ship.template_id}[/dim]",
                "",
                f"Hull  {render_mini_bar(ship.hull, eff_hull)} {ship.hull}/{eff_hull}",
                f"Cargo {render_mini_bar(cargo_used, eff_cargo)} {cargo_used}/{eff_cargo}",
                f"Crew  {render_mini_bar(ship.crew, ship.crew_max)} {ship.crew}/{ship.crew_max}",
            ]
            if ship.upgrades:
                ship_lines.append(f"[dim]Upgrades: {len(ship.upgrades)}/{ship.upgrade_slots}[/dim]")
            ship_w.update("\n".join(ship_lines))
        else:
            ship_w.update("[dim]No ship[/dim]")

        # Location section
        loc_lines: list[str] = []
        if w.voyage:
            from portlight.engine.models import VoyageStatus
            if w.voyage.status == VoyageStatus.AT_SEA:
                pct = int(w.voyage.progress / max(w.voyage.distance, 1) * 100)
                dest = w.ports.get(w.voyage.destination_id)
                dest_name = dest.name if dest else w.voyage.destination_id
                loc_lines.append("[bold cyan]\u2693 At Sea[/bold cyan]")
                loc_lines.append(f"  \u2192 {dest_name}")
                # Voyage progress bar
                bar_w = 18
                filled = int(pct / 100 * bar_w)
                empty = bar_w - filled
                ship_char = "[bold cyan]\u25ba[/bold cyan]"
                bar = f"[dim blue]{'~' * filled}[/dim blue]{ship_char}[dim]{'.' * empty}[/dim]"
                loc_lines.append(f"  {bar} {pct}%")
                loc_lines.append(f"  [dim]Day {w.voyage.days_elapsed} of voyage[/dim]")
            else:
                port = w.ports.get(w.voyage.destination_id)
                port_name = port.name if port else "???"
                region = port.region if port and hasattr(port, "region") else ""
                badge = REGION_BADGES.get(region, "")
                loc_lines.append(f"\u2693 [bold]{port_name}[/bold]")
                if badge:
                    loc_lines.append(f"  {badge} [dim]{region}[/dim]")
        location_w.update("\n".join(loc_lines))
        wave_w.update(WAVE_FRAMES[self._wave_frame])


def _prov_display(provisions: int) -> str:
    if provisions > 20:
        return f"[green]{provisions} days[/green]"
    elif provisions > 10:
        return f"[yellow]{provisions} days[/yellow]"
    elif provisions > 0:
        return f"[bold red]{provisions} days[/bold red]"
    return "[bold red]EMPTY![/bold red]"


# ---------------------------------------------------------------------------
# Content Area — tabbed view renderer with enhanced views
# ---------------------------------------------------------------------------

class ContentArea(Widget):
    """Switchable content area with enhanced views."""

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
            self._static.update(
                SPLASH_ART + "\n" + SPLASH_TITLE
                + "\n[dim]Start a game with: portlight new <name>[/dim]"
            )
            return
        self._static.update(self._get_view())

    def _get_view(self):
        from portlight.app import views

        s = self.session
        w = s.world
        cap = w.captain
        tab = self._current_tab

        if tab == "dashboard":
            return self._enhanced_dashboard()
        elif tab == "market":
            return self._enhanced_market()
        elif tab == "cargo":
            return views.cargo_view(cap)
        elif tab == "routes":
            return self._enhanced_routes()
        elif tab == "port":
            return self._enhanced_port()
        elif tab == "fleet":
            return views.fleet_view(cap)
        elif tab == "inventory":
            return self._inventory_view()
        elif tab == "contracts":
            return self._enhanced_contracts()
        elif tab == "ledger":
            return self._enhanced_ledger()
        elif tab == "infrastructure":
            return self._infra_view()
        elif tab == "map":
            return self._map_view()
        elif tab == "help":
            return self._help_view()
        return Text(f"Unknown tab: {tab}", style="red")

    # --- Enhanced views that go beyond the CLI ---

    def _enhanced_dashboard(self):
        """Rich dashboard with trade tips and situation summary."""
        from portlight.app.tui.theme import render_bar, silver_display

        s = self.session
        w = s.world
        cap = w.captain

        lines: list[str] = []
        lines.append(f"[bold #e9c46a]\u2693 Captain {cap.name} — Day {w.day}[/bold #e9c46a]")
        lines.append("")

        # Quick stats row
        lines.append(f"  Silver: {silver_display(cap.silver)}    Provisions: {_prov_display(cap.provisions)}")
        if cap.ship:
            from portlight.content.upgrades import UPGRADES as _UPG
            from portlight.engine.ship_stats import resolve_hull_max
            eff_hull = resolve_hull_max(cap.ship, _UPG)
            lines.append(f"  Hull:   {render_bar(cap.ship.hull, eff_hull, 16)} {cap.ship.hull}/{eff_hull}")
        lines.append("")

        # Trade summary
        if s.ledger.receipts:
            net = s.ledger.net_profit
            trade_count = len(s.ledger.receipts)
            if net > 0:
                lines.append(f"  [green]\u25b2 Net profit: +{net:,} silver ({trade_count} trades)[/green]")
            elif net < 0:
                lines.append(f"  [red]\u25bc Net loss: {net:,} silver ({trade_count} trades)[/red]")
            else:
                lines.append(f"  [dim]Break-even ({trade_count} trades)[/dim]")
            lines.append("")

        # Active contracts
        active = [c for c in s.board.active if not c.completed]
        if active:
            lines.append("[bold]Active Contracts[/bold]")
            for c in active[:3]:
                days_left = c.deadline_day - w.day
                urgency = "[red]" if days_left < 5 else "[yellow]" if days_left < 10 else "[dim]"
                lines.append(f"  {urgency}\u2022 {c.description} ({days_left}d left){urgency.replace('[', '[/')}")
            lines.append("")

        # Location-based tips
        port = s.current_port
        if port:
            lines.append(f"[bold]At {port.name}[/bold]")
            # Find cheapest good to buy here
            cheap = sorted(
                [sl for sl in port.market if sl.stock_current > 0 and sl.buy_price > 0],
                key=lambda sl: sl.buy_price,
            )
            if cheap:
                from portlight.content.goods import GOODS
                sl = cheap[0]
                good = GOODS.get(sl.good_id)
                if good:
                    lines.append(f"  [dim]Cheapest:[/dim] {good.name} at {sl.buy_price} silver")
            # Find most profitable route
            if w.routes:
                best_routes = sorted(
                    [r for r in w.routes if r.port_a == port.id or r.port_b == port.id],
                    key=lambda r: r.distance,
                )
                if best_routes:
                    r = best_routes[0]
                    dest_id = r.port_b if r.port_a == port.id else r.port_a
                    dest = w.ports.get(dest_id)
                    if dest:
                        lines.append(f"  [dim]Nearest:[/dim] {dest.name} ({r.distance} leagues)")
        elif s.at_sea:
            lines.append("[bold cyan]Sailing...[/bold cyan]")
            lines.append("  Press [bold]A[/bold] to advance a day")

        lines.append("")
        lines.append("[dim]Press ? for keybinding help[/dim]")

        return Panel(
            "\n".join(lines),
            title="[bold #e9c46a]\u2693 Dashboard[/bold #e9c46a]",
            border_style="#264653",
        )

    def _enhanced_market(self):
        """Market view with profit indicators and visual stock bars."""
        from portlight.app.tui.theme import render_mini_bar

        port = self.session.current_port
        if not port:
            return Text("\u2693 Not docked at a port. Sail to a port first.", style="yellow")

        cap = self.session.world.captain
        from portlight.content.goods import GOODS

        table = Table(
            title=f"\u2693 Market — {port.name}",
            border_style="#264653",
            header_style="bold #2a9d8f",
            show_lines=False,
            pad_edge=True,
        )
        table.add_column("Good", style="bold", min_width=12)
        table.add_column("Buy", justify="right", style="#e9c46a")
        table.add_column("Sell", justify="right", style="#c8d6e5")
        table.add_column("Stock", min_width=12)
        table.add_column("Margin", justify="right")
        table.add_column("Cargo", justify="right", style="cyan")
        table.add_column("Afford", justify="right")

        for slot in sorted(port.market, key=lambda s: s.buy_price):
            good = GOODS.get(slot.good_id)
            if not good:
                continue
            name = good.name

            # Stock bar
            stock_bar = render_mini_bar(slot.stock_current, slot.stock_target)
            stock_label = f"{stock_bar} {slot.stock_current}"

            # Margin indicator
            if slot.buy_price > 0 and slot.sell_price > 0:
                margin = slot.sell_price - slot.buy_price
                if margin > 0:
                    margin_str = f"[green]+{margin}[/green]"
                elif margin < 0:
                    margin_str = f"[red]{margin}[/red]"
                else:
                    margin_str = "[dim]0[/dim]"
            else:
                margin_str = "[dim]-[/dim]"

            # Cargo held
            held = sum(c.quantity for c in cap.cargo if c.good_id == slot.good_id)
            held_str = str(held) if held > 0 else "[dim]-[/dim]"

            # Affordability
            if slot.buy_price > 0:
                can_buy = cap.silver // slot.buy_price
                if can_buy > 0:
                    afford_str = f"[green]{can_buy}[/green]"
                else:
                    afford_str = "[red]\u2717[/red]"
            else:
                afford_str = "[dim]-[/dim]"

            table.add_row(
                name,
                str(slot.buy_price) if slot.buy_price > 0 else "-",
                str(slot.sell_price) if slot.sell_price > 0 else "-",
                stock_label,
                margin_str,
                held_str,
                afford_str,
            )

        return Group(
            table,
            Text(""),
            Text("  [B]uy  [S]ell  [D]ashboard", style="#576574"),
        )

    def _enhanced_routes(self):
        """Routes view with compass rose and danger skulls."""
        from portlight.app.tui.theme import danger_indicator, REGION_BADGES

        s = self.session
        w = s.world
        port = s.current_port

        parts: list[str] = []

        if port:
            parts.append(f"[bold #e9c46a]\u2693 Routes from {port.name}[/bold #e9c46a]")
        elif s.at_sea:
            parts.append("[bold cyan]\u2693 At sea — no routes available[/bold cyan]")
            parts.append("")
            parts.append("Press [bold]A[/bold] to advance a day.")
            return Panel("\n".join(parts), title="\u2693 Routes", border_style="#264653")
        else:
            return Text("Not docked.", style="yellow")

        parts.append("")

        # Build route table
        table = Table(
            border_style="#264653",
            header_style="bold #2a9d8f",
            show_lines=False,
        )
        table.add_column("Destination", style="bold", min_width=16)
        table.add_column("Region")
        table.add_column("Dist.", justify="right")
        table.add_column("Days", justify="right", style="cyan")
        table.add_column("Danger")
        table.add_column("Ship Req.")

        routes_from = []
        for route in w.routes:
            if route.port_a == port.id:
                dest = w.ports.get(route.port_b)
                if dest:
                    routes_from.append((dest, route))
            elif route.port_b == port.id:
                dest = w.ports.get(route.port_a)
                if dest:
                    routes_from.append((dest, route))

        routes_from.sort(key=lambda x: x[1].distance)

        for dest, route in routes_from:
            region = dest.region if hasattr(dest, "region") else ""
            badge = REGION_BADGES.get(region, f"[dim]{region}[/dim]")
            speed = w.captain.ship.speed if w.captain.ship else 5
            days = max(1, round(route.distance / speed))
            danger = danger_indicator(route.danger)
            ship_class = getattr(route, "min_ship_class", "")
            ship_req = ship_class if ship_class else "[dim]-[/dim]"

            table.add_row(
                dest.name,
                badge,
                str(route.distance),
                str(days),
                danger,
                ship_req,
            )

        return Group(
            Panel("\n".join(parts), border_style="#264653"),
            table,
            Text(""),
            Text("  [G]o/Sail  [D]ashboard", style="#576574"),
        )

    def _enhanced_port(self):
        """Port view with region badge and feature highlights."""
        from portlight.app.tui.theme import REGION_BADGES

        port = self.session.current_port
        if not port:
            return Text("\u2693 Not docked at a port.", style="yellow")


        lines: list[str] = []
        region = port.region if hasattr(port, "region") else ""
        badge = REGION_BADGES.get(region, "")
        lines.append(f"[bold #e9c46a]\u2693 {port.name}[/bold #e9c46a] {badge}")
        lines.append(f"[italic dim]{port.description}[/italic dim]")
        lines.append("")

        # Features
        if hasattr(port, "features") and port.features:
            features_str = ", ".join(
                f"[bold #2a9d8f]{f.value if hasattr(f, 'value') else f}[/bold #2a9d8f]"
                for f in port.features
            )
            lines.append(f"Features: {features_str}")
            lines.append("")

        # Port fee
        if hasattr(port, "port_fee"):
            lines.append(f"Port fee: [yellow]{port.port_fee}[/yellow] silver")

        # Available services
        services = []
        if hasattr(port, "features"):
            feat_vals = [f.value if hasattr(f, "value") else str(f) for f in port.features]
            if "shipyard" in feat_vals:
                services.append("[#2a9d8f]\u2692 Shipyard[/#2a9d8f]")
            if "black_market" in feat_vals:
                services.append("[#e76f51]\u2620 Black Market[/#e76f51]")
            if "safe_harbor" in feat_vals:
                services.append("[green]\u2693 Safe Harbor[/green]")
        if services:
            lines.append(f"Services: {' '.join(services)}")

        return Panel(
            "\n".join(lines),
            title=f"\u2693 {port.name}",
            border_style="#264653",
        )

    def _enhanced_contracts(self):
        """Contracts view with urgency coloring."""
        from portlight.app import views
        s = self.session
        w = s.world

        parts = []
        # Available offers
        parts.append(views.contracts_view(s.board, w.day))

        # Active obligations with urgency
        active = [c for c in s.board.active if not c.completed]
        if active:
            lines = ["\n[bold #e9c46a]Active Obligations[/bold #e9c46a]", ""]
            for c in active:
                days_left = c.deadline_day - w.day
                if days_left < 3:
                    icon = "[bold red]\u26a0[/bold red]"
                    style = "bold red"
                elif days_left < 7:
                    icon = "[yellow]\u25cf[/yellow]"
                    style = "yellow"
                else:
                    icon = "[green]\u25cf[/green]"
                    style = "dim"
                lines.append(f"  {icon} [{style}]{c.description}[/{style}]")
                lines.append(f"      [dim]{days_left} days remaining[/dim]")
            parts.append(Text.from_markup("\n".join(lines)))

        return Group(*parts)

    def _enhanced_ledger(self):
        """Ledger with P&L summary header."""
        from portlight.app import views

        s = self.session
        cap = s.world.captain

        lines = []
        if s.ledger.receipts:
            net = s.ledger.net_profit
            total_trades = len(s.ledger.receipts)
            profitable = sum(1 for r in s.ledger.receipts if r.action.value == "sell")

            lines.append("[bold #e9c46a]Trade Performance[/bold #e9c46a]")
            lines.append("")
            if net > 0:
                lines.append(f"  Net P&L:     [bold green]+{net:,}[/bold green] silver")
            elif net < 0:
                lines.append(f"  Net P&L:     [bold red]{net:,}[/bold red] silver")
            else:
                lines.append("  Net P&L:     [dim]Break-even[/dim]")
            lines.append(f"  Trades:      {total_trades} ({profitable} profitable)")
            lines.append(f"  Win rate:    {profitable/total_trades*100:.0f}%")
            lines.append("")

        header = Panel("\n".join(lines), border_style="#264653") if lines else Text("")
        return Group(header, views.ledger_view(s.ledger, cap))

    def _inventory_view(self):
        """Build inventory view data from captain state."""
        from portlight.app.combat_views import inventory_view
        cap = self.session.world.captain

        gear_data = {
            "armor": None,
            "melee": None,
            "ranged": None,
            "style": None,
            "injuries": [],
            "cargo_summary": [],
            "silver": cap.silver,
        }

        if hasattr(cap, "armor") and cap.armor:
            gear_data["armor"] = {
                "name": cap.armor.name,
                "dr": cap.armor.damage_reduction,
                "dodge_penalty": getattr(cap.armor, "dodge_penalty", 0),
            }
        if hasattr(cap, "melee_weapon") and cap.melee_weapon:
            gear_data["melee"] = {
                "name": cap.melee_weapon.name,
                "damage": cap.melee_weapon.base_damage,
                "speed": getattr(cap.melee_weapon, "speed_modifier", 0),
            }
        if hasattr(cap, "ranged") and cap.ranged:
            gear_data["ranged"] = {
                "name": cap.ranged.name,
                "damage": cap.ranged.base_damage,
                "ammo": getattr(cap.ranged, "ammo", 0),
            }
        if hasattr(cap, "fighting_style") and cap.fighting_style:
            gear_data["style"] = {"name": cap.fighting_style.name}
        if hasattr(cap, "injuries"):
            gear_data["injuries"] = [
                {"name": inj.name, "severity": inj.severity, "days_remaining": inj.days_remaining}
                for inj in cap.injuries
            ]
        gear_data["cargo_summary"] = [
            {"good_id": c.good_id, "quantity": c.quantity}
            for c in cap.cargo
        ]

        return inventory_view(gear_data)

    def _infra_view(self):
        """Composite infrastructure view."""
        from portlight.app.views import (
            warehouse_view, offices_view, licenses_view,
            insurance_view, credit_view,
        )
        s = self.session
        parts = []
        parts.append(warehouse_view(s.infra, s.world, s.world.captain))
        parts.append(offices_view(s.infra))
        if s.world.captain.standing:
            parts.append(licenses_view(s.infra, s.world.captain.standing))
            parts.append(credit_view(s.infra, s.world.captain.standing))
        heat = 0
        if s.world.captain.standing:
            heat = max(s.world.captain.standing.customs_heat.values(), default=0)
        parts.append(insurance_view(s.infra, heat))
        return Group(*parts)

    def _map_view(self):
        """World map view — reuses the ASCII map renderer from views."""
        from portlight.app import views
        s = self.session
        player_port = s.current_port_id
        return views.world_map_view(
            s.world, player_port_id=player_port,
            show_routes=True, region_filter=None,
        )

    def _help_view(self):
        """Keybinding help with maritime styling."""
        lines = [
            "",
            "[bold #e9c46a]\u2693 Portlight — Keybindings[/bold #e9c46a]",
            "",
            "[bold #2a9d8f]Navigation[/bold #2a9d8f]",
            "  [bold cyan]D[/bold cyan] Dashboard    [bold cyan]M[/bold cyan] Market     [bold cyan]R[/bold cyan] Routes",
            "  [bold cyan]C[/bold cyan] Cargo        [bold cyan]I[/bold cyan] Inventory  [bold cyan]F[/bold cyan] Fleet",
            "  [bold cyan]K[/bold cyan] Contracts    [bold cyan]P[/bold cyan] Port       [bold cyan]L[/bold cyan] Ledger",
            "  [bold cyan]W[/bold cyan] Infra        [bold cyan]V[/bold cyan] Map        [bold cyan]?[/bold cyan] Help       [bold cyan]Q[/bold cyan] Quit",
            "",
            "[bold #2a9d8f]Actions[/bold #2a9d8f]",
            "  [bold #e9c46a]B[/bold #e9c46a] Buy goods    [bold #e9c46a]S[/bold #e9c46a] Sell goods",
            "  [bold #e9c46a]G[/bold #e9c46a] Sail (go)    [bold #e9c46a]A[/bold #e9c46a] Advance day",
            "",
            "[bold #2a9d8f]Combat[/bold #2a9d8f]",
            "  [bold #e76f51]T[/bold #e76f51] Thrust       [bold #e76f51]Z[/bold #e76f51] Slash      [bold #e76f51]X[/bold #e76f51] Parry",
            "  [bold #e76f51]O[/bold #e76f51] Shoot        [bold #e76f51]E[/bold #e76f51] Dodge/Evade",
            "",
            "[bold #2a9d8f]General[/bold #2a9d8f]",
            "  [dim]Esc[/dim]   Back / Cancel",
            "  [dim]Enter[/dim] Confirm selection",
            "",
            "[dim]Three frontends, one engine:[/dim]",
            "[dim]  portlight         \u2192 CLI (Rich)[/dim]",
            "[dim]  portlight tui     \u2192 TUI (Textual)[/dim]",
            "[dim]  portlight-desktop \u2192 Desktop (Tauri)[/dim]",
        ]
        return Panel(
            "\n".join(lines),
            title="[bold #e9c46a]\u2693 Help[/bold #e9c46a]",
            border_style="#264653",
        )


# ---------------------------------------------------------------------------
# Tab Bar — maritime-styled navigation
# ---------------------------------------------------------------------------

class TabBar(Static):
    """Bottom tab bar with maritime styling."""

    TAB_LABELS = [
        ("D", "Dash"), ("M", "Market"), ("R", "Routes"),
        ("C", "Cargo"), ("I", "Inv"), ("F", "Fleet"),
        ("K", "Contracts"), ("P", "Port"), ("L", "Ledger"),
        ("W", "Infra"), ("V", "Map"), ("?", "Help"),
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
            "D": "dashboard", "M": "market", "R": "routes",
            "C": "cargo", "I": "inventory", "F": "fleet",
            "K": "contracts", "P": "port", "L": "ledger",
            "W": "infrastructure", "V": "map", "?": "help",
        }
        parts = []
        for key, label in self.TAB_LABELS:
            tab_id = tab_map.get(key, label.lower())
            if tab_id == self._active:
                parts.append(f"[bold #e9c46a on #264653] {key}\u00b7{label} [/bold #e9c46a on #264653]")
            else:
                parts.append(f"[dim #576574] {key}[/dim #576574][#c8d6e5]\u00b7{label}[/#c8d6e5]")
        self.update(" ".join(parts))


# ---------------------------------------------------------------------------
# Dashboard Screen — main container
# ---------------------------------------------------------------------------

class DashboardScreen(Widget):
    """Main screen combining sidebar, content area, and tab bar."""

    def __init__(self, session: "GameSession") -> None:
        super().__init__()
        self.session = session
        self._sidebar = StatusSidebar(session)
        self._content = ContentArea(session)
        self._tabbar = TabBar()

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self._sidebar
            yield self._content
        yield self._tabbar
        yield Footer()

    def switch_tab(self, tab: str) -> None:
        self._content.switch_tab(tab)
        self._tabbar.set_active(tab)

    def refresh_all(self) -> None:
        self._sidebar.refresh_status()
        self._content._render_tab()
