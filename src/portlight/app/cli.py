"""Typer CLI — player-facing commands.

Every command produces an updated game screen. No raw success text.
The CLI feels like a commandable game, not a command library.
"""

from __future__ import annotations

import random

import typer
from rich.console import Console

from portlight import __version__
from portlight.app import views
from portlight.app.session import GameSession

app = typer.Typer(
    name="starfreight",
    help="Star Freight — space merchant captain RPG",
    no_args_is_help=True,
)
console = Console()

# Global save slot -- set by --save callback before any subcommand runs
_active_slot: str = "default"


@app.callback()
def _main(
    save: str = typer.Option("default", "--save", "-s",
        help="Save slot name (isolates separate games)"),
) -> None:
    """Star Freight — space merchant captain RPG."""
    global _active_slot  # noqa: PLW0603
    _active_slot = save


@app.command()
def version() -> None:
    """Print version and exit."""
    typer.echo(f"starfreight {__version__}")
    raise typer.Exit()


def _session() -> GameSession:
    """Load or fail with helpful message."""
    from portlight.engine.save import SaveVersionError
    s = GameSession(slot=_active_slot)
    try:
        loaded = s.load()
    except SaveVersionError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    if not loaded:
        console.print("[red]No saved game found.[/red] Start a new game with: [bold]portlight new YourName --type merchant[/bold]")
        raise typer.Exit(1)
    return s


# ---------------------------------------------------------------------------
# New game
# ---------------------------------------------------------------------------

@app.command()
def new(
    name: str = typer.Argument("Captain", help="Captain name"),
    captain_type: str = typer.Option(None, "--type", "-t",
        help="Captain type: merchant, smuggler, navigator, privateer, corsair, scholar, merchant_prince, dockhand, bounty_hunter, custom"),
) -> None:
    """Start a new game. Choose your captain type to shape your career."""
    from portlight.engine.captain_identity import CaptainType

    # Interactive selection when --type is omitted
    if captain_type is None:
        _interactive_captain_select(name)
        return

    valid_types = {ct.value for ct in CaptainType}
    if captain_type not in valid_types:
        console.print(f"[red]Unknown captain type: {captain_type}[/red]")
        console.print(f"Choose: {', '.join(sorted(valid_types))}")
        raise typer.Exit(1)
    if captain_type == "custom":
        _create_custom_game(name)
        return

    s = GameSession(slot=_active_slot)
    s.new(name, captain_type=captain_type)
    console.print("\n[bold green]A new voyage begins.[/bold green]\n")
    console.print(views.welcome_view(s.captain, s.captain_template, s.world, s.infra))


def _interactive_captain_select(name: str) -> None:
    """Interactive captain selection screen with roster, spotlight, and confirmation."""
    from portlight.engine.captain_identity import (
        CAPTAIN_COLORS,
        CAPTAIN_ORDER,
        CAPTAIN_QUOTES,
        CAPTAIN_TEMPLATES,
        CaptainType,
    )

    order = CAPTAIN_ORDER
    templates = CAPTAIN_TEMPLATES
    total = len(order)

    def _show_roster() -> None:
        console.clear()
        console.print(views.captain_roster_view(
            templates, order, CAPTAIN_QUOTES, CAPTAIN_COLORS,
            console_width=console.width,
        ))

    def _show_spotlight(idx: int) -> None:
        ct = order[idx]
        tmpl = templates[ct]
        color = CAPTAIN_COLORS.get(ct, "blue")
        console.clear()
        console.print(views.captain_spotlight_view(tmpl, idx + 1, total, color=color))
        console.print(
            "  [bold green][Enter][/bold green] [dim]Choose this captain[/dim]    "
            "[bold yellow]B[/bold yellow] [dim]Back to roster[/dim]    "
            "[bold cyan]N[/bold cyan]/[bold cyan]P[/bold cyan] [dim]Next/Previous[/dim]\n"
        )

    def _confirm(ct: CaptainType) -> bool:
        tmpl = templates[ct]
        color = CAPTAIN_COLORS.get(ct, "green")
        console.print(views.captain_confirm_view(name, tmpl, color=color))
        try:
            answer = input("  Proceed? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        return answer in ("", "y", "yes")

    # Main loop
    _show_roster()
    while True:
        try:
            choice = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Cancelled.[/dim]")
            raise typer.Exit(0)

        # Number selection (1-9 for spotlight, 0 for custom)
        if choice == "0":
            _create_custom_game(name)
            return
        if choice == "q":
            console.print("[dim]Cancelled.[/dim]")
            raise typer.Exit(0)
        if choice in {str(i) for i in range(1, total + 1)}:
            idx = int(choice) - 1
            _show_spotlight(idx)

            # Spotlight sub-loop
            while True:
                try:
                    sub = input("  > ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    _show_roster()
                    break

                if sub in ("", "enter", "y", "yes"):
                    # Confirm selection
                    ct = order[idx]
                    if _confirm(ct):
                        s = GameSession(slot=_active_slot)
                        s.new(name, captain_type=ct.value)
                        console.print("\n[bold green]A new voyage begins.[/bold green]\n")
                        console.print(views.welcome_view(s.captain, s.captain_template, s.world, s.infra))
                        return
                    else:
                        _show_spotlight(idx)
                elif sub in ("b", "back"):
                    _show_roster()
                    break
                elif sub in ("n", "next"):
                    idx = (idx + 1) % total
                    _show_spotlight(idx)
                elif sub in ("p", "prev", "previous"):
                    idx = (idx - 1) % total
                    _show_spotlight(idx)
                else:
                    console.print("  [dim]Enter, B(ack), N(ext), or P(rev)[/dim]")
            continue

        # Name-based selection (fuzzy match)
        matched = None
        for ct in order:
            tmpl = templates[ct]
            if choice in tmpl.name.lower() or choice in ct.value:
                matched = ct
                break
        if matched:
            idx = order.index(matched)
            _show_spotlight(idx)
            continue

        # Unknown input
        console.print("  [dim]Enter 1-9 to preview a captain, 0 for custom, or q to quit.[/dim]")


def _create_custom_game(name: str) -> None:
    """Interactive custom captain builder."""
    from portlight.engine.captain_identity import CAPTAIN_TEMPLATES, CaptainType
    from portlight.engine.custom_captain import CustomCaptainSpec, build_custom_template, validate_spec

    console.print("\n[bold cyan]--- Custom Captain Builder ---[/bold cyan]")
    console.print("Distribute [bold]10 skill points[/bold] across 4 categories.\n")

    # Point allocation
    console.print("  [bold]Trade[/bold]      — better buy/sell prices, lower port fees")
    console.print("  [bold]Sailing[/bold]    — faster travel, less provisions, storm resistance")
    console.print("  [bold]Shadow[/bold]     — inspection evasion, underworld connections")
    console.print("  [bold]Reputation[/bold] — starting trust and regional standing\n")

    trade = typer.prompt("Trade points (0-6)", default=2, type=int)
    sailing = typer.prompt("Sailing points (0-6)", default=3, type=int)
    shadow = typer.prompt("Shadow points (0-6)", default=3, type=int)
    reputation = typer.prompt("Reputation points (0-6)", default=2, type=int)

    total = trade + sailing + shadow + reputation
    if total != 10:
        console.print(f"[red]Points must total 10 (got {total}). Try again.[/red]")
        raise typer.Exit(1)

    # Home port
    console.print("\n[bold]Choose home port:[/bold]")
    home_ports = {
        "1": ("porto_novo", "Mediterranean"),
        "2": ("corsairs_rest", "Mediterranean"),
        "3": ("ironhaven", "North Atlantic"),
        "4": ("sun_harbor", "West Africa"),
        "5": ("crosswind_isle", "East Indies"),
        "6": ("coral_throne", "South Seas"),
    }
    for k, (pid, region) in home_ports.items():
        console.print(f"  [{k}] {pid.replace('_', ' ').title()} ({region})")
    port_choice = typer.prompt("Home port", default="1")
    port_id, region = home_ports.get(port_choice, ("porto_novo", "Mediterranean"))

    # Title
    title = typer.prompt("Captain title", default="Freelance Captain")

    spec = CustomCaptainSpec(
        name=name,
        title=title,
        home_port_id=port_id,
        home_region=region,
        trade_points=trade,
        sailing_points=sailing,
        shadow_points=shadow,
        reputation_points=reputation,
    )

    errors = validate_spec(spec)
    if errors:
        for e in errors:
            console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    template = build_custom_template(spec)

    # Register the template temporarily so new_game can find it
    CAPTAIN_TEMPLATES[CaptainType.CUSTOM] = template

    s = GameSession(slot=_active_slot)
    s.new(name, captain_type="custom")
    console.print("\n[bold green]A new voyage begins.[/bold green]\n")
    console.print(views.welcome_view(s.captain, s.captain_template, s.world, s.infra))
    console.print(f"\n[dim]Build: Trade {trade} / Sailing {sailing} / Shadow {shadow} / Reputation {reputation}[/dim]")
    console.print(f"[dim]Home: {port_id.replace('_', ' ').title()} ({region})[/dim]")


# ---------------------------------------------------------------------------
# Textual TUI
# ---------------------------------------------------------------------------

@app.command()
def tui() -> None:
    """Launch interactive terminal UI."""
    try:
        from portlight.app.tui.app import StarFreightApp
    except ImportError:
        console.print("[red]Textual not installed.[/red] Install with: [bold]pip install portlight[tui][/bold]")
        raise typer.Exit(1)
    s = GameSession(slot=_active_slot)
    tui_app = StarFreightApp(session=s)
    tui_app.run()


# ---------------------------------------------------------------------------
# Captain identity
# ---------------------------------------------------------------------------

@app.command()
def captain() -> None:
    """Show captain identity and advantages."""
    s = _session()
    t = s.captain_template
    if not t:
        console.print("[red]Unknown captain type[/red]")
        return
    console.print(views.captain_view(s.captain, t))


# ---------------------------------------------------------------------------
# Reputation
# ---------------------------------------------------------------------------

@app.command()
def reputation() -> None:
    """Show standing, customs heat, and commercial trust."""
    s = _session()
    console.print(views.reputation_view(s.captain.standing, s.captain))


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@app.command()
def status() -> None:
    """Show captain status."""
    s = _session()
    console.print(views.status_view(s.world, s.ledger, s.infra))


# ---------------------------------------------------------------------------
# Port
# ---------------------------------------------------------------------------

@app.command()
def port() -> None:
    """Show current port info."""
    s = _session()
    p = s.current_port
    if not p:
        console.print("[yellow]You're at sea. Use [bold]portlight advance[/bold] to continue sailing.[/yellow]")
        return
    console.print(views.port_view(p, s.captain))


# ---------------------------------------------------------------------------
# Market
# ---------------------------------------------------------------------------

@app.command()
def market() -> None:
    """Show market board for current port."""
    s = _session()
    p = s.current_port
    if not p:
        console.print("[yellow]You're at sea — no market here.[/yellow]")
        return
    console.print(views.market_view(p, s.captain))


# ---------------------------------------------------------------------------
# Cargo
# ---------------------------------------------------------------------------

@app.command()
def cargo() -> None:
    """Show cargo hold contents."""
    s = _session()
    console.print(views.cargo_view(s.captain))


# ---------------------------------------------------------------------------
# Buy
# ---------------------------------------------------------------------------

@app.command()
def buy(good: str, qty: str) -> None:
    """Buy goods from port market."""
    try:
        quantity = int(qty)
    except ValueError:
        console.print(f"[red]Invalid quantity: {qty}[/red]")
        return
    if quantity <= 0:
        console.print("[red]Quantity must be a positive number.[/red]")
        return
    s = _session()
    result = s.buy(good, quantity)
    if isinstance(result, str):
        console.print(f"[red]{result}[/red]")
        return
    # Show updated market + cargo after trade
    from portlight.app.formatting import silver
    console.print(f"\n[green]Bought {result.quantity}x {result.good_id} for {silver(result.total_price)}[/green]\n")

    # Warn if remaining silver is too low for port fees
    port = s.current_port
    if port and s.captain.silver < port.port_fee:
        console.print(f"[yellow]Warning: You have {silver(s.captain.silver)} left — "
                       f"port fee to depart is {silver(port.port_fee)}. "
                       f"You may need to sell cargo, hunt, or work the docks.[/yellow]\n")

    console.print(views.market_view(s.current_port, s.captain))
    console.print(views.cargo_view(s.captain))


# ---------------------------------------------------------------------------
# Sell
# ---------------------------------------------------------------------------

@app.command()
def sell(good: str, qty: str) -> None:
    """Sell goods to port market."""
    try:
        quantity = int(qty)
    except ValueError:
        console.print(f"[red]Invalid quantity: {qty}[/red]")
        return
    if quantity <= 0:
        console.print("[red]Quantity must be a positive number.[/red]")
        return
    s = _session()
    result = s.sell(good, quantity)
    if isinstance(result, str):
        console.print(f"[red]{result}[/red]")
        return
    from portlight.app.formatting import silver
    # Show sale result
    console.print(f"\n[green]Sold {result.quantity}x {result.good_id} for {silver(result.total_price)}[/green]\n")
    console.print(views.market_view(s.current_port, s.captain))
    console.print(views.cargo_view(s.captain))


# ---------------------------------------------------------------------------
# Provision
# ---------------------------------------------------------------------------

@app.command()
def provision(days: int = typer.Argument(10, help="Days of provisions to buy")) -> None:
    """Buy provisions (2 silver per day)."""
    s = _session()
    err = s.provision(days)
    if err:
        console.print(f"[red]{err}[/red]")
        return
    from portlight.app.formatting import provision_status, silver
    console.print(f"[green]Provisioned for {days} days ({silver(days * 2)})[/green]")
    console.print(f"Provisions: {provision_status(s.captain.provisions)}")
    console.print(f"Silver: {silver(s.captain.silver)}")


# ---------------------------------------------------------------------------
# Repair
# ---------------------------------------------------------------------------

@app.command()
def repair(amount: int = typer.Argument(None, help="Hull points to repair (default: full)")) -> None:
    """Repair ship hull (3 silver per HP)."""
    s = _session()
    result = s.repair(amount)
    if isinstance(result, str):
        console.print(f"[red]{result}[/red]")
        return
    repaired, cost = result
    from portlight.app.formatting import hull_bar, silver
    console.print(f"[green]Repaired {repaired} hull points ({silver(cost)})[/green]")
    console.print(f"Hull: {hull_bar(s.captain.ship.hull, s.captain.ship.hull_max)}")
    console.print(f"Silver: {silver(s.captain.silver)}")


# ---------------------------------------------------------------------------
# Hunting (anti-soft-lock)
# ---------------------------------------------------------------------------

@app.command()
def hunt() -> None:
    """Hunt or forage for provisions, pelts, and silver. Works at port or at sea.

    Port hunting is safe and reliable. Sea hunting yields more but carries
    dangers: crew injuries, hull damage, predator encounters.
    """
    from portlight.engine.hunting import hunt as do_hunt
    from portlight.engine.models import CargoItem
    s = _session()
    location = "sea" if s.world.voyage and s.world.voyage.status.value == "at_sea" else "port"

    if location == "sea" and s.captain.ship and s.captain.ship.morale < 20:
        console.print("[yellow]Crew morale too low for hunting at sea (need 20+).[/yellow]")
        return

    crew_count = s.captain.ship.crew if s.captain.ship else 1
    result = do_hunt(s.captain, location, crew_count, s._rng)
    # hunt() advances captain.day but not world.day — keep them in sync
    s.world.day = s.captain.day

    console.print(f"\n[bold]Hunting {'at port' if location == 'port' else 'at sea'}...[/bold]")
    console.print(f"  {result.flavor}")

    if result.success:
        if result.provisions_gained > 0:
            s.captain.provisions += result.provisions_gained
            console.print(f"  [green]+{result.provisions_gained} provisions[/green]")
        if result.pelts_gained > 0:
            # Add pelts to cargo
            existing = next((c for c in s.captain.cargo if c.good_id == "pelts"), None)
            if existing:
                existing.quantity += result.pelts_gained
            else:
                s.captain.cargo.append(CargoItem(
                    good_id="pelts", quantity=result.pelts_gained,
                    cost_basis=0, acquired_port=s.current_port.id if s.current_port else "",
                    acquired_region="", acquired_day=s.captain.day,
                ))
            total_pelts = existing.quantity if existing else result.pelts_gained
            console.print(f"  [green]+{result.pelts_gained} pelts[/green]  [dim](sell at any port: sell pelts {total_pelts})[/dim]")
        if result.silver_gained > 0:
            s.captain.silver += result.silver_gained
            from portlight.app.formatting import silver
            console.print(f"  [green]+{silver(result.silver_gained)}[/green]")
    else:
        console.print("  [dim]Nothing useful found.[/dim]")

    # Apply dangers
    if result.danger_text:
        console.print(f"  [red]{result.danger_text}[/red]")
    if result.crew_lost > 0 and s.captain.ship:
        s.captain.ship.crew = max(1, s.captain.ship.crew - result.crew_lost)
        console.print(f"  [red]Lost {result.crew_lost} crew member{'s' if result.crew_lost > 1 else ''}.[/red]")
    if result.hull_damage > 0 and s.captain.ship:
        s.captain.ship.hull = max(1, s.captain.ship.hull - result.hull_damage)
        console.print(f"  [red]Hull damage: -{result.hull_damage} HP[/red]")

    if result.morale_cost > 0 and s.captain.ship:
        s.captain.ship.morale = max(0, s.captain.ship.morale - result.morale_cost)
        console.print(f"  [yellow]Morale -{result.morale_cost}[/yellow]")

    console.print(f"  Day {s.captain.day}.")
    s._save()


# ---------------------------------------------------------------------------
# Work the docks (anti-soft-lock)
# ---------------------------------------------------------------------------

@app.command()
def work() -> None:
    """Work the docks for a day to earn silver. Safety valve when stranded."""
    from portlight.engine.economy import work_docks
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to work the docks.[/yellow]")
        return
    earned = work_docks(s.captain, s._rng)
    # work_docks() advances captain.day but not world.day — keep them in sync
    s.world.day = s.captain.day
    console.print(f"\n[bold]Day's work on the {s.current_port.name} docks.[/bold]")
    console.print("  Hauled crates, mended rope, cleaned bilges.")
    console.print(f"  Earned [green]{earned} silver[/green]. Day {s.captain.day}.")
    s._save()


# ---------------------------------------------------------------------------
# Hire
# ---------------------------------------------------------------------------

@app.command()
def hire(
    count: int = typer.Argument(None, help="Crew to hire (default: 1)"),
    role: str = typer.Option("sailor", "--role", "-r", help="Role: sailor, gunner, navigator, surgeon, marine, quartermaster"),
) -> None:
    """Hire crew members. Specify role with --role."""
    s = _session()
    if count is None:
        count = 1
    err = s.hire_crew(count, role)
    if err:
        console.print(f"[red]{err}[/red]")
        return
    from portlight.app.formatting import crew_status
    ship = s.captain.ship
    from portlight.content.ships import SHIPS
    template = SHIPS.get(ship.template_id)
    crew_min = template.crew_min if template else 1
    console.print(f"[green]Hired {count} {role}(s)[/green]")
    console.print(f"Crew: {crew_status(ship.crew, ship.crew_max, crew_min)}")


@app.command()
def fire(
    count: int = typer.Argument(None, help="Crew to fire (default: 1)"),
    role: str = typer.Option("sailor", "--role", "-r", help="Role: sailor, gunner, navigator, surgeon, marine, quartermaster"),
) -> None:
    """Fire crew members. Specify role with --role."""
    s = _session()
    if count is None:
        count = 1
    # Track actual count before firing for accurate message
    from portlight.engine.models import CrewRole
    from portlight.content.crew_roles import get_role_count
    try:
        crew_role = CrewRole(role.lower())
    except ValueError:
        crew_role = None
    before = get_role_count(s.captain.ship.roster, crew_role) if crew_role and s.captain.ship else 0
    err = s.fire_crew(count, role)
    if err:
        console.print(f"[red]{err}[/red]")
        return
    actual_fired = min(count, before)
    console.print(f"[yellow]Fired {actual_fired} {role}(s).[/yellow]")


@app.command(name="crew")
def crew_cmd() -> None:
    """Show crew roster breakdown."""
    s = _session()
    console.print(views.crew_roster_view(s.captain.ship))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.command()
def routes() -> None:
    """List available routes from current port."""
    s = _session()
    if s.at_sea:
        console.print("[yellow]You're at sea — check routes when you arrive.[/yellow]")
        return
    console.print(views.routes_view(s.world))


# ---------------------------------------------------------------------------
# Map
# ---------------------------------------------------------------------------

@app.command(name="map")
def world_map(
    routes: bool = typer.Option(False, "--routes", "-r", help="Show trade route lines"),
    region: str | None = typer.Option(None, "--region", help="Filter to region (med/atl/afr/ind/sea)"),
) -> None:
    """Display the world map with all ports and regions."""
    s = _session()
    player_port = s.current_port_id
    console.print(views.world_map_view(
        s.world, player_port_id=player_port,
        show_routes=routes, region_filter=region,
    ))


# ---------------------------------------------------------------------------
# Sail
# ---------------------------------------------------------------------------

@app.command()
def sail(
    destination: str,
    defer: bool = typer.Option(False, "--defer", help="Defer port fee (pay double on arrival)"),
) -> None:
    """Depart for a destination port."""
    s = _session()
    err = s.sail(destination, defer_fee=defer)
    if err:
        console.print(f"[red]{err}[/red]")
        # Show routes to help
        if s.current_port:
            console.print()
            console.print(views.routes_view(s.world))
        return
    dest = s.world.ports.get(destination)
    dest_name = dest.name if dest else destination
    console.print(f"\n[bold cyan]Setting sail for {dest_name}![/bold cyan]\n")
    console.print(views.voyage_view(s.world))


# ---------------------------------------------------------------------------
# Advance
# ---------------------------------------------------------------------------

@app.command()
def advance(days: int = typer.Argument(1, help="Days to advance")) -> None:
    """Advance time (sail if at sea, wait if in port)."""
    global _active_encounter, _player_combatant, _opponent_combatant
    s = _session()

    # Block if there's an unresolved encounter (persisted or in-memory)
    _restore_encounter(s)
    if _active_encounter is not None:
        console.print("[bold red]Encounter in progress![/bold red] Resolve it first:")
        phase = getattr(_active_encounter, "phase", "approach")
        if phase == "approach":
            console.print("  [cyan]portlight encounter <negotiate|flee|fight>[/cyan]")
        elif phase == "naval":
            console.print("  [cyan]portlight naval <broadside|close|evade|rake|flee>[/cyan]")
        elif phase == "boarding":
            console.print("  [cyan]portlight fight <thrust|slash|parry|shoot|throw|dodge>[/cyan]")
        elif phase == "duel":
            console.print("  [cyan]portlight fight <thrust|slash|parry|shoot|throw|dodge>[/cyan]")
        elif phase == "resolved":
            console.print("  [cyan]portlight spare[/cyan] or [cyan]portlight take-all[/cyan]")
        return

    for _ in range(days):
        was_at_sea = s.at_sea
        events = s.advance()

        # Tick NPC captain agency (autonomous actions)
        if s.world and s.at_sea:
            from portlight.engine.captain_memory import tick_captain_agency
            region = s._voyage_region() if hasattr(s, '_voyage_region') else "Mediterranean"
            captain_actions = tick_captain_agency(
                s.world.pirates.captain_memories, region,
                s.captain.silver, s.world.day, s._rng,
            )
            for ca in captain_actions:
                if ca.effect_type == "encounter" and _active_encounter is None:
                    # Ambush or challenge — create encounter immediately
                    from portlight.engine.encounter import create_encounter
                    enc = create_encounter(s.world.ports, s.world.voyage.destination_id if s.world.voyage else "porto_novo", s._rng)
                    if enc:
                        enc.enemy_captain_id = ca.captain_id
                        enc.enemy_captain_name = ca.captain_name
                        _active_encounter = enc
                        _player_combatant = None
                        _opponent_combatant = None
                        from portlight.app import combat_views
                        console.print(f"\n[bold red]{ca.message}[/bold red]")
                        console.print(combat_views.encounter_view(
                            enc.enemy_captain_name, "", enc.enemy_personality, enc.enemy_strength,
                            f"{enc.enemy_captain_name}'s Ship", ca.message,
                        ))
                        if ca.verb == "ambush":
                            enc.phase = "naval"  # no negotiate for ambushes
                            console.print("\n[bold red]No time to negotiate! Use [cyan]portlight naval <action>[/cyan][/bold red]")
                        else:
                            console.print("\n[bold]Use [cyan]portlight encounter <negotiate|flee|fight>[/cyan][/bold]")
                        s._save()
                        break
                elif ca.effect_type == "silver":
                    s.captain.silver += ca.effect_value
                    console.print(f"\n[dim]{ca.message}[/dim]")
                elif ca.effect_type == "message":
                    console.print(f"\n[dim]{ca.message}[/dim]")

            if _active_encounter is not None:
                break  # stop advancing — handle encounter first

        # Check for pirate encounter — intercept and create interactive encounter
        pirate_event = None
        for evt in events:
            if hasattr(evt, '_pending_duel') and evt._pending_duel is not None:
                pirate_event = evt
                break

        if pirate_event and pirate_event._pending_duel:
            console.print(views.voyage_view(s.world, events))
            # Create interactive encounter from the pending duel
            from portlight.engine.encounter import create_encounter
            enc = create_encounter(
                s.world.ports, s.world.voyage.destination_id if s.world.voyage else "porto_novo",
                s._rng,
            )
            if enc:
                # Override with the specific captain from the event
                pd = pirate_event._pending_duel
                enc.enemy_captain_id = pd.captain_id
                enc.enemy_captain_name = pd.captain_name
                enc.enemy_faction_id = pd.faction_id
                enc.enemy_personality = pd.personality
                enc.enemy_strength = pd.strength
                enc.enemy_region = pd.region

                _active_encounter = enc
                _player_combatant = None
                _opponent_combatant = None
                # Keep pending_duel set so encounter persists across CLI invocations
                # It will be cleared when the encounter resolves

                from portlight.app import combat_views
                from portlight.content.factions import FACTIONS, PIRATE_CAPTAINS
                faction = FACTIONS.get(pd.faction_id)
                captain_data = PIRATE_CAPTAINS.get(pd.captain_id)
                try:
                    console.print(combat_views.encounter_view(
                        pd.captain_name,
                        faction.name if faction else "Unknown",
                        pd.personality, pd.strength,
                        f"{pd.captain_name}'s Ship",
                        captain_data.encounter_text if captain_data else "",
                    ))
                except Exception as e:
                    console.print(f"\n[bold red]Pirate encounter: {pd.captain_name} ({pd.personality}, str {pd.strength})[/bold red]")
                    console.print(f"[dim]View error: {e}[/dim]")
                # Check weapon recognition
                gear = s.captain.combat_gear
                if gear.melee_weapon and gear.weapon_provenance.get(gear.melee_weapon):
                    from portlight.engine.weapon_provenance import WeaponProvenance, check_recognition
                    prov = gear.weapon_provenance[gear.melee_weapon]
                    if isinstance(prov, WeaponProvenance):
                        from portlight.engine.captain_memory import get_or_create_memory
                        cap_mem = get_or_create_memory(s.world.pirates.captain_memories, pd.captain_id)
                        recog = check_recognition(
                            prov, gear.melee_weapon.replace("_", " ").title(),
                            pd.captain_id, cap_mem.relationship.familiarity, s._rng,
                        )
                        if recog.recognized:
                            console.print(f"\n[bold]{recog.flavor}[/bold]")
                            # Apply fear/respect bonus to captain memory
                            cap_mem.relationship.fear = min(100, cap_mem.relationship.fear + recog.fear_bonus)
                            cap_mem.relationship.respect = min(100, cap_mem.relationship.respect + recog.respect_bonus)

                console.print("\n[bold]Use [cyan]portlight encounter <negotiate|flee|fight>[/cyan][/bold]")
                break  # stop advancing — player must respond to encounter
            else:
                console.print(views.voyage_view(s.world, events))
        elif events:
            console.print(views.voyage_view(s.world, events))
        else:
            console.print(f"[dim]Day {s.world.day}. Markets shift.[/dim]")

        # Check if arrived (only show arrival if we transitioned from sea)
        if s.current_port and was_at_sea:
            port = s.current_port
            console.print(f"\n[bold green]Arrived at {port.name}![/bold green]\n")
            console.print(views.port_view(port, s.captain))
            console.print(views.status_view(s.world, s.ledger, s.infra))
            break

        # Check if ship sank
        if s.captain.ship and s.captain.ship.hull <= 0:
            console.print("\n[bold red]Your ship has broken apart. The voyage ends here.[/bold red]")
            break


# ---------------------------------------------------------------------------
# Duel
# ---------------------------------------------------------------------------

@app.command()
def duel(
    stances: str = typer.Argument(..., help="Comma-separated stances: thrust,slash,parry (5 rounds)"),
) -> None:
    """Fight a pirate captain in a sword duel. Stances: thrust, slash, parry."""
    s = _session()
    pending = s.world.pirates.pending_duel
    if pending is None:
        console.print("[yellow]No pirate has challenged you. Duels happen during pirate encounters at sea.[/yellow]")
        return

    # Parse stances
    stance_list = [st.strip().lower() for st in stances.split(",")]
    valid = {"thrust", "slash", "parry"}
    for st in stance_list:
        if st not in valid:
            console.print(f"[red]Invalid stance: {st}[/red]. Use: thrust, slash, parry")
            return
    if len(stance_list) < 3:
        console.print("[red]Provide at least 3 stances (e.g. thrust,parry,slash,thrust,parry)[/red]")
        return

    from portlight.engine.duel import resolve_duel
    from portlight.engine.models import PirateEncounterRecord

    result = resolve_duel(
        player_stances=stance_list,
        opponent_id=pending.captain_id,
        opponent_name=pending.captain_name,
        opponent_personality=pending.personality,
        opponent_strength=pending.strength,
        rng=s._rng,
        player_crew=s.captain.ship.crew if s.captain.ship else 5,
    )

    # Show round-by-round
    console.print(f"\n[bold]Duel vs {pending.captain_name}[/bold] (strength {pending.strength}, {pending.personality})\n")
    for i, r in enumerate(result.rounds, 1):
        outcome = "WIN" if r.damage_to_opponent > 0 and r.damage_to_player == 0 else (
            "LOSE" if r.damage_to_player > 0 and r.damage_to_opponent == 0 else "DRAW"
        )
        console.print(f"  Round {i}: You [{r.player_stance}] vs [{r.opponent_stance}] — {outcome}")
        console.print(f"    {r.flavor}")

    # Show result
    if result.player_won:
        console.print(f"\n[bold green]VICTORY![/bold green] You defeated {pending.captain_name}.")
    elif result.draw:
        console.print("\n[bold yellow]DRAW.[/bold yellow] Neither captain falls.")
    else:
        console.print(f"\n[bold red]DEFEAT.[/bold red] {pending.captain_name} bests you.")

    # Apply consequences
    s.captain.silver = max(0, s.captain.silver + result.silver_delta)
    from portlight.app.formatting import silver
    if result.silver_delta >= 0:
        console.print(f"  Silver: +{silver(result.silver_delta)}")
    else:
        console.print(f"  Silver: -{silver(abs(result.silver_delta))}")

    # Record encounter
    outcome_str = "duel_win" if result.player_won else ("duel_draw" if result.draw else "duel_loss")
    s.world.pirates.encounters.append(PirateEncounterRecord(
        captain_id=pending.captain_id,
        faction_id=pending.faction_id,
        day=s.world.day,
        outcome=outcome_str,
        region=pending.region,
    ))
    if result.player_won:
        s.world.pirates.duels_won += 1
    elif not result.draw:
        s.world.pirates.duels_lost += 1

    # Clear pending duel
    s.world.pirates.pending_duel = None
    s._save()


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------

@app.command()
def ledger() -> None:
    """Show trade receipt ledger."""
    s = _session()
    console.print(views.ledger_view(s.ledger, s.captain))


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

@app.command()
def inventory() -> None:
    """Show all personal gear: armor, weapons, styles, ranged, injuries, cargo."""
    s = _session()
    gear = s.captain.combat_gear

    # Build gear data dict for the view
    from portlight.content.armor import ARMOR
    from portlight.content.melee_weapons import MELEE_WEAPONS
    from portlight.content.ranged_weapons import RANGED_WEAPONS
    from portlight.content.fighting_styles import FIGHTING_STYLES

    armor_def = ARMOR.get(gear.armor) if gear.armor else None
    melee_def = MELEE_WEAPONS.get(gear.melee_weapon) if gear.melee_weapon else None
    firearm_def = RANGED_WEAPONS.get(gear.firearm) if gear.firearm else None
    mechanical_def = RANGED_WEAPONS.get(gear.mechanical_weapon) if gear.mechanical_weapon else None
    style_def = FIGHTING_STYLES.get(s.captain.active_style) if s.captain.active_style else None

    throwing_summary = []
    for wid, count in gear.throwing_weapons.items():
        w = RANGED_WEAPONS.get(wid)
        throwing_summary.append({"name": w.name if w else wid, "count": count})

    from portlight.content.injuries import INJURIES
    injuries_data = []
    for inj in s.captain.injuries:
        idef = INJURIES.get(inj.injury_id)
        if idef:
            if inj.heal_remaining is None:
                healing = "Permanent"
            elif inj.heal_remaining <= 0:
                healing = "Healed"
            else:
                healing = f"{inj.heal_remaining} days"
            injuries_data.append({
                "name": idef.name,
                "severity": idef.severity,
                "healing": healing,
            })

    ship_upgrades = []
    if s.captain.ship and hasattr(s.captain.ship, 'upgrades'):
        from portlight.content.upgrades import UPGRADES
        for u in s.captain.ship.upgrades:
            uid = u.upgrade_id if hasattr(u, 'upgrade_id') else u
            udef = UPGRADES.get(uid)
            ship_upgrades.append(udef.name if udef else uid)

    cargo_used = sum(c.quantity for c in s.captain.cargo)
    cargo_cap = s.captain.ship.cargo_capacity if s.captain.ship else 0

    gear_data = {
        "armor_name": armor_def.name if armor_def else "None",
        "armor_dr": armor_def.damage_reduction if armor_def else 0,
        "armor_type": armor_def.armor_type if armor_def else "",
        "melee_name": melee_def.name if melee_def else "Fists",
        "melee_bonus": f"+{melee_def.damage_bonus} dmg" if melee_def else "",
        "active_style": style_def.name if style_def else "None",
        "style_special": style_def.special_action.name if style_def and style_def.special_action else "",
        "firearm_name": firearm_def.name if firearm_def else "None",
        "firearm_ammo": gear.firearm_ammo,
        "mechanical_name": mechanical_def.name if mechanical_def else "None",
        "mechanical_ammo": gear.mechanical_ammo,
        "throwing_summary": throwing_summary,
        "injuries": injuries_data,
        "ship_upgrades": ship_upgrades,
        "cargo_used": cargo_used,
        "cargo_capacity": cargo_cap,
        "silver": s.captain.silver,
    }
    from portlight.app.combat_views import inventory_view as inv_view
    console.print(inv_view(gear_data))


# ---------------------------------------------------------------------------
# Equip (armor + melee weapon)
# ---------------------------------------------------------------------------

@app.command()
def equip(
    slot: str = typer.Argument(..., help="What to equip: armor, weapon, or 'remove'"),
    item_id: str = typer.Argument(None, help="Item ID to equip, or slot to remove (armor/weapon)"),
) -> None:
    """Equip or unequip armor and melee weapons."""
    s = _session()
    gear = s.captain.combat_gear

    if slot == "remove":
        if item_id == "armor":
            if gear.armor is None:
                console.print("[dim]No armor worn.[/dim]")
                return
            from portlight.content.armor import ARMOR
            old = ARMOR.get(gear.armor)
            gear.armor = None
            s._save()
            console.print(f"[yellow]Removed {old.name if old else 'armor'}.[/yellow]")
        elif item_id == "weapon":
            if gear.melee_weapon is None:
                console.print("[dim]No melee weapon equipped.[/dim]")
                return
            from portlight.content.melee_weapons import MELEE_WEAPONS
            old = MELEE_WEAPONS.get(gear.melee_weapon)
            gear.melee_weapon = None
            s._save()
            console.print(f"[yellow]Stowed {old.name if old else 'weapon'}.[/yellow]")
        else:
            console.print("[red]Usage: portlight equip remove armor|weapon[/red]")
        return

    if slot == "armor":
        if item_id is None:
            console.print("[red]Usage: portlight equip armor <armor_id>[/red]")
            return
        from portlight.content.armor import ARMOR
        armor_def = ARMOR.get(item_id)
        if armor_def is None:
            console.print(f"[red]Unknown armor: {item_id}[/red]")
            return
        gear.armor = item_id
        s._save()
        console.print(f"[green]Equipped {armor_def.name} (DR {armor_def.damage_reduction}).[/green]")

    elif slot == "weapon":
        if item_id is None:
            console.print("[red]Usage: portlight equip weapon <weapon_id>[/red]")
            return
        from portlight.content.melee_weapons import MELEE_WEAPONS
        weapon_def = MELEE_WEAPONS.get(item_id)
        if weapon_def is None:
            console.print(f"[red]Unknown weapon: {item_id}[/red]")
            return
        gear.melee_weapon = item_id
        s._save()
        console.print(f"[green]Equipped {weapon_def.name} (+{weapon_def.damage_bonus} dmg).[/green]")

    else:
        console.print(f"[red]Unknown slot: {slot}[/red]. Use: armor, weapon, or remove")


# ---------------------------------------------------------------------------
# Merchant
# ---------------------------------------------------------------------------

@app.command()
def merchant(
    merchant_id: str = typer.Argument(None, help="Merchant ID to browse, or omit to list"),
    buy_item: str = typer.Argument(None, help="Item ID to buy from this merchant"),
    qty: int = typer.Argument(1, help="Quantity to buy"),
) -> None:
    """Browse or buy from port merchants."""
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to visit merchants.[/yellow]")
        return

    from portlight.content.merchants import get_merchants_at_port, get_merchant
    from portlight.engine.merchant import buy_from_merchant, get_merchant_inventory
    from portlight.app.combat_views import merchant_list_view, merchant_shop_view

    port = s.current_port

    if merchant_id is None:
        # List merchants at port
        merchants = get_merchants_at_port(port.id)
        data = [{
            "id": m.id, "name": m.name, "title": m.title,
            "greeting": m.greeting,
            "inventory_types": list(m.inventory_types),
            "markup": m.price_markup,
        } for m in merchants]
        console.print(merchant_list_view(data, port.name))
        return

    m = get_merchant(merchant_id)
    if m is None:
        # Try partial match
        merchants = get_merchants_at_port(port.id)
        matches = [me for me in merchants if merchant_id in me.id]
        if len(matches) == 1:
            m = matches[0]
        else:
            console.print(f"[red]Unknown merchant: {merchant_id}[/red]")
            return

    if m.port_id != port.id:
        console.print(f"[red]{m.name} is not at {port.name}.[/red]")
        return

    if buy_item is None:
        # Show merchant's inventory
        inv = get_merchant_inventory(m, port.region)
        console.print(merchant_shop_view(m.name, m.greeting, inv, s.captain.silver))
        return

    # Buy from merchant
    result = buy_from_merchant(s.captain, m.id, buy_item, qty, port.region)
    if isinstance(result, str):
        console.print(f"[red]{result}[/red]")
        return
    from portlight.app.formatting import silver
    console.print(
        f"\n[green]Bought {result['item_name']} from {m.name} "
        f"for {silver(result['total_cost'])}[/green]"
    )
    s._save()


# ---------------------------------------------------------------------------
# Sell gear (anti-soft-lock)
# ---------------------------------------------------------------------------

@app.command(name="sell-gear")
def sell_gear(item_id: str = typer.Argument(..., help="Weapon or armor ID to sell back")) -> None:
    """Sell a weapon or armor back to the port for 50% of its value."""
    from portlight.engine.economy import sell_gear_value
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to sell gear.[/yellow]")
        return

    gear = s.captain.combat_gear
    # Build a lookup of what we can sell
    sellable: dict[str, str] = {}  # item_id -> field_name
    if gear.melee_weapon:
        sellable[gear.melee_weapon] = "melee_weapon"
    if gear.firearm:
        sellable[gear.firearm] = "firearm"
    if gear.mechanical_weapon:
        sellable[gear.mechanical_weapon] = "mechanical_weapon"
    if gear.armor:
        sellable[gear.armor] = "armor"

    if item_id not in sellable:
        console.print(f"[yellow]You don't have '{item_id}' equipped. Sellable: {', '.join(sellable) or 'nothing'}[/yellow]")
        return

    # Get price from weapon/armor tables
    from portlight.content.melee_weapons import MELEE_WEAPONS
    from portlight.content.armor import ARMOR
    tables: dict[str, object] = {}
    tables.update(MELEE_WEAPONS)
    tables.update(ARMOR)
    price = sell_gear_value(item_id, tables)
    if price is None:
        console.print(f"[red]Cannot determine value of {item_id}.[/red]")
        return

    # Remove the item and pay the captain
    setattr(gear, sellable[item_id], None)
    s.captain.silver += price
    console.print(f"\n[green]Sold {item_id} for {price} silver.[/green]")
    s._save()


# ---------------------------------------------------------------------------
# Shipyard
# ---------------------------------------------------------------------------

@app.command()
def shipyard(buy_ship: str = typer.Argument(None, help="Ship ID to purchase")) -> None:
    """View or buy ships at the shipyard."""
    from portlight.engine.models import PortFeature
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to visit the shipyard.[/yellow]")
        return

    has_shipyard = PortFeature.SHIPYARD in s.current_port.features

    if buy_ship:
        if not has_shipyard:
            console.print(f"[yellow]{s.current_port.name} has no shipyard.[/yellow]")
            return
        err = s.buy_ship(buy_ship)
        if err:
            console.print(f"[red]{err}[/red]")
        else:
            console.print("\n[bold green]Ship purchased![/bold green]\n")
            console.print(views.status_view(s.world, s.ledger, s.infra))
    else:
        if not has_shipyard:
            console.print(f"[yellow]{s.current_port.name} has no shipyard. Browse only — no purchases available.[/yellow]\n")
        console.print(views.shipyard_view(s.captain))


@app.command()
def drydock(
    ship: str = typer.Option(None, "--ship", "-s", help="Fleet ship name (default: flagship)"),
) -> None:
    """Restore degraded hull_max at a shipyard. Costs 5x normal repair rate."""
    s = _session()
    result = s.dry_dock(ship)
    if isinstance(result, str):
        console.print(f"[red]{result}[/red]")
    else:
        restored, cost = result
        console.print(f"[green]Dry dock complete! Restored {restored} hull points for {cost} silver.[/green]")
        console.print(views.status_view(s.world, s.ledger, s.infra))


@app.command()
def rename(
    new_name: str = typer.Argument(..., help="New name for the ship"),
    ship: str = typer.Option(None, "--ship", "-s", help="Name of fleet ship to rename (default: flagship)"),
) -> None:
    """Rename your flagship or a fleet ship."""
    s = _session()
    err = s.rename_ship(new_name, ship)
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        target = ship or "flagship"
        console.print(f"[green]Renamed {target} to '{new_name}'[/green]")


@app.command()
def fleet() -> None:
    """Show all ships in your fleet."""
    s = _session()
    console.print(views.fleet_view(s.captain))


@app.command()
def dock() -> None:
    """Park current ship and switch to another at the same port."""
    s = _session()
    err = s.dock_current_ship()
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        console.print("\n[bold green]Switched ships![/bold green]\n")
        console.print(views.status_view(s.world, s.ledger, s.infra))


@app.command()
def board(ship_name: str = typer.Argument(..., help="Name of ship to board")) -> None:
    """Switch to a docked ship at the same port."""
    s = _session()
    err = s.board_fleet_ship(ship_name)
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        console.print("\n[bold green]Boarded new flagship![/bold green]\n")
        console.print(views.status_view(s.world, s.ledger, s.infra))


@app.command()
def transfer(
    good: str = typer.Argument(..., help="Good ID to transfer"),
    qty: int = typer.Argument(..., help="Quantity"),
    from_ship: str = typer.Argument(..., help="Source ship name"),
    to_ship: str = typer.Argument(..., help="Destination ship name"),
) -> None:
    """Move cargo between ships at the same port."""
    s = _session()
    err = s.transfer_fleet_cargo(good, qty, from_ship, to_ship)
    if err:
        console.print(f"[red]{err}[/red]")
    else:
        console.print(f"\n[bold green]Transferred {qty} {good}.[/bold green]\n")


@app.command()
def upgrade(
    upgrade_id: str = typer.Argument(None, help="Upgrade ID to install, or omit to browse"),
    remove: bool = typer.Option(False, "--remove", "-r", help="Remove an installed upgrade"),
) -> None:
    """Browse or install ship upgrades at the shipyard."""
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to visit the shipyard.[/yellow]")
        return

    if upgrade_id and remove:
        err = s.remove_upgrade(upgrade_id)
        if err:
            console.print(f"[red]{err}[/red]")
        else:
            console.print(f"\n[bold green]Removed {upgrade_id}.[/bold green]\n")
            console.print(views.status_view(s.world, s.ledger, s.infra))
    elif upgrade_id:
        err = s.install_upgrade(upgrade_id)
        if err:
            console.print(f"[red]{err}[/red]")
        else:
            console.print("\n[bold green]Upgrade installed![/bold green]\n")
            console.print(views.status_view(s.world, s.ledger, s.infra))
    else:
        console.print(views.upgrade_catalog_view(s.captain))


# ---------------------------------------------------------------------------
# Save / Load (explicit)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

@app.command()
def contracts() -> None:
    """Show the contract board at the current port."""
    s = _session()
    if not s.current_port:
        console.print("[yellow]Must be docked to view the contract board.[/yellow]")
        return
    # Lazy refresh: populate board on first view at this port
    s._refresh_board(s.current_port)
    s._save()
    console.print(views.contracts_view(s.board, s.world.day))


@app.command()
def obligations() -> None:
    """Show active contract obligations."""
    s = _session()
    console.print(views.obligations_view(s.board, s.world.day, s.world))


@app.command()
def accept(offer_id: str) -> None:
    """Accept a contract offer from the board."""
    s = _session()
    # Allow short IDs (first 8 chars)
    matched = next((o for o in s.board.offers if o.id.startswith(offer_id)), None)
    if not matched:
        console.print(f"[red]No offer matching '{offer_id}'. Check the board with: portlight contracts[/red]")
        return
    err = s.accept_contract(matched.id)
    if err:
        console.print(f"[red]{err}[/red]")
        return
    console.print(f"\n[bold green]Contract accepted: {matched.title}[/bold green]\n")
    console.print(views.obligations_view(s.board, s.world.day))


@app.command()
def abandon(offer_id: str) -> None:
    """Abandon an active contract (reputation cost)."""
    s = _session()
    # Allow short IDs
    matched = next((c for c in s.board.active if c.offer_id.startswith(offer_id)), None)
    if not matched:
        console.print(f"[red]No active contract matching '{offer_id}'. Check obligations with: portlight obligations[/red]")
        return
    err = s.abandon_contract_cmd(matched.offer_id)
    if err:
        console.print(f"[red]{err}[/red]")
        return
    console.print(f"\n[yellow]Contract abandoned: {matched.title}[/yellow]")
    console.print("[dim]Reputation penalty applied.[/dim]")


# ---------------------------------------------------------------------------
# Warehouses
# ---------------------------------------------------------------------------

@app.command()
def warehouse(
    action: str = typer.Argument(None, help="lease, deposit, withdraw, or omit to view"),
    arg1: str = typer.Argument(None, help="tier (for lease) or good_id (for deposit/withdraw)"),
    arg2: int = typer.Argument(None, help="quantity (for deposit/withdraw)"),
    source: str = typer.Option(None, "--source", "-s", help="Source port filter for withdraw"),
) -> None:
    """Manage warehouses: view, lease, deposit, or withdraw cargo."""
    s = _session()

    if action is None:
        # Show warehouse status
        port = s.current_port
        port_id = port.id if port else None
        port_name = port.name if port else None
        console.print(views.warehouse_view(s.infra, port_id, port_name))
        return

    if action == "lease":
        if not s.current_port:
            console.print("[yellow]Must be docked to lease a warehouse.[/yellow]")
            return
        if arg1 is None:
            # Show available tiers
            console.print(views.warehouse_lease_options(s.current_port.id))
            return
        from portlight.engine.infrastructure import WarehouseTier
        from portlight.content.infrastructure import available_tiers
        try:
            tier = WarehouseTier(arg1)
        except ValueError:
            console.print(f"[red]Unknown tier: {arg1}[/red]. Options: depot, regional, commercial")
            return
        tiers = available_tiers(s.current_port.id)
        spec = next((t for t in tiers if t.tier == tier), None)
        if not spec:
            console.print(f"[red]{s.current_port.name} does not support {arg1} warehouses.[/red]")
            return
        err = s.lease_warehouse_cmd(spec)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        console.print(f"\n[bold green]Leased {spec.name} at {s.current_port.name}![/bold green]")
        console.print(f"Capacity: {spec.capacity} | Upkeep: {spec.upkeep_per_day}/day")
        console.print(f"Silver: {s.captain.silver}")
        return

    if action == "deposit":
        if arg1 is None or arg2 is None:
            console.print("[red]Usage: portlight warehouse deposit <good> <qty>[/red]")
            return
        result = s.deposit_cmd(arg1, arg2)
        if isinstance(result, str):
            console.print(f"[red]{result}[/red]")
            return
        console.print(f"[green]Deposited {result}x {arg1} into warehouse.[/green]")
        port = s.current_port
        console.print(views.warehouse_view(s.infra, port.id if port else None, port.name if port else None))
        return

    if action == "withdraw":
        if arg1 is None or arg2 is None:
            console.print("[red]Usage: portlight warehouse withdraw <good> <qty> [--source <port>][/red]")
            return
        result = s.withdraw_cmd(arg1, arg2, source)
        if isinstance(result, str):
            console.print(f"[red]{result}[/red]")
            return
        console.print(f"[green]Withdrew {result}x {arg1} from warehouse.[/green]")
        console.print(views.cargo_view(s.captain))
        return

    console.print(f"[red]Unknown warehouse action: {action}[/red]. Use: lease, deposit, withdraw")


# ---------------------------------------------------------------------------
# Broker offices
# ---------------------------------------------------------------------------

@app.command()
def office(
    action: str = typer.Argument(None, help="open, upgrade, or omit to view"),
    region: str = typer.Argument(None, help="Region name (Mediterranean, 'West Africa', 'East Indies')"),
) -> None:
    """Manage broker offices: view, open, or upgrade."""
    s = _session()

    if action is None:
        console.print(views.offices_view(s.infra))
        return

    if action in ("open", "upgrade"):
        if not s.current_port:
            console.print("[yellow]Must be docked to manage broker offices.[/yellow]")
            return
        port_region = s.current_port.region
        target_region = region or port_region

        from portlight.engine.infrastructure import BrokerTier, get_broker_tier
        from portlight.content.infrastructure import available_broker_tiers

        current = get_broker_tier(s.infra, target_region)
        tiers = available_broker_tiers(target_region)

        if not tiers:
            console.print(f"[red]No broker offices available in {target_region}.[/red]")
            return

        if region is None and action == "open":
            # Show options
            console.print(views.office_options_view(target_region, current.value))
            return

        # Find the right tier to open/upgrade to
        if action == "open" and current == BrokerTier.NONE:
            spec = tiers[0]  # Local tier
        elif action == "upgrade" and current == BrokerTier.LOCAL:
            spec = next((t for t in tiers if t.tier == BrokerTier.ESTABLISHED), None)
            if not spec:
                console.print(f"[red]No upgrade available in {target_region}.[/red]")
                return
        elif action == "open" and current != BrokerTier.NONE:
            console.print(f"[yellow]Already have a broker in {target_region}. Use [bold]portlight office upgrade[/bold] to upgrade.[/yellow]")
            return
        else:
            console.print(f"[yellow]Broker in {target_region} is already at maximum tier.[/yellow]")
            return

        err = s.open_broker_cmd(target_region, spec)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        console.print(f"\n[bold green]{spec.name} opened![/bold green]")
        console.print(f"Board quality: +{int((spec.board_quality_bonus - 1) * 100)}% | Upkeep: {spec.upkeep_per_day}/day")
        return

    console.print(f"[red]Unknown office action: {action}[/red]. Use: open, upgrade")


# ---------------------------------------------------------------------------
# Licenses
# ---------------------------------------------------------------------------

@app.command()
def license(
    action: str = typer.Argument(None, help="buy or omit to view"),
    license_id: str = typer.Argument(None, help="License ID to purchase"),
) -> None:
    """View or purchase commercial licenses."""
    s = _session()

    if action is None:
        console.print(views.licenses_view(s.infra, s.captain.standing))
        return

    if action == "buy":
        if license_id is None:
            console.print("[red]Usage: portlight license buy <license_id>[/red]")
            console.print(views.licenses_view(s.infra, s.captain.standing))
            return
        from portlight.content.infrastructure import get_license_spec
        spec = get_license_spec(license_id)
        if not spec:
            # Try partial match
            from portlight.content.infrastructure import LICENSE_CATALOG
            matches = [s for s in LICENSE_CATALOG.values() if license_id in s.id]
            if len(matches) == 1:
                spec = matches[0]
            else:
                console.print(f"[red]Unknown license: {license_id}[/red]")
                return
        err = s.purchase_license_cmd(spec)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        console.print(f"\n[bold green]License purchased: {spec.name}![/bold green]")
        console.print(f"Upkeep: {spec.upkeep_per_day}/day | Silver: {s.captain.silver}")
        return

    console.print(f"[red]Unknown license action: {action}[/red]. Use: buy")


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

@app.command()
def insure(
    action: str = typer.Argument(None, help="buy or omit to view"),
    policy_id: str = typer.Argument(None, help="Policy ID to purchase"),
    contract: str = typer.Option(None, "--contract", "-c", help="Contract ID for guarantee policies"),
) -> None:
    """View or purchase insurance policies."""
    s = _session()

    region = s.current_port.region if s.current_port else "Mediterranean"
    heat = s.captain.standing.customs_heat.get(region, 0)

    if action is None:
        console.print(views.insurance_view(s.infra, heat))
        return

    if action == "buy":
        if policy_id is None:
            console.print("[red]Usage: portlight insure buy <policy_id>[/red]")
            console.print(views.insurance_view(s.infra, heat))
            return
        from portlight.content.infrastructure import get_policy_spec
        spec = get_policy_spec(policy_id)
        if not spec:
            from portlight.content.infrastructure import POLICY_CATALOG
            matches = [p for p in POLICY_CATALOG.values() if policy_id in p.id]
            if len(matches) == 1:
                spec = matches[0]
            else:
                console.print(f"[red]Unknown policy: {policy_id}[/red]")
                return

        # Determine scope targets
        target_id = contract or ""
        voyage_origin = ""
        voyage_destination = ""
        if s.at_sea and s.world.voyage:
            voyage_origin = s.world.voyage.origin_id
            voyage_destination = s.world.voyage.destination_id
        elif s.current_port:
            voyage_origin = s.current_port.id

        err = s.purchase_policy_cmd(
            spec, target_id=target_id,
            voyage_origin=voyage_origin, voyage_destination=voyage_destination,
        )
        if err:
            console.print(f"[red]{err}[/red]")
            return

        # Show heat-adjusted premium
        heat_surcharge = max(0, heat) * spec.heat_premium_mult
        adj_premium = int(spec.premium * (1.0 + heat_surcharge))
        console.print(f"\n[bold green]Policy purchased: {spec.name}![/bold green]")
        console.print(f"Premium: {adj_premium} silver | Coverage: {int(spec.coverage_pct * 100)}% up to {spec.coverage_cap} silver")
        console.print(f"Silver: {s.captain.silver}")
        return

    console.print(f"[red]Unknown insure action: {action}[/red]. Use: buy")


# ---------------------------------------------------------------------------
# Credit
# ---------------------------------------------------------------------------

@app.command()
def credit(
    action: str = typer.Argument(None, help="open, draw, repay, or omit to view"),
    amount: int = typer.Argument(None, help="Amount to draw or repay"),
) -> None:
    """Manage credit line: view, open, draw, or repay."""
    s = _session()

    if action is None:
        console.print(views.credit_view(s.infra, s.captain.standing))
        return

    if action == "open":
        from portlight.content.infrastructure import available_credit_tiers
        from portlight.engine.infrastructure import check_credit_eligibility
        # Find the best tier the player qualifies for
        tiers = available_credit_tiers()
        best = None
        for spec in reversed(tiers):  # try highest first
            err = check_credit_eligibility(s.infra, spec, s.captain.standing)
            if err is None:
                best = spec
                break
        if best is None:
            console.print("[red]No credit tier available. Build trust and standing first.[/red]")
            console.print(views.credit_view(s.infra, s.captain.standing))
            return
        err = s.open_credit_cmd(best)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        console.print(f"\n[bold green]Credit line opened: {best.name}![/bold green]")
        console.print(f"Limit: {best.credit_limit} | Rate: {int(best.interest_rate * 100)}% per {best.interest_period} days")
        return

    if action == "draw":
        if amount is None:
            console.print("[red]Usage: portlight credit draw <amount>[/red]")
            return
        err = s.draw_credit_cmd(amount)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        from portlight.engine.infrastructure import _ensure_credit
        cred = _ensure_credit(s.infra)
        from portlight.app.formatting import silver
        console.print(f"[green]Drew {silver(amount)} on credit. Outstanding: {silver(cred.outstanding)}[/green]")
        console.print(f"Silver: {silver(s.captain.silver)}")
        return

    if action == "repay":
        if amount is None:
            console.print("[red]Usage: portlight credit repay <amount>[/red]")
            return
        err = s.repay_credit_cmd(amount)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        from portlight.engine.infrastructure import _ensure_credit
        cred = _ensure_credit(s.infra)
        from portlight.app.formatting import silver
        remaining = cred.outstanding + cred.interest_accrued
        console.print(f"[green]Repaid {silver(amount)}. Remaining: {silver(remaining)}[/green]")
        console.print(f"Silver: {silver(s.captain.silver)}")
        return

    if action == "emergency":
        if amount is None:
            console.print("[yellow]Usage: portlight credit emergency <amount> (max 200)[/yellow]")
            return
        from portlight.engine.infrastructure import emergency_loan
        result = emergency_loan(s.captain, amount)
        if isinstance(result, str):
            console.print(f"[red]{result}[/red]")
            return
        interest = max(1, int(amount * 0.15))
        from portlight.app.formatting import silver
        console.print("\n[bold yellow]Emergency loan![/bold yellow]")
        console.print(f"  Received: [green]{silver(amount)}[/green]")
        console.print(f"  Owed: [red]{silver(amount + interest)}[/red] (15% interest, collected on next port arrival)")
        console.print(f"  Silver: {silver(s.captain.silver)}")
        s._save()
        return

    console.print(f"[red]Unknown credit action: {action}[/red]. Use: open, draw, repay, emergency")


# ---------------------------------------------------------------------------
# Milestones / Campaign
# ---------------------------------------------------------------------------

@app.command()
def milestones() -> None:
    """Show merchant career ledger: milestones, profile, and victory progress."""
    s = _session()
    snap = s._build_snapshot()
    console.print(views.milestones_view(s.campaign, snap))


# ---------------------------------------------------------------------------
# Guide - grouped command reference
# ---------------------------------------------------------------------------

@app.command()
def guide() -> None:
    """Show grouped command reference for all game actions."""
    from rich.panel import Panel
    lines: list[str] = []

    lines.append("[bold]Trading[/bold]")
    lines.append("  market          — view prices, stock, and what you can afford")
    lines.append("  buy <good> <n>  — buy goods from port market")
    lines.append("  sell <good> <n> — sell goods to port market")
    lines.append("  cargo           — view cargo hold contents")
    lines.append("")

    lines.append("[bold]Navigation[/bold]")
    lines.append("  routes          — list available routes from current port")
    lines.append("  sail <dest>     — depart for a destination port")
    lines.append("  advance [days]  — advance time (sail or wait)")
    lines.append("  port            — view current port info")
    lines.append("  provision [n]   — buy provisions")
    lines.append("  repair [n]      — repair hull")
    lines.append("  hire [n] [--role <role>]  — hire crew (default: sailor)")
    lines.append("  fire [n] [--role <role>]  — fire crew (default: sailor)")
    lines.append("  duel <stances>  — fight a pirate captain (e.g. thrust,parry,slash)")
    lines.append("")

    lines.append("[bold]Contracts[/bold]")
    lines.append("  contracts       — view contract board offers")
    lines.append("  accept <id>     — accept a contract offer")
    lines.append("  obligations     — view active contract obligations")
    lines.append("  abandon <id>    — abandon a contract (reputation cost)")
    lines.append("")

    lines.append("[bold]Infrastructure[/bold]")
    lines.append("  warehouse [action] — manage warehouses (lease, deposit, withdraw)")
    lines.append("  office [action]    — manage broker offices (open, upgrade)")
    lines.append("  license [buy <id>] — view or purchase licenses")
    lines.append("")

    lines.append("[bold]Finance[/bold]")
    lines.append("  insure [buy <id>]  — view or purchase insurance")
    lines.append("  credit [action]    — manage credit (open, draw, repay)")
    lines.append("")

    lines.append("[bold]Combat Gear[/bold]")
    lines.append("  inventory           — view all personal gear and status")
    lines.append("  equip <slot> <id>   — equip armor or weapon")
    lines.append("  equip remove <slot> — unequip armor or weapon")
    lines.append("  merchant [id] [item] — list merchants, browse one, or buy an item")
    lines.append("  armory [buy] [qty]  — quick-buy weapons/ammo (no markup)")
    lines.append("  train [style]       — learn a fighting style")
    lines.append("  equip-style [id]    — equip or unequip a style")
    lines.append("  injuries            — view current wounds")
    lines.append("  upgrade [id] [--remove] — browse, install, or remove ship upgrades")
    lines.append("")

    lines.append("[bold]Career[/bold]")
    lines.append("  captain         — view captain identity and advantages")
    lines.append("  reputation      — view standing, heat, and trust")
    lines.append("  milestones      — view career milestones and victory progress")
    lines.append("  status          — view captain overview")
    lines.append("  ledger          — view trade receipt history")
    lines.append("  shipyard [buy]  — view or buy ships")
    lines.append("")

    lines.append("[bold]System[/bold]")
    lines.append("  save            — explicitly save the game")
    lines.append("  load            — load a saved game")
    lines.append("  guide           — show this reference")

    console.print(Panel("\n".join(lines), title="[bold]Portlight Command Guide[/bold]", border_style="blue"))


# ---------------------------------------------------------------------------
# Save / Load (explicit)
# ---------------------------------------------------------------------------

@app.command()
def save() -> None:
    """Explicitly save the game."""
    s = _session()
    s._save()
    console.print("[green]Game saved.[/green]")


@app.command()
def load() -> None:
    """Load a saved game."""
    s = GameSession(slot=_active_slot)
    if s.load():
        console.print("[green]Game loaded.[/green]")
        console.print(views.status_view(s.world, s.ledger, s.infra))
    else:
        console.print("[red]No saved game found.[/red]")


# ---------------------------------------------------------------------------
# Combat system commands (Phase 5+)
# ---------------------------------------------------------------------------

# Active encounter + combatant state held in module-level for interactive turns
_active_encounter = None
_player_combatant = None
_opponent_combatant = None
_pending_victory = False  # True when player won and must choose spare/take-all


def _sync_encounter_phase(s) -> None:
    """Persist the current encounter phase and combat state to save data."""
    if _active_encounter and s and s.world:
        enc = _active_encounter
        s.world.pirates.encounter_phase = enc.phase
        estate = {
            "boarding_progress": enc.boarding_progress,
            "boarding_threshold": enc.boarding_threshold,
            "naval_turns": enc.naval_turns,
            "duel_turns": enc.duel_turns,
            "enemy_ship_hull": enc.enemy_ship_hull,
            "enemy_ship_crew": enc.enemy_ship_crew,
        }
        # Persist combatant HP/stamina for duel phase
        if _player_combatant:
            estate["player_hp"] = _player_combatant.hp
            estate["player_stamina"] = _player_combatant.stamina
        if _opponent_combatant:
            estate["opponent_hp"] = _opponent_combatant.hp
            estate["opponent_stamina"] = _opponent_combatant.stamina
        estate["pending_victory"] = _pending_victory
        s.world.pirates.encounter_state = estate
    elif s and s.world:
        s.world.pirates.encounter_phase = ""
        s.world.pirates.encounter_state = {}


def _clear_encounter(s) -> None:
    """Clear active encounter and pending_duel from save."""
    global _active_encounter, _player_combatant, _opponent_combatant, _pending_victory
    _active_encounter = None
    _player_combatant = None
    _opponent_combatant = None
    _pending_victory = False
    if s and s.world:
        s.world.pirates.pending_duel = None
        s.world.pirates.encounter_phase = ""
        s.world.pirates.encounter_state = {}


def _restore_encounter(s) -> None:
    """Restore encounter from pending_duel if module state was lost (new process)."""
    global _active_encounter
    if _active_encounter is not None:
        return  # already have one
    pd = s.world.pirates.pending_duel
    if pd is None:
        return
    from portlight.engine.encounter import create_encounter
    enc = create_encounter(
        s.world.ports,
        s.world.voyage.destination_id if s.world.voyage else "porto_novo",
        s._rng,
    )
    if enc:
        enc.enemy_captain_id = pd.captain_id
        enc.enemy_captain_name = pd.captain_name
        enc.enemy_faction_id = pd.faction_id
        enc.enemy_personality = pd.personality
        enc.enemy_strength = pd.strength
        enc.enemy_region = pd.region
        # Restore persisted phase and combat state
        phase = s.world.pirates.encounter_phase
        if phase and phase in ("approach", "naval", "boarding", "duel"):
            enc.phase = phase
        estate = s.world.pirates.encounter_state
        if estate:
            enc.boarding_progress = estate.get("boarding_progress", 0)
            enc.boarding_threshold = estate.get("boarding_threshold", 3)
            enc.naval_turns = estate.get("naval_turns", 0)
            enc.duel_turns = estate.get("duel_turns", 0)
            enc.enemy_ship_hull = estate.get("enemy_ship_hull", enc.enemy_ship_hull)
            enc.enemy_ship_crew = estate.get("enemy_ship_crew", enc.enemy_ship_crew)
        # Restore pending victory flag
        global _pending_victory
        if estate and estate.get("pending_victory"):
            _pending_victory = True
            enc.phase = "resolved"  # victory means encounter is resolved, awaiting spare/take-all
        _active_encounter = enc


@app.command()
def encounter(
    choice: str = typer.Argument(..., help="negotiate, flee, or fight"),
) -> None:
    """Respond to a pirate encounter: negotiate, flee, or fight."""
    global _active_encounter
    from portlight.app import combat_views
    from portlight.engine.encounter import (
        begin_fight,
        resolve_flee,
        resolve_negotiate,
    )

    s = _session()
    _restore_encounter(s)
    if _active_encounter is None or _active_encounter.phase != "approach":
        console.print("[yellow]No active encounter. Encounters happen during pirate events at sea.[/yellow]")
        return

    enc = _active_encounter
    choice = choice.lower().strip()

    # Resolve ship stats (upgrades applied) for combat calculations
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolved_ship
    combat_ship = resolved_ship(s.captain.ship, UPGRADES)

    if choice == "negotiate":
        success, msg = resolve_negotiate(
            enc, s.captain.standing.underworld_standing,
            s.captain.captain_type, s._rng,
        )
        console.print(f"\n{msg}")
        if not success:
            msg2 = begin_fight(enc, combat_ship)
            console.print(f"\n{msg2}")
            console.print(combat_views.naval_status_view(
                s.captain.ship.hull, s.captain.ship.hull_max,
                s.captain.ship.crew, s.captain.ship.cannons,
                enc.enemy_ship_hull, enc.enemy_ship_hull_max,
                enc.enemy_ship_crew, enc.enemy_ship_cannons,
                enc.boarding_progress, enc.boarding_threshold, 0,
            ))
        else:
            _clear_encounter(s)
        _sync_encounter_phase(s)
        s._save()

    elif choice == "flee":
        escaped, dmg, msg = resolve_flee(enc, combat_ship, s._rng)
        console.print(f"\n{msg}")
        if dmg > 0:
            s.captain.ship.hull = max(0, s.captain.ship.hull - dmg)
        if escaped:
            _clear_encounter(s)
        else:
            msg2 = begin_fight(enc, combat_ship)
            console.print(f"\n{msg2}")
        _sync_encounter_phase(s)
        s._save()

    elif choice == "fight":
        msg = begin_fight(enc, combat_ship)
        console.print(f"\n{msg}")
        _sync_encounter_phase(s)
        console.print(combat_views.naval_status_view(
            s.captain.ship.hull, s.captain.ship.hull_max,
            s.captain.ship.crew, s.captain.ship.cannons,
            enc.enemy_ship_hull, enc.enemy_ship_hull_max,
            enc.enemy_ship_crew, enc.enemy_ship_cannons,
            enc.boarding_progress, enc.boarding_threshold, 0,
        ))
        s._save()

    else:
        console.print("[red]Choose: negotiate, flee, or fight[/red]")


@app.command()
def naval(
    action: str = typer.Argument(..., help="broadside, close, evade, or rake"),
) -> None:
    """Execute a naval combat action."""
    global _active_encounter
    from portlight.app import combat_views
    from portlight.engine.encounter import (
        get_encounter_naval_actions,
        resolve_boarding_phase,
        resolve_naval_turn,
    )

    s = _session()
    _restore_encounter(s)
    if _active_encounter is None or _active_encounter.phase != "naval":
        console.print("[yellow]Not in naval combat.[/yellow]")
        return

    enc = _active_encounter

    # Resolve ship stats (upgrades applied) for combat calculations
    from portlight.content.upgrades import UPGRADES
    from portlight.engine.ship_stats import resolved_ship, resolve_cannons
    effective_cannons = resolve_cannons(s.captain.ship, UPGRADES)
    valid = get_encounter_naval_actions(effective_cannons)
    action = action.lower().strip()
    if action not in valid:
        console.print(f"[red]Invalid action. Available: {', '.join(valid)}[/red]")
        return

    # Handle flee attempt during naval combat
    if action == "flee":
        from portlight.engine.naval import attempt_flee
        from portlight.engine.models import EnemyShip
        import random
        flee_rng = random.Random(s.world.seed + s.world.day * 1000 + enc.naval_turns + 8888)
        combat_ship = resolved_ship(s.captain.ship, UPGRADES)
        enemy_ship = EnemyShip(
            name=f"{enc.enemy_captain_name}'s Ship",
            hull=enc.enemy_ship_hull, hull_max=enc.enemy_ship_hull_max,
            cannons=enc.enemy_ship_cannons, maneuver=enc.enemy_ship_maneuver,
            speed=enc.enemy_ship_speed, crew=enc.enemy_ship_crew,
            crew_max=enc.enemy_ship_crew_max,
        )
        escaped, damage = attempt_flee(combat_ship, enemy_ship, flee_rng)
        s.captain.ship.hull = max(0, s.captain.ship.hull - damage)
        enc.naval_turns += 1  # Flee counts as a turn
        if escaped:
            msg = "You break away!"
            if damage > 0:
                msg += f" A parting shot catches your hull for {damage} damage."
            console.print(f"\n[bold green]{msg}[/bold green]")
            _clear_encounter(s)
        else:
            console.print(f"\n[bold red]Flee failed! Their broadside rakes you for {damage} hull damage.[/bold red]")
            if s.captain.ship.hull <= 0:
                console.print("\n[bold red]Your ship is sinking![/bold red]")
                s.world.pirates.naval_defeats += 1
                _clear_encounter(s)
            elif s.captain.ship.crew <= 0:
                console.print("\n[bold red]No crew left to sail! Your ship drifts helplessly.[/bold red]")
                s.world.pirates.naval_defeats += 1
                _clear_encounter(s)
            else:
                # Show naval status so player sees the damage in context
                console.print(combat_views.naval_status_view(
                    s.captain.ship.hull, s.captain.ship.hull_max,
                    s.captain.ship.crew, s.captain.ship.cannons,
                    enc.enemy_ship_hull, enc.enemy_ship_hull_max,
                    enc.enemy_ship_crew, enc.enemy_ship_cannons,
                    enc.boarding_progress, enc.boarding_threshold, enc.naval_turns,
                ))
        _sync_encounter_phase(s)
        s._save()
        return

    combat_ship = resolved_ship(s.captain.ship, UPGRADES)
    # Unique RNG per turn to avoid replay on process restart
    import random
    naval_rng = random.Random(s.world.seed + s.world.day * 1000 + enc.naval_turns + 7777)
    result = resolve_naval_turn(enc, action, combat_ship, naval_rng)

    # Apply hull/crew damage to player ship
    s.captain.ship.hull = max(0, s.captain.ship.hull + result["player_hull_delta"])
    s.captain.ship.crew = max(0, s.captain.ship.crew + result["player_crew_delta"])

    console.print(combat_views.naval_round_view(result))

    if result["enemy_sunk"]:
        console.print("\n[bold green]Enemy ship sinks beneath the waves![/bold green]")
        s.world.pirates.naval_victories += 1
        # Check if capture is possible
        from portlight.engine.encounter import can_capture_prize
        from portlight.engine.models import max_fleet_size
        trust = s.captain.standing.commercial_trust
        can_cap, reason = can_capture_prize(s.captain, enc, max_fleet_size(trust))
        if can_cap:
            enc.phase = "capture_available"
            console.print("\n[bold yellow]You can capture this ship as a prize![/bold yellow]")
            console.print(f"  Enemy ship: {enc.enemy_captain_name}'s vessel")
            console.print("  Use: [cyan]portlight capture <crew_to_assign>[/cyan]")
        else:
            console.print(f"\n[dim]Cannot capture: {reason}[/dim]")
            _clear_encounter(s)
    elif result["boarding_triggered"]:
        console.print("\n[bold yellow]Boarding action![/bold yellow]")
        boarding = resolve_boarding_phase(enc, s.captain.ship.crew, s._rng)
        s.captain.ship.crew = max(0, s.captain.ship.crew - boarding["player_crew_lost"])
        console.print(f"\n{boarding['flavor']}")
        console.print("\n[bold]Personal combat begins! Use [cyan]portlight fight <action>[/cyan][/bold]")
    elif s.captain.ship.hull <= 0:
        console.print("\n[bold red]Your ship is sinking![/bold red]")
        s.world.pirates.naval_defeats += 1
        _clear_encounter(s)
    elif s.captain.ship.crew <= 0:
        console.print("\n[bold red]No crew left to sail! Your ship drifts helplessly.[/bold red]")
        console.print("[dim]The pirates board unopposed and take what they want.[/dim]")
        # Lose some cargo and silver as penalty
        cargo_loss = sum(c.quantity for c in s.captain.ship.cargo) // 2
        silver_loss = s.captain.silver // 4
        if cargo_loss > 0:
            # Remove half of each cargo type
            for item in s.captain.ship.cargo:
                item.quantity = max(0, item.quantity - item.quantity // 2)
            s.captain.ship.cargo = [c for c in s.captain.ship.cargo if c.quantity > 0]
            console.print("[red]Pirates take half your cargo.[/red]")
        if silver_loss > 0:
            s.captain.silver -= silver_loss
            console.print(f"[red]Pirates take {silver_loss} silver.[/red]")
        s.world.pirates.naval_defeats += 1
        _clear_encounter(s)
    else:
        console.print(combat_views.naval_status_view(
            s.captain.ship.hull, s.captain.ship.hull_max,
            s.captain.ship.crew, s.captain.ship.cannons,
            enc.enemy_ship_hull, enc.enemy_ship_hull_max,
            enc.enemy_ship_crew, enc.enemy_ship_cannons,
            enc.boarding_progress, enc.boarding_threshold, enc.naval_turns,
        ))

    _sync_encounter_phase(s)
    s._save()


@app.command()
def capture(
    crew_to_assign: int = typer.Argument(..., help="Number of crew to assign to prize ship"),
) -> None:
    """Capture a defeated enemy ship as a prize."""
    global _active_encounter
    s = _session()
    if _active_encounter is None or _active_encounter.phase != "capture_available":
        console.print("[yellow]No ship available to capture.[/yellow]")
        return

    enc = _active_encounter
    from portlight.engine.encounter import can_capture_prize, capture_prize, prize_template_id
    from portlight.engine.models import max_fleet_size
    from portlight.content.ships import SHIPS

    trust = s.captain.standing.commercial_trust
    can_cap, reason = can_capture_prize(s.captain, enc, max_fleet_size(trust))
    if not can_cap:
        console.print(f"[red]Cannot capture: {reason}[/red]")
        return

    # Validate crew assignment
    prize_tid = prize_template_id(enc.enemy_strength)
    prize_tmpl = SHIPS.get(prize_tid)
    prize_min = prize_tmpl.crew_min if prize_tmpl else 3
    current_tmpl = SHIPS.get(s.captain.ship.template_id)
    current_min = current_tmpl.crew_min if current_tmpl else 3

    if crew_to_assign < prize_min:
        console.print(f"[red]Need at least {prize_min} crew for the prize ship.[/red]")
        return
    if s.captain.ship.crew - crew_to_assign < current_min:
        console.print(f"[red]Would leave your flagship with {s.captain.ship.crew - crew_to_assign} crew (need {current_min}).[/red]")
        return

    # Capture the prize
    owned = capture_prize(s.captain, enc, crew_to_assign)
    # Set docked port to current voyage destination (or origin if not sailing)
    if s.world.voyage:
        owned.docked_port_id = s.world.voyage.destination_id
    else:
        owned.docked_port_id = s.current_port_id or "porto_novo"
    s.captain.fleet.append(owned)
    _clear_encounter(s)

    console.print(f"\n[bold green]Prize captured![/bold green] {owned.ship.name} added to your fleet.")
    console.print(f"  Crew split: {s.captain.ship.crew} on flagship, {crew_to_assign} on prize")
    console.print(views.fleet_view(s.captain))
    s._save()


@app.command()
def fight(
    action: str = typer.Argument(..., help="thrust, slash, parry, shoot, throw, dodge, or style action"),
) -> None:
    """Execute a personal combat action."""
    global _active_encounter, _player_combatant, _opponent_combatant, _pending_victory
    from portlight.app import combat_views
    from portlight.engine.encounter import (
        create_duel_combatants,
        get_encounter_combat_actions,
        resolve_duel_turn,
    )
    from portlight.engine.injuries import create_injury

    s = _session()
    _restore_encounter(s)
    enc = _active_encounter
    if enc is None or enc.phase != "duel":
        console.print("[yellow]Not in personal combat.[/yellow]")
        return

    # Initialize combatants on first fight turn
    if _player_combatant is None or _opponent_combatant is None:
        gear = s.captain.combat_gear
        total_throwing = sum(gear.throwing_weapons.values()) if gear.throwing_weapons else 0
        # Build throwing weapon ID list from gear dict
        tw_ids = []
        for wid, count in gear.throwing_weapons.items():
            tw_ids.extend([wid] * count)
        # Get weapon quality
        melee_q = gear.weapon_quality.get(gear.melee_weapon, "standard") if gear.melee_weapon else "standard"
        ranged_q = gear.weapon_quality.get(gear.firearm, "standard") if gear.firearm else "standard"
        _player_combatant, _opponent_combatant = create_duel_combatants(
            enc,
            player_crew=s.captain.ship.crew if s.captain.ship else 5,
            player_style=s.captain.active_style,
            player_injury_ids=[inj.injury_id for inj in s.captain.injuries],
            player_firearm=gear.firearm,
            player_ammo=gear.firearm_ammo,
            player_throwing=total_throwing,
            player_mechanical=gear.mechanical_weapon,
            player_mechanical_ammo=gear.mechanical_ammo,
        )
        # Set fields that create_duel_combatants doesn't handle
        _player_combatant.throwing_weapon_ids = tw_ids
        _player_combatant.melee_weapon_id = gear.melee_weapon
        _player_combatant.melee_quality = melee_q
        _player_combatant.ranged_quality = ranged_q
        if gear.armor:
            from portlight.content.armor import ARMOR
            armor_def = ARMOR.get(gear.armor)
            if armor_def:
                _player_combatant.armor_dr = armor_def.damage_reduction
                _player_combatant.dodge_stamina_penalty = armor_def.dodge_penalty

        # Restore HP/stamina from persisted state (cross-process resume)
        estate = s.world.pirates.encounter_state
        if estate:
            if "player_hp" in estate:
                _player_combatant.hp = estate["player_hp"]
            if "player_stamina" in estate:
                _player_combatant.stamina = estate["player_stamina"]
            if "opponent_hp" in estate:
                _opponent_combatant.hp = estate["opponent_hp"]
            if "opponent_stamina" in estate:
                _opponent_combatant.stamina = estate["opponent_stamina"]

    p, o = _player_combatant, _opponent_combatant
    valid = get_encounter_combat_actions(p)
    action = action.lower().strip()
    if action not in valid:
        console.print(f"[red]Invalid action. Available: {', '.join(valid)}[/red]")
        return

    # Advance RNG past already-played turns to avoid deterministic replay
    combat_rng = random.Random(s.world.seed + s.world.day * 1000 + enc.duel_turns + enc.naval_turns)
    result = resolve_duel_turn(enc, action, p, o, combat_rng)

    console.print(combat_views.combat_round_view({
        "turn": result.turn,
        "player_action": result.player_action,
        "opponent_action": result.opponent_action,
        "damage_to_opponent": result.damage_to_opponent,
        "damage_to_player": result.damage_to_player,
        "player_stamina_delta": result.player_stamina_delta,
        "injury_inflicted": result.injury_inflicted,
        "opponent_injury": result.opponent_injury,
        "flavor": result.flavor,
        "style_effect": result.style_effect,
    }))

    # Show status
    console.print(combat_views.combat_status_view(
        p.hp, p.hp_max, p.stamina, p.stamina_max,
        o.hp, o.hp_max, enc.enemy_captain_name,
        p.ammo, p.throwing_weapons, s.captain.active_style,
        [inj.injury_id for inj in s.captain.injuries] + (
            [result.injury_inflicted] if result.injury_inflicted else []
        ),
        get_encounter_combat_actions(p), result.turn,
    ))

    # Check fight over
    if enc.phase == "resolved":
        player_won = o.hp <= 0 and p.hp > 0
        draw = p.hp <= 0 and o.hp <= 0

        # Apply injuries regardless of outcome
        if result.injury_inflicted:
            new_injury = create_injury(result.injury_inflicted, s.world.day)
            s.captain.injuries.append(new_injury)
            from portlight.content.injuries import INJURIES
            inj_def = INJURIES.get(result.injury_inflicted)
            if inj_def:
                console.print(f"\n[bold red]Injury: {inj_def.name} — {inj_def.description}[/bold red]")

        # Tick weapon degradation
        from portlight.engine.skill_engine import get_degrade_threshold_bonus, get_skill_level
        from portlight.engine.weapon_quality import tick_weapon_degradation
        gear = s.captain.combat_gear
        bs_bonus = get_degrade_threshold_bonus(get_skill_level(s.captain.skills, "blacksmith"))
        if gear.melee_weapon:
            degraded, new_q = tick_weapon_degradation(gear.weapon_quality, gear.weapon_usage, gear.melee_weapon, "melee", threshold_bonus=bs_bonus)
            if degraded:
                console.print(f"[yellow]Your {gear.melee_weapon.replace('_', ' ').title()} has degraded to {new_q} quality![/yellow]")
        if gear.armor:
            degraded, new_q = tick_weapon_degradation(gear.weapon_quality, gear.weapon_usage, gear.armor, "armor", threshold_bonus=bs_bonus)
            if degraded:
                console.print(f"[yellow]Your {gear.armor.replace('_', ' ').title()} has degraded to {new_q} quality![/yellow]")

        # Sync ammo back to captain
        gear.firearm_ammo = p.ammo
        gear.mechanical_ammo = p.mechanical_ammo
        if gear.throwing_weapons:
            total_before = sum(gear.throwing_weapons.values())
            spent = total_before - p.throwing_weapons
            for wid in list(gear.throwing_weapons):
                if spent <= 0:
                    break
                can_take = min(spent, gear.throwing_weapons[wid])
                gear.throwing_weapons[wid] -= can_take
                spent -= can_take
            # Remove fully spent throwing weapons
            gear.throwing_weapons = {k: v for k, v in gear.throwing_weapons.items() if v > 0}

        if player_won:
            # VICTORY — pause for spare/take-all choice
            _pending_victory = True
            console.print(f"\n[bold green]Victory over {enc.enemy_captain_name}![/bold green]")
            console.print(f"\n{enc.enemy_captain_name} lies defeated at your feet.")
            console.print("\n[bold]Choose:[/bold]")
            console.print("  [cyan]portlight spare[/cyan]     — Show mercy. (+25 respect, -10 grudge, +5 underworld standing)")
            console.print("  [cyan]portlight take-all[/cyan]  — Take everything. (+5 fear, +10 grudge, more silver)")
            _sync_encounter_phase(s)
            s._save()
            return  # DON'T clear encounter yet — spare/take-all commands will finalize

        elif draw:
            s.world.pirates.duels_won += 1
            console.print("\n[bold yellow]Draw! Mutual respect earned.[/bold yellow]")
            # Record encounter
            from portlight.engine.captain_memory import get_or_create_memory, record_encounter
            memory = get_or_create_memory(s.world.pirates.captain_memories, enc.enemy_captain_id)
            record_encounter(memory, s.world.day, enc.enemy_region, "player_won",
                             crew_killed=max(0, enc.enemy_ship_crew_max - enc.enemy_ship_crew))
        else:
            silver_loss = 15 + enc.enemy_strength * 3
            s.captain.silver = max(0, s.captain.silver - silver_loss)
            s.world.pirates.duels_lost += 1
            console.print(f"\n[bold red]Defeated. -{silver_loss} silver.[/bold red]")
            # Record encounter
            from portlight.engine.captain_memory import get_or_create_memory, record_encounter
            memory = get_or_create_memory(s.world.pirates.captain_memories, enc.enemy_captain_id)
            record_encounter(memory, s.world.day, enc.enemy_region, "player_lost",
                             crew_killed=max(0, enc.enemy_ship_crew_max - enc.enemy_ship_crew))

        _clear_encounter(s)

    _sync_encounter_phase(s)
    s._save()


@app.command()
def train(
    style_id: str = typer.Argument(None, help="Style to learn (e.g. la_destreza, dambe)"),
) -> None:
    """Learn a fighting style from a regional master."""
    from portlight.app import combat_views
    from portlight.content.injuries import get_injured_body_parts
    from portlight.engine.training import can_learn_style, get_masters_at_port, learn_style

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked at a port to train.[/yellow]")
        return

    masters = get_masters_at_port(port.id)
    if not masters and style_id is None:
        console.print("[dim]No fighting masters at this port.[/dim]")
        return

    if style_id is None:
        from portlight.content.fighting_styles import FIGHTING_STYLES
        master_dicts = []
        for m in masters:
            style = FIGHTING_STYLES.get(m.style_id)
            master_dicts.append({
                "name": m.name,
                "style": style.name if style else m.style_id,
                "style_id": m.style_id,
                "region": style.region if style else "",
                "cost": style.silver_cost if style else 0,
                "days": style.training_days if style else 0,
                "prereqs": style.prerequisite_styles if style else 0,
                "dialog": m.dialog,
                "description": m.description,
            })
        console.print(combat_views.training_view(
            port.name, master_dicts, s.captain.learned_styles, s.captain.silver,
        ))
        return

    injured_parts = get_injured_body_parts([inj.injury_id for inj in s.captain.injuries])
    error = can_learn_style(
        s.captain.learned_styles, injured_parts,
        s.captain.silver, port.id, style_id,
    )
    if error:
        console.print(f"[red]{error}[/red]")
        return

    from portlight.content.fighting_styles import FIGHTING_STYLES
    style = FIGHTING_STYLES[style_id]
    s.captain.learned_styles, s.captain.silver = learn_style(
        s.captain.learned_styles, s.captain.silver, style_id,
    )
    # Training days advance the clock
    for _ in range(style.training_days):
        s.advance()
    console.print(f"\n[bold green]Learned {style.name}![/bold green] ({style.training_days} days, {style.silver_cost} silver)")
    s._save()


@app.command(name="equip-style")
def equip_style(
    style_id: str = typer.Argument(None, help="Style to equip (or omit to unequip)"),
) -> None:
    """Equip or unequip a fighting style."""
    s = _session()
    if style_id is None:
        s.captain.active_style = None
        console.print("[dim]Fighting style unequipped.[/dim]")
        s._save()
        return

    if style_id not in s.captain.learned_styles:
        console.print(f"[red]You haven't learned {style_id}. Use [bold]portlight train[/bold] at the right port.[/red]")
        return

    from portlight.content.injuries import get_injured_body_parts
    from portlight.engine.training import check_style_usable
    injured_parts = get_injured_body_parts([inj.injury_id for inj in s.captain.injuries])
    if not check_style_usable(style_id, injured_parts):
        console.print("[red]Your injuries prevent using this style.[/red]")
        return

    s.captain.active_style = style_id
    from portlight.content.fighting_styles import FIGHTING_STYLES
    style = FIGHTING_STYLES[style_id]
    console.print(f"[bold green]Equipped: {style.name}[/bold green]")
    s._save()


@app.command()
def armory(
    buy: str = typer.Argument(None, help="Weapon or ammo ID to buy"),
    qty: int = typer.Argument(1, help="Quantity to buy"),
) -> None:
    """View or buy ranged weapons and ammunition."""
    from portlight.app import combat_views
    from portlight.content.ranged_weapons import AMMO, RANGED_WEAPONS, get_ammo_for_region, get_weapons_for_region

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked to visit the armory.[/yellow]")
        return

    if buy is None:
        weapons = get_weapons_for_region(port.region)
        _ammo = get_ammo_for_region(port.region)
        console.print(combat_views.armory_view(
            [{"id": w.id, "name": w.name, "type": w.weapon_type, "damage": f"{w.damage_min}-{w.damage_max}",
              "accuracy": f"{w.accuracy:.0%}", "cost": w.silver_cost, "reload": w.reload_turns}
             for w in weapons],
            {"melee": s.captain.combat_gear.melee_weapon or "fists",
             "ranged": s.captain.combat_gear.firearm or s.captain.combat_gear.mechanical_weapon or "none",
             "ammo": s.captain.combat_gear.firearm_ammo + s.captain.combat_gear.mechanical_ammo,
             "throwing": s.captain.combat_gear.throwing_weapons},
        ))
        return

    gear = s.captain.combat_gear

    # Try weapon purchase
    if buy in RANGED_WEAPONS:
        weapon = RANGED_WEAPONS[buy]
        if port.region not in weapon.available_regions:
            console.print(f"[red]{weapon.name} not available in {port.region}.[/red]")
            return
        cost = weapon.silver_cost * qty
        if s.captain.silver < cost:
            console.print(f"[red]Need {cost} silver.[/red]")
            return
        s.captain.silver -= cost
        if weapon.weapon_type == "firearm":
            gear.firearm = buy
            console.print(f"[green]Bought {weapon.name}![/green]")
        elif weapon.weapon_type == "mechanical":
            gear.mechanical_weapon = buy
            console.print(f"[green]Bought {weapon.name}![/green]")
        elif weapon.weapon_type == "thrown":
            current = gear.throwing_weapons.get(buy, 0)
            gear.throwing_weapons[buy] = current + qty * weapon.ammo_per_purchase
            console.print(f"[green]Bought {qty * weapon.ammo_per_purchase}x {weapon.name}![/green]")
        s._save()
        return

    # Try ammo purchase
    if buy in AMMO:
        ammo_def = AMMO[buy]
        if port.region not in ammo_def.available_regions:
            console.print(f"[red]{ammo_def.name} not available in {port.region}.[/red]")
            return
        cost = ammo_def.silver_cost * qty
        if s.captain.silver < cost:
            console.print(f"[red]Need {cost} silver.[/red]")
            return
        s.captain.silver -= cost
        if ammo_def.weapon_type == "firearm":
            gear.firearm_ammo += qty * ammo_def.quantity
        elif ammo_def.weapon_type == "mechanical":
            gear.mechanical_ammo += qty * ammo_def.quantity
        console.print(f"[green]Bought {qty * ammo_def.quantity}x {ammo_def.name}![/green]")
        s._save()
        return

    console.print(f"[red]Unknown item: {buy}[/red]")


@app.command()
def injuries() -> None:
    """Show current injuries and healing status."""
    from portlight.app import combat_views
    from portlight.content.injuries import INJURIES

    s = _session()
    if not s.captain.injuries:
        console.print("[dim]No injuries. You're in fighting shape.[/dim]")
        return

    injury_data = []
    for inj in s.captain.injuries:
        defn = INJURIES.get(inj.injury_id)
        if defn:
            injury_data.append({
                "name": defn.name,
                "severity": defn.severity,
                "body_part": defn.body_part,
                "description": defn.description,
                "heal_remaining": inj.heal_remaining,
                "treated": inj.treated,
            })
    console.print(combat_views.injuries_view(injury_data))


# ---------------------------------------------------------------------------
# Weapon quality commands
# ---------------------------------------------------------------------------

@app.command()
def maintain(
    weapon: str = typer.Argument(None, help="Weapon ID to maintain (e.g. cutlass, matchlock_pistol)"),
) -> None:
    """Maintain a weapon to prevent quality degradation."""
    from portlight.engine.weapon_quality import (
        get_maintenance_cost,
        get_weapon_summary,
    )

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked to maintain weapons.[/yellow]")
        return

    gear = s.captain.combat_gear

    if weapon is None:
        # Show all weapons and their quality/usage
        weapons_to_show = []
        if gear.melee_weapon:
            weapons_to_show.append((gear.melee_weapon, "melee"))
        if gear.firearm:
            weapons_to_show.append((gear.firearm, "firearm"))
        if gear.mechanical_weapon:
            weapons_to_show.append((gear.mechanical_weapon, "mechanical"))
        if gear.armor:
            weapons_to_show.append((gear.armor, "armor"))

        if not weapons_to_show:
            console.print("[dim]No weapons to maintain.[/dim]")
            return

        from rich.table import Table
        table = Table(title="Weapon Condition")
        table.add_column("Weapon")
        table.add_column("Quality")
        table.add_column("Usage")
        table.add_column("Maint. Cost")
        for wid, wtype in weapons_to_show:
            summary = get_weapon_summary(wid, wid.replace("_", " ").title(), gear.weapon_quality, gear.weapon_usage, wtype)
            warn = " [red]!!![/red]" if summary["near_degradation"] else ""
            cost = get_maintenance_cost(wid, gear.weapon_quality)
            table.add_row(
                summary["name"],
                f"[{summary['quality_color']}]{summary['quality_label']}[/{summary['quality_color']}]",
                f"{summary['usage']}/{summary['uses_until_degrade'] + summary['usage']}{warn}",
                f"{cost} silver",
            )
        console.print(table)
        return

    # Apply blacksmith discount
    from portlight.engine.skill_engine import apply_maintenance_discount, get_skill_level
    bs_level = get_skill_level(s.captain.skills, "blacksmith")
    base_cost = get_maintenance_cost(weapon, gear.weapon_quality)
    discounted_cost = apply_maintenance_discount(base_cost, bs_level)

    if s.captain.silver < discounted_cost:
        console.print(f"[red]Maintenance costs {discounted_cost} silver. You have {s.captain.silver}.[/red]")
        return

    gear.weapon_usage[weapon] = 0
    s.captain.silver -= discounted_cost
    discount_note = " (blacksmith discount!)" if discounted_cost < base_cost else ""
    console.print(f"[green]{weapon.replace('_', ' ').title()} maintained — usage reset, quality preserved.{discount_note}[/green]")
    s._save()


@app.command()
def smith(
    weapon: str = typer.Argument(..., help="Weapon ID to upgrade (e.g. cutlass, rapier)"),
) -> None:
    """Upgrade a weapon's quality at a smith (requires shipyard port)."""
    from portlight.engine.models import PortFeature
    from portlight.engine.weapon_quality import can_upgrade, get_quality_effects, upgrade_weapon

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked to visit a smith.[/yellow]")
        return

    has_shipyard = PortFeature.SHIPYARD in port.features
    gear = s.captain.combat_gear

    error = can_upgrade(weapon, gear.weapon_quality, s.captain.silver, at_smith=has_shipyard)
    if error:
        console.print(f"[red]{error}[/red]")
        return

    new_quality, remaining_silver, days = upgrade_weapon(weapon, gear.weapon_quality, gear.weapon_usage, s.captain.silver)
    s.captain.silver = remaining_silver
    # Training days advance the clock
    for _ in range(days):
        s.advance()

    effects = get_quality_effects(new_quality)
    console.print(
        f"\n[bold green]Upgraded![/bold green] {weapon.replace('_', ' ').title()} is now "
        f"[{effects.color}]{effects.label}[/{effects.color}] quality. "
        f"({days} days, {s.captain.silver} silver remaining)"
    )
    s._save()


@app.command(name="learn-skill")
def learn_skill_cmd(
    skill_id: str = typer.Argument(None, help="Skill to learn (e.g. blacksmith)"),
) -> None:
    """Learn or advance a skill from a trainer at this port."""
    from portlight.content.skills import SKILLS, get_trainers_at_port
    from portlight.engine.skill_engine import can_learn_skill, get_skill_display, learn_skill

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked to learn skills.[/yellow]")
        return

    trainers = get_trainers_at_port(port.id)
    if not trainers and skill_id is None:
        console.print("[dim]No skill trainers at this port.[/dim]")
        return

    if skill_id is None:
        # Show available trainers
        from rich.table import Table
        table = Table(title=f"Skill Trainers — {port.name}")
        table.add_column("Trainer")
        table.add_column("Skill")
        table.add_column("Teaches Up To")
        table.add_column("Your Level")
        for t in trainers:
            skill = SKILLS.get(t.skill_id)
            current = get_skill_display(s.captain.skills, t.skill_id)
            max_name = skill.levels[t.max_teach_level - 1].name if skill else "?"
            table.add_row(t.name, skill.name if skill else t.skill_id, max_name, current)
        console.print(table)
        for t in trainers:
            console.print(f"\n  {t.dialog} — [dim]{t.name}[/dim]")
        return

    # Resolve display name to skill ID (e.g. "blacksmithing" -> "blacksmith")
    if skill_id not in SKILLS:
        _lower = skill_id.lower()
        for _sid, _sdef in SKILLS.items():
            if _sdef.name.lower() == _lower:
                skill_id = _sid
                break

    error = can_learn_skill(s.captain.skills, s.captain.silver, port.id, skill_id)
    if error:
        console.print(f"[red]{error}[/red]")
        return

    s.captain.skills, s.captain.silver, days = learn_skill(s.captain.skills, s.captain.silver, skill_id)
    for _ in range(days):
        s.advance()

    skill = SKILLS[skill_id]
    new_level = s.captain.skills[skill_id]
    level_name = skill.levels[new_level - 1].name
    console.print(f"\n[bold green]Learned {skill.name} — {level_name}![/bold green] ({days} days)")
    console.print(f"[dim]{skill.levels[new_level - 1].description}[/dim]")
    s._save()


@app.command(name="field-repair")
def field_repair_cmd(
    weapon: str = typer.Argument(..., help="Weapon ID to repair at sea"),
) -> None:
    """Repair a weapon at sea (requires Journeyman blacksmith skill)."""
    from portlight.engine.skill_engine import field_repair_weapon, get_skill_level

    s = _session()
    bs_level = get_skill_level(s.captain.skills, "blacksmith")
    gear = s.captain.combat_gear

    success, error = field_repair_weapon(weapon, gear.weapon_quality, gear.weapon_usage, bs_level)
    if error:
        console.print(f"[red]{error}[/red]")
        return
    console.print(f"[green]{weapon.replace('_', ' ').title()} repaired at sea — usage reset.[/green]")
    s._save()


# ---------------------------------------------------------------------------
# Spare / Take-All (post-victory choice)
# ---------------------------------------------------------------------------


def _finalize_victory(s, spared: bool) -> None:
    """Shared victory finalization — called by both spare and take-all commands."""
    global _active_encounter, _player_combatant, _opponent_combatant, _pending_victory
    from portlight.app import combat_views
    from portlight.content.factions import PIRATE_CAPTAINS
    from portlight.engine.captain_memory import get_or_create_memory, record_encounter
    from portlight.engine.underworld import record_duel_outcome

    enc = _active_encounter
    if enc is None:
        return

    gear = s.captain.combat_gear

    # Silver reward
    if spared:
        silver_gain = 20 + enc.enemy_strength * 3  # less silver for mercy
    else:
        silver_gain = 20 + enc.enemy_strength * 7  # more silver for taking all
    s.captain.silver += silver_gain
    s.world.pirates.duels_won += 1

    # Record encounter in captain memory (with spare flag)
    memory = get_or_create_memory(s.world.pirates.captain_memories, enc.enemy_captain_id)
    record_encounter(
        memory, s.world.day, enc.enemy_region, "player_won",
        player_spared=spared,
        player_used_firearm=False,
        crew_killed=max(0, enc.enemy_ship_crew_max - enc.enemy_ship_crew),
    )

    # Underworld standing
    uw_standing = s.captain.standing.underworld_standing
    standing_delta = record_duel_outcome(uw_standing, enc.enemy_faction_id, player_won=True, spared=spared)

    # Record weapon provenance
    if gear.melee_weapon:
        from portlight.engine.weapon_provenance import (
            RELIC_COLORS,
            RELIC_LABELS,
            WeaponProvenance,
            create_provenance,
            record_kill,
        )
        prov = gear.weapon_provenance.get(gear.melee_weapon)
        if not isinstance(prov, WeaponProvenance):
            prov = create_provenance(gear.melee_weapon)
            gear.weapon_provenance[gear.melee_weapon] = prov
        tier_change, new_epithet = record_kill(prov, enc.enemy_captain_id, enc.enemy_captain_name)
        if new_epithet:
            console.print(f"[bold magenta]Your weapon is now known as \"{new_epithet}\"![/bold magenta]")
        if tier_change:
            label = RELIC_LABELS.get(tier_change, tier_change)
            color = RELIC_COLORS.get(tier_change, "white")
            console.print(f"[{color}]Your weapon has reached {label} status — {prov.kills} kills.[/{color}]")

    # Roll loot (take-all gets more)
    try:
        from portlight.engine.loot import apply_loot, roll_loot
        loot = roll_loot(enc.enemy_captain_id, enc.enemy_strength, s._rng)
        if loot and not spared:
            apply_loot(loot, s.captain)
            console.print(combat_views.loot_view(loot) if hasattr(combat_views, 'loot_view') else f"[green]Loot: {loot}[/green]")
        elif loot and spared:
            # Sparing = no loot
            console.print("[dim]You leave their possessions untouched.[/dim]")
    except (ImportError, Exception):
        pass

    # Companion morale trigger
    try:
        from portlight.engine.companion_engine import CompanionState, PartyState, apply_morale_trigger, check_departures
        party_data = s.captain.party
        if isinstance(party_data, dict) and party_data.get("companions"):
            companions = [
                CompanionState(
                    companion_id=c["companion_id"], role_id=c["role_id"],
                    morale=c.get("morale", 70), joined_day=c.get("joined_day", 0),
                    personality=c.get("personality", "pragmatic"),
                ) for c in party_data["companions"]
            ]
            party = PartyState(companions=companions, max_size=party_data.get("max_size", 2),
                               departed=party_data.get("departed", []))

            trigger = "spared_enemy" if spared else "took_all"
            reactions = apply_morale_trigger(party, trigger)
            for comp_id, delta, flavor in reactions:
                console.print(f"  [dim]{flavor}[/dim]")

            departures = check_departures(party)
            for dep in departures:
                console.print(f"\n[bold red]{dep.companion_name} leaves the crew: \"{dep.departure_line}\"[/bold red]")

            # Save party back
            s.captain.party = {
                "companions": [
                    {"companion_id": c.companion_id, "role_id": c.role_id,
                     "morale": c.morale, "joined_day": c.joined_day, "personality": c.personality}
                    for c in party.companions
                ],
                "max_size": party.max_size, "departed": party.departed,
            }
    except (ImportError, Exception):
        pass

    # Summary
    console.print(f"\n[green]+{silver_gain} silver[/green]")
    if standing_delta > 0:
        console.print(f"[green]+{standing_delta} underworld standing with {enc.enemy_faction_id}[/green]")
    elif standing_delta < 0:
        console.print(f"[red]{standing_delta} underworld standing with {enc.enemy_faction_id}[/red]")

    # Captain flavor from factions
    captain_data = PIRATE_CAPTAINS.get(enc.enemy_captain_id)
    if captain_data:
        if spared:
            console.print(f"\n[italic]{captain_data.duel_defeat}[/italic]")
        else:
            console.print(f"\n[italic]{captain_data.duel_victory}[/italic]")

    # Cleanup
    _clear_encounter(s)
    s._save()


@app.command()
def spare() -> None:
    """Show mercy to a defeated pirate captain. Gains respect, reduces grudge."""
    global _pending_victory
    s = _session()
    _restore_encounter(s)
    if not _pending_victory or _active_encounter is None:
        console.print("[yellow]No defeated opponent to spare. Win a duel first.[/yellow]")
        return

    enc = _active_encounter
    console.print("\n[bold cyan]You sheathe your blade and step back.[/bold cyan]")
    console.print(f"\"You fought well, {enc.enemy_captain_name}. Go — and remember this mercy.\"")

    _finalize_victory(s, spared=True)


@app.command(name="take-all")
def take_all() -> None:
    """Take everything from the defeated captain. More silver, more grudge."""
    global _pending_victory
    s = _session()
    _restore_encounter(s)
    if not _pending_victory or _active_encounter is None:
        console.print("[yellow]No defeated opponent. Win a duel first.[/yellow]")
        return

    enc = _active_encounter
    console.print(f"\n[bold red]You take {enc.enemy_captain_name}'s silver, weapons, and dignity.[/bold red]")
    console.print("\"You lost. Everything you carry is mine now.\"")

    _finalize_victory(s, spared=False)


# ---------------------------------------------------------------------------
# Bounty commands
# ---------------------------------------------------------------------------

@app.command()
def bounty(
    action: str = typer.Argument(None, help="list, accept <id>, claim <id>, or omit to view board"),
    target_id: str = typer.Argument(None, help="Bounty target captain ID"),
) -> None:
    """View the bounty board, accept targets, or claim rewards."""
    from portlight.engine.bounty import generate_bounty_board, accept_bounty, claim_bounty
    s = _session()

    if action is None or action == "list":
        targets = generate_bounty_board(s.world.pirates, s._rng)
        if not targets:
            console.print("[dim]No bounties available. All known pirates have been defeated.[/dim]")
            return
        console.print("\n[bold]Bounty Board[/bold]")
        for t in targets:
            active = " [cyan][HUNTING][/cyan]" if t.captain_id in s.captain.active_bounties else ""
            console.print(f"\n  [bold]{t.captain_name}[/bold] ({t.captain_id}){active}")
            console.print(f"    Faction: {t.faction_id}  |  Region: {t.region}  |  Difficulty: {t.difficulty}")
            console.print(f"    Reward: [green]{t.reward} silver[/green]")
            console.print(f"    {t.description}")
        console.print(f"\n  Active bounties: {len(s.captain.active_bounties)}/3")
        console.print("  Use [cyan]bounty accept <id>[/cyan] to hunt a target.")
        return

    if action == "accept":
        if not target_id:
            console.print("[red]Usage: bounty accept <captain_id>[/red]")
            return
        err = accept_bounty(s.captain, target_id)
        if err:
            console.print(f"[red]{err}[/red]")
            return
        console.print(f"\n[bold cyan]Bounty accepted![/bold cyan] Hunting [bold]{target_id}[/bold].")
        console.print("Defeat them at sea, then return to claim your reward.")
        s._save()
        return

    if action == "claim":
        if not target_id:
            console.print("[red]Usage: bounty claim <captain_id>[/red]")
            return
        result = claim_bounty(s.captain, s.world.pirates, target_id)
        if isinstance(result, str):
            console.print(f"[red]{result}[/red]")
            return
        console.print(f"\n[bold green]Bounty claimed![/bold green] +{result} silver.")
        from portlight.app.formatting import silver
        console.print(f"Silver: {silver(s.captain.silver)}")
        s._save()
        return

    console.print(f"[red]Unknown bounty action: {action}[/red]. Use: list, accept, claim")


# ---------------------------------------------------------------------------
# Companion commands
# ---------------------------------------------------------------------------

def _get_party():
    """Get the captain's party as a PartyState object."""
    from portlight.engine.companion_engine import CompanionState, PartyState
    s = _session()
    pd = s.captain.party
    if isinstance(pd, dict):
        companions = [
            CompanionState(
                companion_id=c["companion_id"], role_id=c["role_id"],
                morale=c.get("morale", 70), joined_day=c.get("joined_day", 0),
                personality=c.get("personality", "pragmatic"),
            ) for c in pd.get("companions", [])
        ]
        return PartyState(companions=companions, max_size=pd.get("max_size", 2), departed=pd.get("departed", []))
    return pd


def _save_party(s, party):
    """Save party state back to captain."""
    s.captain.party = {
        "companions": [
            {"companion_id": c.companion_id, "role_id": c.role_id,
             "morale": c.morale, "joined_day": c.joined_day, "personality": c.personality}
            for c in party.companions
        ],
        "max_size": party.max_size,
        "departed": party.departed,
    }
    s._save()


@app.command(name="recruit")
def recruit_cmd(
    companion_id: str = typer.Argument(None, help="Companion ID to recruit"),
) -> None:
    """Recruit a companion at this port."""
    from portlight.content.companions import COMPANIONS, get_companions_at_port
    from portlight.engine.companion_engine import can_recruit, recruit

    s = _session()
    port = s.current_port
    if not port:
        console.print("[yellow]Must be docked to recruit companions.[/yellow]")
        return

    party = _get_party()

    if companion_id is None:
        available = get_companions_at_port(port.id)
        if not available:
            console.print("[dim]No companions available at this port.[/dim]")
            return
        from rich.table import Table
        table = Table(title=f"Available Companions — {port.name}")
        table.add_column("Name")
        table.add_column("Role")
        table.add_column("Cost")
        table.add_column("Req. Standing")
        for c in available:
            already = any(p.companion_id == c.id for p in party.companions)
            departed = c.id in party.departed
            status = " [green](in party)[/green]" if already else " [red](departed)[/red]" if departed else ""
            table.add_row(c.name + status, c.role_id.title(), f"{c.hire_cost} silver", f"{c.required_standing} {c.region}")
        console.print(table)
        for c in available:
            console.print(f"\n  {c.greeting}")
            console.print(f"  [dim]{c.description}[/dim]")
        return

    error = can_recruit(party, companion_id, s.captain.silver, s.captain.standing.regional_standing, port.id)
    if error:
        console.print(f"[red]{error}[/red]")
        return

    comp = COMPANIONS[companion_id]
    s.captain.silver -= comp.hire_cost
    recruit(party, companion_id, s.world.day)
    _save_party(s, party)
    console.print(f"\n[bold green]{comp.name} joins your crew![/bold green]")
    console.print(f"  {comp.hire_dialog}")


@app.command(name="dismiss-companion")
def dismiss_cmd(
    companion_id: str = typer.Argument(..., help="Companion ID to dismiss"),
) -> None:
    """Dismiss a companion from your party."""
    from portlight.content.companions import COMPANIONS
    from portlight.engine.companion_engine import dismiss

    s = _session()
    party = _get_party()
    error = dismiss(party, companion_id)
    if error:
        console.print(f"[red]{error}[/red]")
        return
    comp = COMPANIONS.get(companion_id)
    name = comp.name if comp else companion_id
    _save_party(s, party)
    console.print(f"[yellow]{name} leaves your crew.[/yellow]")


@app.command()
def party() -> None:
    """Show your companion party."""
    from portlight.engine.companion_engine import get_cohesion, get_party_summary

    _session()  # ensure active game
    p = _get_party()
    summary = get_party_summary(p)

    if not summary:
        console.print("[dim]No companions. Visit ports to recruit crew members.[/dim]")
        return

    from rich.table import Table
    table = Table(title=f"Your Party (cohesion: {get_cohesion(p)}%)")
    table.add_column("Name")
    table.add_column("Role")
    table.add_column("Morale")
    table.add_column("Status")
    table.add_column("Personality")
    for cs in summary:
        morale_color = "green" if cs["morale"] >= 60 else "yellow" if cs["morale"] >= 30 else "red"
        table.add_row(
            cs["name"], cs["role"],
            f"[{morale_color}]{cs['morale']}[/{morale_color}]",
            cs["morale_status"],
            cs["personality"],
        )
    console.print(table)


@app.command("print-and-play")
def print_and_play(
    output: str = typer.Option(
        "portlight-print-and-play.pdf",
        "--output", "-o",
        help="Output PDF file path",
    ),
) -> None:
    """Generate the Print-and-Play board game PDF kit."""
    from pathlib import Path

    try:
        from portlight.printandplay.generator import generate
    except ImportError:
        console.print(
            "[red]fpdf2 is required for PDF generation.[/red]\n"
            "Install with: [bold]pip install portlight[printandplay][/bold]"
        )
        raise typer.Exit(1)

    out_path = Path(output)
    console.print("[dim]Generating Print-and-Play kit...[/dim]")
    result = generate(out_path)
    console.print(f"[green]Board game PDF generated:[/green] {result}")


if __name__ == "__main__":
    app()
