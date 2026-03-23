"""Rich views - game-facing screens that answer player questions.

Each view is a function that returns a Rich renderable (Panel, Table, Group).
Views never mutate game state. They read and present.

Captain screen answers: who am I, what advantages, what posture, what next.
Reputation screen answers: where do I stand, what's open, what's endangered.
Port screen answers: what's cheap, what's expensive, what do I hold, readiness.
Market screen answers: buy/sell prices, scarcity, what I can afford.
Route screen answers: where can I go, how long, how risky, can I provision it.
Ledger screen answers: what trades made money, what routes work, upgrade progress.
Shipyard screen answers: what ships, how they compare, can I afford one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from portlight.app import formatting as fmt
from portlight.content.goods import GOODS
from portlight.content.ships import SHIPS

if TYPE_CHECKING:
    from portlight.engine.campaign import CampaignState, SessionSnapshot
    from portlight.engine.captain_identity import CaptainTemplate
    from portlight.engine.contracts import ContractBoard
    from portlight.engine.infrastructure import InfrastructureState
    from portlight.engine.models import Captain, Port, ReputationState, Route, Ship, ShipTemplate, WorldState
    from portlight.receipts.models import ReceiptLedger


# ---------------------------------------------------------------------------
# Captain view - identity, advantages, posture
# ---------------------------------------------------------------------------

def captain_view(captain: "Captain", template: "CaptainTemplate") -> Panel:
    """Captain identity screen: who you are, your modifiers, your posture."""
    lines: list[str] = []
    lines.append(f"[bold]{captain.name}[/bold] - {template.title}")
    lines.append(f"[italic]{template.description}[/italic]")
    lines.append("")

    # Pricing modifiers
    p = template.pricing
    lines.append("[bold]Trade Profile[/bold]")
    lines.append(f"  Buy prices:    {fmt.modifier_str(p.buy_price_mult, invert=True)}")
    lines.append(f"  Sell prices:   {fmt.modifier_str(p.sell_price_mult)}")
    if p.luxury_sell_bonus > 0:
        lines.append(f"  Luxury bonus:  [green]+{int(p.luxury_sell_bonus * 100)}% on silk/spice/porcelain[/green]")
    lines.append(f"  Port fees:     {fmt.modifier_str(p.port_fee_mult, invert=True)}")
    lines.append("")

    # Voyage modifiers
    v = template.voyage
    lines.append("[bold]Voyage Profile[/bold]")
    lines.append(f"  Provision burn:  {fmt.modifier_str(v.provision_burn, invert=True)}")
    if v.speed_bonus > 0:
        lines.append(f"  Speed bonus:     [green]+{v.speed_bonus}[/green]")
    if v.storm_resist_bonus > 0:
        lines.append(f"  Storm resist:    [green]+{int(v.storm_resist_bonus * 100)}%[/green]")
    lines.append(f"  Cargo damage:    {fmt.modifier_str(v.cargo_damage_mult, invert=True)}")
    lines.append("")

    # Inspection profile
    i = template.inspection
    lines.append("[bold]Inspection Profile[/bold]")
    lines.append(f"  Frequency:  {fmt.modifier_str(i.inspection_chance_mult, invert=True)}")
    if i.seizure_risk > 0:
        lines.append(f"  Seizure:    [red]{int(i.seizure_risk * 100)}% per inspection[/red]")
    lines.append(f"  Fines:      {fmt.modifier_str(i.fine_mult, invert=True)}")
    lines.append("")

    # Strengths / weaknesses
    lines.append("[bold green]Strengths[/bold green]")
    for s in template.strengths:
        lines.append(f"  + {s}")
    lines.append("[bold red]Weaknesses[/bold red]")
    for w in template.weaknesses:
        lines.append(f"  - {w}")

    return Panel("\n".join(lines), title=f"[bold]{template.name}[/bold]", border_style="blue")


# ---------------------------------------------------------------------------
# Reputation view - standing, heat, trust
# ---------------------------------------------------------------------------

def reputation_view(standing: "ReputationState", captain: "Captain") -> Panel:
    """Reputation screen: standing, heat, trust, access effects, recent incidents."""
    from portlight.engine.reputation import (
        get_fee_modifier,
        get_inspection_modifier,
        get_service_modifier,
        get_trust_tier,
    )

    lines: list[str] = []

    # Regional standing with fee effects
    lines.append("[bold]Regional Standing[/bold]")
    for region, value in standing.regional_standing.items():
        fee_mod = get_fee_modifier(standing, region)
        effect = ""
        if fee_mod < 1.0:
            effect = f"  [green]({int((1 - fee_mod) * 100)}% cheaper fees)[/green]"
        elif fee_mod > 1.0:
            effect = f"  [red](+{int((fee_mod - 1) * 100)}% fees)[/red]"
        lines.append(f"  {region:20s} {fmt.standing_tag(value)} ({value}){effect}")
    lines.append("")

    # Customs heat with inspection effects
    lines.append("[bold]Customs Heat[/bold]")
    for region, value in standing.customs_heat.items():
        insp_mod = get_inspection_modifier(standing, region)
        effect = ""
        if insp_mod > 1.0:
            effect = f"  [red](+{int((insp_mod - 1) * 100)}% inspections)[/red]"
        lines.append(f"  {region:20s} {fmt.heat_tag(value)} ({value}){effect}")
    lines.append("")

    # Commercial trust with tier
    trust_tier = get_trust_tier(standing)
    lines.append("[bold]Commercial Trust[/bold]")
    lines.append(f"  {fmt.trust_tag(standing.commercial_trust)} ({standing.commercial_trust}) - tier: [bold]{trust_tier}[/bold]")
    lines.append("")

    # Port standing with service effects (top 5 by value)
    if standing.port_standing:
        lines.append("[bold]Port Standing[/bold]")
        sorted_ports = sorted(standing.port_standing.items(), key=lambda x: x[1], reverse=True)
        for port_id, value in sorted_ports[:8]:
            svc_mod = get_service_modifier(standing, port_id)
            effect = ""
            if svc_mod < 1.0:
                effect = f"  [green]({int((1 - svc_mod) * 100)}% cheaper services)[/green]"
            lines.append(f"  {port_id:20s} {fmt.standing_tag(value)} ({value}){effect}")
        lines.append("")

    # Recent incidents (last 5)
    if standing.recent_incidents:
        lines.append("[bold]Recent Incidents[/bold]")
        for inc in standing.recent_incidents[:5]:
            # Color based on whether it was good or bad
            if inc.heat_delta > 0:
                icon = "[red]![/red]"
            elif inc.standing_delta > 0 or inc.trust_delta > 0:
                icon = "[green]+[/green]"
            else:
                icon = "[dim].[/dim]"
            lines.append(f"  {icon} Day {inc.day} at {inc.port_id}: {inc.description}")

    return Panel("\n".join(lines), title="[bold]Reputation[/bold]", border_style="cyan")


# ---------------------------------------------------------------------------
# Status view - the captain's dashboard
# ---------------------------------------------------------------------------

def status_view(world: "WorldState", ledger: "ReceiptLedger", infra: "InfrastructureState | None" = None) -> Panel:
    """Captain overview: silver, ship, cargo, provisions, position, upgrade distance, upkeep."""
    captain = world.captain
    ship = captain.ship

    lines: list[str] = []
    lines.append(f"[bold]{captain.name}[/bold]  Day {world.day}")
    lines.append(f"Silver: {fmt.silver(captain.silver)}")

    if ship:
        lines.append(f"Ship: [bold]{ship.name}[/bold] ({ship.template_id})")
        # Show resolved stats if upgrades are installed
        from portlight.content.upgrades import UPGRADES as _UPGRADES_CAT
        from portlight.engine.ship_stats import resolve_cargo_capacity, resolve_hull_max
        eff_cargo = resolve_cargo_capacity(ship, _UPGRADES_CAT)
        eff_hull_max = resolve_hull_max(ship, _UPGRADES_CAT)
        cargo_used = sum(c.quantity for c in captain.cargo)
        lines.append(f"Cargo: {fmt.cargo_bar(cargo_used, eff_cargo)}")
        lines.append(f"Hull:  {fmt.hull_bar(ship.hull, eff_hull_max)}")
        lines.append(f"Crew:  {fmt.crew_status(ship.crew, ship.crew_max, _crew_min(ship))}")
        if ship.upgrades:
            upgrade_names = []
            for inst in ship.upgrades:
                utmpl = _UPGRADES_CAT.get(inst.upgrade_id)
                upgrade_names.append(utmpl.name if utmpl else inst.upgrade_id)
            lines.append(f"Upgrades: {', '.join(upgrade_names)} ({len(ship.upgrades)}/{ship.upgrade_slots})")
    lines.append(f"Provisions: {fmt.provision_status(captain.provisions)}")

    # Current location
    if world.voyage:
        from portlight.engine.models import VoyageStatus
        if world.voyage.status == VoyageStatus.AT_SEA:
            pct = int(world.voyage.progress / max(world.voyage.distance, 1) * 100)
            dest_name = world.ports.get(world.voyage.destination_id)
            dest_label = dest_name.name if dest_name else world.voyage.destination_id
            lines.append(f"[bold cyan]At sea[/bold cyan] -> {dest_label} ({pct}% complete, day {world.voyage.days_elapsed})")
        else:
            port = world.ports.get(world.voyage.destination_id)
            lines.append(f"Docked at [bold]{port.name if port else '???'}[/bold]")

    # Upgrade tracker
    next_ship = _next_upgrade(ship, captain.silver)
    if next_ship:
        lines.append(f"Next upgrade: {next_ship.name} - {fmt.upgrade_distance(captain.silver, next_ship.price)}")

    # Net P&L
    if ledger.receipts:
        lines.append(f"Net P&L: {fmt.silver_delta(ledger.net_profit)} ({len(ledger.receipts)} trades)")

    # Wanted status
    if captain.wanted_level >= 3:
        lines.append("[bold red][HUNTED][/bold red] Bounty hunters are searching for you!")
    elif captain.wanted_level >= 2:
        lines.append("[bold yellow][WANTED][/bold yellow] Ports are watching for you.")
    elif captain.wanted_level >= 1:
        lines.append("[yellow][WATCHED][/yellow] Your reputation precedes you.")

    # Deferred debts
    if captain.deferred_fees:
        total_debt = sum(f["amount"] for f in captain.deferred_fees)
        lines.append(f"[red]Debts: {total_debt} silver owed[/red]")

    # Daily upkeep burn (if infrastructure exists)
    upkeep = _daily_upkeep(infra) if infra else 0
    if upkeep > 0:
        lines.append(f"Daily upkeep: [yellow]{upkeep}[/yellow] silver/day")

    # Infrastructure summary
    if infra:
        parts: list[str] = []
        active_wh = sum(1 for w in infra.warehouses if w.active)
        active_br = sum(1 for b in infra.brokers if b.active and b.tier.value != "none")
        active_lic = sum(1 for lic in infra.licenses if lic.active)
        if active_wh:
            parts.append(f"{active_wh} warehouse{'s' if active_wh > 1 else ''}")
        if active_br:
            parts.append(f"{active_br} broker{'s' if active_br > 1 else ''}")
        if active_lic:
            parts.append(f"{active_lic} license{'s' if active_lic > 1 else ''}")
        if parts:
            lines.append(f"Active: {', '.join(parts)}")

    return Panel("\n".join(lines), title="[bold]Captain Status[/bold]", border_style="blue")


def _daily_upkeep(infra: "InfrastructureState") -> int:
    """Compute total daily upkeep across all active infrastructure."""
    from portlight.content.infrastructure import LICENSE_CATALOG
    total = 0
    for w in infra.warehouses:
        if w.active:
            total += w.upkeep_per_day
    for b in infra.brokers:
        if b.active and b.tier.value != "none":
            from portlight.content.infrastructure import available_broker_tiers
            specs = available_broker_tiers(b.region)
            spec = next((s for s in specs if s.tier == b.tier), None)
            if spec:
                total += spec.upkeep_per_day
    for lic in infra.licenses:
        if lic.active:
            spec = LICENSE_CATALOG.get(lic.license_id)
            if spec:
                total += spec.upkeep_per_day
    if infra.credit and infra.credit.active:
        # Interest is periodic not daily, but show effective daily rate
        from portlight.content.infrastructure import available_credit_tiers
        tiers = available_credit_tiers()
        cred = infra.credit
        if cred.outstanding > 0:
            tier_spec = next((t for t in tiers if t.tier.value == cred.tier), None)
            if tier_spec and tier_spec.interest_period > 0:
                daily_interest = int(cred.outstanding * tier_spec.interest_rate / tier_spec.interest_period)
                total += daily_interest
    return total


# ---------------------------------------------------------------------------
# Welcome view - new game first screen
# ---------------------------------------------------------------------------

def welcome_view(
    captain: "Captain",
    template: "CaptainTemplate",
    world: "WorldState",
    infra: "InfrastructureState",
) -> Panel:
    """First-run welcome screen with captain identity and suggested first moves."""
    lines: list[str] = []
    lines.append(f"[bold]{captain.name}[/bold] — {template.title}")
    lines.append(f"[italic]{template.description}[/italic]")
    lines.append("")

    # Current port highlights
    port = None
    if world.voyage:
        from portlight.engine.models import VoyageStatus
        if world.voyage.status == VoyageStatus.IN_PORT:
            port = world.ports.get(world.voyage.destination_id)

    if port:
        cheap = []
        expensive = []
        for slot in port.market:
            good = GOODS.get(slot.good_id)
            if not good:
                continue
            ratio = slot.stock_current / max(slot.stock_target, 1)
            if ratio > 1.3:
                cheap.append(good.name)
            elif ratio < 0.5:
                expensive.append(good.name)
        if cheap:
            lines.append(f"Cheap at {port.name}: [green]{', '.join(cheap)}[/green]")
        if expensive:
            lines.append(f"Pricey at {port.name}: [red]{', '.join(expensive)}[/red]")
        lines.append("")

    # Suggested first moves
    lines.append("[bold]Suggested first moves:[/bold]")
    lines.append("  [cyan]market[/cyan]      — see what's cheap and what sells")
    lines.append("  [cyan]buy grain 10[/cyan] — buy goods to trade at another port")
    lines.append("  [cyan]routes[/cyan]       — see where you can sail")
    lines.append("  [cyan]contracts[/cyan]    — pick up a delivery contract for bonus silver")
    lines.append("")
    lines.append("[dim]As you grow, unlock warehouses, broker offices, licenses, and more.[/dim]")

    return Panel("\n".join(lines), title="[bold]Welcome to Portlight[/bold]", border_style="green")


def hint_line(
    world: "WorldState",
    infra: "InfrastructureState",
    board: "ContractBoard",
) -> str | None:
    """Return one contextual hint based on current game state, or None."""
    captain = world.captain

    # Low provisions warning
    if captain.provisions < 5:
        return "[yellow]Low provisions![/yellow] Buy more before sailing: [cyan]portlight provision 15[/cyan]"

    # Ship upgrade close
    ship = captain.ship
    if ship:
        next_ship = _next_upgrade(ship, captain.silver)
        if next_ship:
            gap = next_ship.price - captain.silver
            if 0 < gap <= 200:
                return f"[yellow]{gap} silver[/yellow] from upgrading to {next_ship.name}. A few good trades away."

    # No warehouse yet and have done some trades
    if not any(w.active for w in infra.warehouses):
        cargo_used = sum(c.quantity for c in captain.cargo)
        if ship and cargo_used > ship.cargo_capacity * 0.5:
            return "Hold getting full? Lease a warehouse to stage cargo: [cyan]portlight warehouse lease depot[/cyan]"

    # Available contracts
    if board.offers and not board.active:
        return "Contracts available at the board. Accept one for bonus silver: [cyan]portlight contracts[/cyan]"

    return None


# ---------------------------------------------------------------------------
# Port view - arrival screen
# ---------------------------------------------------------------------------

def port_view(port: "Port", captain: "Captain") -> Panel:
    """Port arrival screen: name, features, notable market conditions."""
    lines: list[str] = []
    lines.append(f"[italic]{port.description}[/italic]")
    lines.append(f"Region: {port.region}  |  Port fee: {fmt.silver(port.port_fee)}")
    lines.append(f"Provisions: {port.provision_cost}/day  |  Repairs: {port.repair_cost}/hp  |  Crew: {port.crew_cost}/head")

    if port.features:
        feats = ", ".join(f.value.replace("_", " ").title() for f in port.features)
        lines.append(f"Facilities: [cyan]{feats}[/cyan]")

    # Market highlights
    cheap = []
    expensive = []
    for slot in port.market:
        good = GOODS.get(slot.good_id)
        if not good:
            continue
        ratio = slot.stock_current / max(slot.stock_target, 1)
        if ratio > 1.3:
            cheap.append(f"[green]{good.name}[/green]")
        elif ratio < 0.5:
            expensive.append(f"[red]{good.name}[/red]")

    if cheap:
        lines.append(f"Cheap here: {', '.join(cheap)}")
    if expensive:
        lines.append(f"Pricey here: {', '.join(expensive)}")

    # Cargo summary
    if captain.cargo:
        cargo_names = [f"{c.quantity}x {GOODS[c.good_id].name}" for c in captain.cargo if c.good_id in GOODS]
        lines.append(f"You carry: {', '.join(cargo_names)}")
    else:
        lines.append("[dim]Hold is empty[/dim]")

    return Panel("\n".join(lines), title=f"[bold]{port.name}[/bold]", border_style="cyan")


# ---------------------------------------------------------------------------
# Market view - the trading screen
# ---------------------------------------------------------------------------

def market_view(port: "Port", captain: "Captain") -> Panel:
    """Full market board: buy/sell prices, scarcity, what you hold, what you can afford."""
    table = Table(title=f"{port.name} Market", show_header=True, header_style="bold")
    table.add_column("Good", style="bold")
    table.add_column("Buy", justify="right")
    table.add_column("Sell", justify="right")
    table.add_column("Stock", justify="center")
    table.add_column("Status")
    table.add_column("You Hold", justify="right")
    table.add_column("Can Buy", justify="right")

    has_flood = False
    for slot in port.market:
        good = GOODS.get(slot.good_id)
        if not good:
            continue
        held = sum(c.quantity for c in captain.cargo if c.good_id == slot.good_id)
        affordable = captain.silver // slot.buy_price if slot.buy_price > 0 else 0
        # Cap by available stock and cargo space
        ship = captain.ship
        if ship:
            cargo_used = sum(c.quantity for c in captain.cargo)
            space = ship.cargo_capacity - int(cargo_used)
            affordable = min(affordable, slot.stock_current, max(0, space))

        # Show flood penalty as sell price warning with percentage
        sell_str = str(slot.sell_price)
        if slot.flood_penalty > 0.1:
            flood_pct = int(slot.flood_penalty * 100)
            sell_str = f"[red]{slot.sell_price}[/red] (flooded: -{flood_pct}%)"
            has_flood = True
        elif slot.flood_penalty > 0:
            sell_str = f"[yellow]{slot.sell_price}[/yellow]"

        # Show good ID when it differs from display name (helps with buy/sell commands)
        good_label = good.name if good.name.lower().replace(" ", "_") == slot.good_id else f"{good.name} ({slot.good_id})"
        table.add_row(
            good_label,
            str(slot.buy_price),
            sell_str,
            f"{slot.stock_current}/{slot.stock_target}",
            fmt.scarcity_tag(slot.stock_current, slot.stock_target),
            str(held) if held > 0 else "[dim]-[/dim]",
            str(affordable) if affordable > 0 else "[dim]-[/dim]",
        )

    footer = ""
    if has_flood:
        footer = "\n[dim]Flooded goods sell for less. Trade elsewhere or wait for recovery.[/dim]"

    return Panel(Group(table, Text.from_markup(footer) if footer else Text("")), border_style="green")


# ---------------------------------------------------------------------------
# Cargo view
# ---------------------------------------------------------------------------

def cargo_view(captain: "Captain") -> Panel:
    """What's in the hold, cost basis, current value hints."""
    if not captain.cargo:
        return Panel("[dim]Hold is empty[/dim]", title="[bold]Cargo[/bold]", border_style="yellow")

    from portlight.content.upgrades import UPGRADES as _UPG
    from portlight.engine.ship_stats import resolve_cargo_capacity

    table = Table(show_header=True, header_style="bold")
    table.add_column("Good", style="bold")
    table.add_column("Qty", justify="right")
    table.add_column("Avg Cost", justify="right")
    table.add_column("Total Cost", justify="right")

    for item in captain.cargo:
        good = GOODS.get(item.good_id)
        name = good.name if good else item.good_id
        avg = item.cost_basis // item.quantity if item.quantity > 0 else 0
        table.add_row(name, str(item.quantity), str(avg), str(item.cost_basis))

    ship = captain.ship
    if ship:
        cargo_used = sum(c.quantity for c in captain.cargo)
        eff_cargo = resolve_cargo_capacity(ship, _UPG)
        footer = f"\nCargo: {fmt.cargo_bar(cargo_used, eff_cargo)}"
    else:
        footer = ""

    return Panel(Group(table, Text.from_markup(footer) if footer else Text("")),
                 title="[bold]Cargo Hold[/bold]", border_style="yellow")


# ---------------------------------------------------------------------------
# Routes view - where can I go
# ---------------------------------------------------------------------------

def routes_view(world: "WorldState") -> Panel:
    """Available routes from current port with travel time, risk, provision cost."""
    current_port_id = world.voyage.destination_id if world.voyage else None
    ship = world.captain.ship

    table = Table(title="Available Routes", show_header=True, header_style="bold")
    table.add_column("Destination", style="bold")
    table.add_column("Region")
    table.add_column("Distance", justify="right")
    table.add_column("Est. Days", justify="right")
    table.add_column("Risk")
    table.add_column("Min Ship")
    table.add_column("Provisions", justify="right")

    from portlight.engine.voyage import check_route_suitability

    routes = _routes_from(world.routes, current_port_id)
    for route in routes:
        dest_id = route.port_b if route.port_a == current_port_id else route.port_a
        dest_port = world.ports.get(dest_id)
        if not dest_port:
            continue
        speed = ship.speed if ship else 4
        est_days = max(1, round(route.distance / speed))
        prov_needed = est_days + 2  # buffer

        prov_ok = world.captain.provisions >= prov_needed
        prov_color = "green" if prov_ok else "red"

        # Ship suitability
        suit_warning = check_route_suitability(route, ship) if ship else None
        if suit_warning and "BLOCKED" in suit_warning:
            ship_col = f"[bold red]{route.min_ship_class.title()}[/bold red]"
        elif suit_warning:
            ship_col = f"[yellow]{route.min_ship_class.title()}[/yellow]"
        else:
            ship_col = f"[dim]{route.min_ship_class.title()}[/dim]"

        table.add_row(
            dest_port.name,
            dest_port.region,
            str(route.distance),
            fmt.travel_time(route.distance, speed),
            fmt.risk_tag(route.danger),
            ship_col,
            f"[{prov_color}]{prov_needed} days[/{prov_color}]",
        )

    if not routes:
        return Panel("[dim]No routes available from here[/dim]", title="Routes", border_style="magenta")

    return Panel(table, border_style="magenta")


# ---------------------------------------------------------------------------
# Voyage view - at sea screen
# ---------------------------------------------------------------------------

def voyage_view(world: "WorldState", events: list | None = None) -> Panel:
    """At-sea status: progress, recent events, ship condition."""
    voyage = world.voyage
    captain = world.captain

    lines: list[str] = []

    if voyage:
        origin = world.ports.get(voyage.origin_id)
        dest = world.ports.get(voyage.destination_id)
        origin_name = origin.name if origin else voyage.origin_id
        dest_name = dest.name if dest else voyage.destination_id

        pct = min(100, int(voyage.progress / max(voyage.distance, 1) * 100))
        # Progress bar
        filled = min(10, pct // 10)
        empty = 10 - filled
        bar = f"[cyan]{'#' * filled}{'-' * empty}[/cyan]"
        lines.append(f"{origin_name} {bar} {dest_name}")
        lines.append(f"Day {voyage.days_elapsed} at sea  |  {pct}% complete")
    else:
        lines.append("[dim]Not at sea[/dim]")

    if captain.ship:
        lines.append(f"Hull: {fmt.hull_bar(captain.ship.hull, captain.ship.hull_max)}")
        lines.append(f"Crew: {fmt.crew_status(captain.ship.crew, captain.ship.crew_max, _crew_min(captain.ship))}")
    lines.append(f"Provisions: {fmt.provision_status(captain.provisions)}")
    lines.append(f"Silver: {fmt.silver(captain.silver)}")

    if events:
        lines.append("")
        for event in events:
            lines.append(f"  {_event_icon(event.event_type.value)} {event.message}")

    return Panel("\n".join(lines), title="[bold]At Sea[/bold]", border_style="cyan")


# ---------------------------------------------------------------------------
# Ledger view
# ---------------------------------------------------------------------------

def ledger_view(ledger: "ReceiptLedger", captain: "Captain") -> Panel:
    """Trade history with P&L, route analysis, upgrade tracker."""
    if not ledger.receipts:
        return Panel("[dim]No trades recorded yet[/dim]", title="[bold]Trade Ledger[/bold]", border_style="white")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Day", justify="right")
    table.add_column("Port")
    table.add_column("Action", justify="center")
    table.add_column("Good")
    table.add_column("Qty", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Total", justify="right")

    # Show last 15 receipts
    recent = ledger.receipts[-15:]
    for r in recent:
        action_style = "[green]BUY[/green]" if r.action.value == "buy" else "[red]SELL[/red]"
        good = GOODS.get(r.good_id)
        good_name = good.name if good else r.good_id
        table.add_row(
            str(r.day), r.port_id, action_style, good_name,
            str(r.quantity), str(r.unit_price), str(r.total_price),
        )

    summary_lines = []
    summary_lines.append(f"Total bought: {fmt.silver(ledger.total_buys)}")
    summary_lines.append(f"Total sold:   {fmt.silver(ledger.total_sells)}")
    summary_lines.append(f"Net P&L:      {fmt.silver_delta(ledger.net_profit)}")
    summary_lines.append(f"Trades:       {len(ledger.receipts)}")

    # Upgrade tracker
    next_ship = _next_upgrade(captain.ship, captain.silver)
    if next_ship:
        summary_lines.append(f"Next ship:    {next_ship.name} - {fmt.upgrade_distance(captain.silver, next_ship.price)}")

    summary = "\n".join(summary_lines)

    return Panel(Group(table, Text(""), Text.from_markup(summary)),
                 title="[bold]Trade Ledger[/bold]", border_style="white")


# ---------------------------------------------------------------------------
# Shipyard view
# ---------------------------------------------------------------------------

def fleet_view(captain: "Captain") -> Panel:
    """Show all ships in the player's fleet."""
    from portlight.content.upgrades import UPGRADES as _UPG
    from portlight.engine.ship_stats import resolve_cargo_capacity

    table = Table(title="Fleet", show_header=True, header_style="bold")
    table.add_column("Ship", style="bold")
    table.add_column("Class")
    table.add_column("Hull", justify="right")
    table.add_column("Cargo", justify="right")
    table.add_column("Crew", justify="right")
    table.add_column("Location")
    table.add_column("Upgrades")

    # Flagship
    if captain.ship:
        s = captain.ship
        cargo_used = sum(c.quantity for c in captain.cargo)
        eff_cargo = resolve_cargo_capacity(s, _UPG)
        upg_str = str(len(s.upgrades)) if s.upgrades else "[dim]-[/dim]"
        table.add_row(
            f"{s.name} [cyan]*flagship[/cyan]",
            s.template_id.replace("_", " ").title(),
            f"{s.hull}/{s.hull_max}",
            f"{cargo_used}/{eff_cargo}",
            str(s.crew),
            "[bold cyan]Active[/bold cyan]",
            upg_str,
        )

    # Docked fleet
    for owned in captain.fleet:
        s = owned.ship
        cargo_used = sum(c.quantity for c in owned.cargo)
        eff_cargo = resolve_cargo_capacity(s, _UPG)
        upg_str = str(len(s.upgrades)) if s.upgrades else "[dim]-[/dim]"
        table.add_row(
            s.name,
            s.template_id.replace("_", " ").title(),
            f"{s.hull}/{s.hull_max}",
            f"{cargo_used}/{eff_cargo}",
            str(s.crew),
            owned.docked_port_id.replace("_", " ").title(),
            upg_str,
        )

    from portlight.engine.models import max_fleet_size
    limit = max_fleet_size(captain.standing.commercial_trust)
    total = 1 + len(captain.fleet)
    footer = f"Fleet: {total}/{limit} ships"

    return Panel(table, subtitle=footer, border_style="blue")


def crew_roster_view(ship: "Ship | None") -> Panel:
    """Show crew breakdown by role with wages and effects."""
    if not ship:
        return Panel("[dim]No ship[/dim]", title="Crew Roster")

    from portlight.content.crew_roles import ROLE_SPECS, get_role_count
    from portlight.engine.models import CrewRole

    table = Table(title="Crew Roster", show_header=True, header_style="bold")
    table.add_column("Role", style="bold")
    table.add_column("Count", justify="right")
    table.add_column("Wage/day", justify="right")
    table.add_column("Limit", justify="right")
    table.add_column("Effect")

    for role in CrewRole:
        spec = ROLE_SPECS[role]
        count = get_role_count(ship.roster, role)
        limit_str = str(spec.max_per_ship) if spec.max_per_ship else "[dim]none[/dim]"
        count_style = "bold green" if count > 0 else "dim"
        table.add_row(
            spec.name,
            f"[{count_style}]{count}[/{count_style}]",
            fmt.silver(spec.wage),
            limit_str,
            spec.description,
        )

    # Named officers section
    if ship.officers:
        table.add_section()
        table.add_row("[bold]Officers[/bold]", "", "", "", "")
        for officer in ship.officers:
            table.add_row(
                f"  {officer.name}",
                officer.role.value.title(),
                f"[dim]{officer.trait}[/dim]",
                f"[dim]{officer.experience}d exp[/dim]",
                f"[dim]from {officer.origin_port}[/dim]" if officer.origin_port else "",
            )

    from portlight.content.ships import SHIPS as _SHIPS_CAT
    from portlight.engine.ship_stats import compute_daily_wages
    _tmpl = _SHIPS_CAT.get(ship.template_id)
    _ship_wage = _tmpl.daily_wage if _tmpl else 1
    total_wage = compute_daily_wages(ship.roster, _ship_wage)
    morale_str = f"  |  Morale: {ship.morale}/100"
    footer = f"Total crew: {ship.crew}/{ship.crew_max}  |  Daily wages: {total_wage} silver{morale_str}"

    return Panel(table, subtitle=footer, border_style="cyan")


def shipyard_view(captain: "Captain") -> Panel:
    """Ship comparison panel for upgrade decisions."""
    current = captain.ship

    table = Table(title="Shipyard", show_header=True, header_style="bold")
    table.add_column("Ship", style="bold")
    table.add_column("Class")
    table.add_column("Cargo", justify="right")
    table.add_column("Speed", justify="right")
    table.add_column("Hull", justify="right")
    table.add_column("Crew", justify="right")
    table.add_column("Wage/day", justify="right")
    table.add_column("Storm Res.", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Status")

    for template in SHIPS.values():
        is_current = current and current.template_id == template.id
        status = "[bold cyan]* Current[/bold cyan]" if is_current else fmt.upgrade_distance(captain.silver, template.price)

        # Comparison arrows
        cargo_cmp = _compare(template.cargo_capacity, current.cargo_capacity if current else 0)
        speed_cmp = _compare(template.speed, current.speed if current else 0)
        hull_cmp = _compare(template.hull_max, current.hull_max if current else 0)

        # Daily wage cost (wage * crew_min is the minimum operating cost)
        wage_str = f"{template.daily_wage * template.crew_min}-{template.daily_wage * template.crew_max}"
        storm_str = f"{int(template.storm_resist * 100)}%" if template.storm_resist > 0 else "[dim]-[/dim]"

        table.add_row(
            template.name,
            template.ship_class.value.title(),
            f"{template.cargo_capacity} {cargo_cmp}",
            f"{template.speed} {speed_cmp}",
            f"{template.hull_max} {hull_cmp}",
            f"{template.crew_min}-{template.crew_max}",
            wage_str,
            storm_str,
            fmt.silver(template.price) if template.price > 0 else "[dim]-[/dim]",
            status,
        )

    return Panel(table, border_style="yellow")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def upgrade_catalog_view(captain: "Captain") -> Panel:
    """Show available upgrades with bonuses and prices."""
    from portlight.content.upgrades import UPGRADES as _UPGRADES_CAT

    ship = captain.ship
    table = Table(title="Ship Upgrades", show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Name", style="bold")
    table.add_column("Category")
    table.add_column("Price", justify="right")
    table.add_column("Effects")
    table.add_column("Status")

    installed_ids = {inst.upgrade_id for inst in (ship.upgrades if ship else [])}
    slots_used = len(ship.upgrades) if ship else 0
    slots_max = ship.upgrade_slots if ship else 0

    for uid, tmpl in sorted(_UPGRADES_CAT.items(), key=lambda x: (x[1].category.value, x[1].price)):
        effects: list[str] = []
        if tmpl.speed_bonus:
            effects.append(f"+{tmpl.speed_bonus} speed")
        if tmpl.speed_penalty:
            effects.append(f"-{tmpl.speed_penalty} speed")
        if tmpl.hull_max_bonus:
            effects.append(f"+{tmpl.hull_max_bonus} hull")
        if tmpl.cargo_bonus:
            effects.append(f"+{tmpl.cargo_bonus} cargo")
        if tmpl.cannon_bonus:
            effects.append(f"+{tmpl.cannon_bonus} cannons")
        if tmpl.maneuver_bonus:
            effects.append(f"+{tmpl.maneuver_bonus} maneuver")
        if tmpl.storm_resist_bonus:
            effects.append(f"+{int(tmpl.storm_resist_bonus * 100)}% storm")
        if tmpl.crew_max_bonus:
            effects.append(f"+{tmpl.crew_max_bonus} crew")
        if tmpl.special:
            effects.append(f"[italic]{tmpl.special}[/italic]")

        if uid in installed_ids:
            status = "[bold cyan]Installed[/bold cyan]"
        elif slots_used >= slots_max:
            status = "[dim]No slots[/dim]"
        elif tmpl.price > captain.silver:
            need = tmpl.price - captain.silver
            status = f"[red]Need {need} more[/red]"
        else:
            status = "[green]Available[/green]"

        table.add_row(
            uid,
            tmpl.name,
            tmpl.category.value.replace("_", " ").title(),
            fmt.silver(tmpl.price),
            ", ".join(effects) if effects else "[dim]-[/dim]",
            status,
        )

    footer = f"Slots: {slots_used}/{slots_max}"
    if ship:
        footer += f"  |  Ship: {ship.name}"

    return Panel(table, subtitle=footer, border_style="yellow")


def _routes_from(routes: list["Route"], port_id: str | None) -> list["Route"]:
    if port_id is None:
        return []
    return [r for r in routes if r.port_a == port_id or r.port_b == port_id]


def _next_upgrade(ship: "Ship | None", silver: int) -> "ShipTemplate | None":
    """Find the cheapest ship that costs more than the current one (actual upgrade)."""
    if ship is None:
        return None
    current = SHIPS.get(ship.template_id)
    current_price = current.price if current else 0
    for template in sorted(SHIPS.values(), key=lambda s: s.price):
        if template.id != ship.template_id and template.price > current_price:
            return template
    return None


def _compare(new: float, current: float) -> str:
    if new > current:
        return "[green]+[/green]"
    elif new < current:
        return "[red]-[/red]"
    return ""


def _crew_min(ship: "Ship") -> int:
    """Get crew_min from template."""
    template = SHIPS.get(ship.template_id)
    return template.crew_min if template else 1


def _event_icon(event_type: str) -> str:
    icons = {
        "storm": "[red]*[/red]",
        "pirates": "[red]![/red]",
        "inspection": "[yellow]?[/yellow]",
        "favorable_wind": "[green]>[/green]",
        "calm_seas": "[cyan]~[/cyan]",
        "provisions_spoiled": "[red]x[/red]",
        "nothing": "[dim].[/dim]",
    }
    return icons.get(event_type, ".")


# ---------------------------------------------------------------------------
# Contract board view - available offers
# ---------------------------------------------------------------------------

def contracts_view(board: "ContractBoard", day: int) -> Panel:
    """Contract board: available offers with requirements and rewards."""
    if not board.offers:
        return Panel("[dim]No contract offers available. Check back tomorrow or try another port.[/dim]",
                     title="[bold]Contract Board[/bold]", border_style="yellow")

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Good")
    table.add_column("Qty", justify="right")
    table.add_column("Reward", justify="right")
    table.add_column("Deadline", justify="right")
    table.add_column("Trust")
    table.add_column("Reason")

    for offer in board.offers:
        good = GOODS.get(offer.good_id)
        good_name = good.name if good else offer.good_id
        days_left = offer.deadline_day - day
        deadline_style = "red" if days_left < 10 else "yellow" if days_left < 20 else "green"
        reward_str = f"{offer.reward_silver}"
        if offer.bonus_reward > 0:
            reward_str += f" [green](+{offer.bonus_reward})[/green]"

        # Trust requirement
        trust_str = offer.required_trust_tier
        if offer.required_standing > 0:
            trust_str += f" / standing {offer.required_standing}+"

        table.add_row(
            offer.id[:8],
            offer.title,
            good_name,
            str(offer.quantity),
            reward_str,
            f"[{deadline_style}]{days_left}d[/{deadline_style}]",
            trust_str,
            offer.offer_reason,
        )

    active_count = len(board.active)
    footer = f"\nActive contracts: {active_count}/3"
    if active_count >= 3:
        footer += " [red](max reached)[/red]"

    return Panel(Group(table, Text.from_markup(footer)),
                 title="[bold]Contract Board[/bold]", border_style="yellow")


def _estimate_sail_days(world: "WorldState | None", dest_port_id: str) -> int | None:
    """Estimate sail days from current position to destination, or None if unknown."""
    if not world or not world.voyage:
        return None
    from portlight.engine.models import VoyageStatus
    if world.voyage.status != VoyageStatus.IN_PORT:
        return None  # already at sea, not useful
    current_port_id = world.voyage.destination_id
    if current_port_id == dest_port_id:
        return 0  # already there
    # Find route distance
    speed = world.captain.ship.speed if world.captain.ship else 6
    for route in world.routes:
        if (route.port_a == current_port_id and route.port_b == dest_port_id) or \
           (route.port_b == current_port_id and route.port_a == dest_port_id):
            return max(1, round(route.distance / speed))
    return None  # no direct route


# ---------------------------------------------------------------------------
# Obligations view - active contracts
# ---------------------------------------------------------------------------

def obligations_view(
    board: "ContractBoard",
    day: int,
    world: "WorldState | None" = None,
) -> Panel:
    """Active contract obligations: progress, deadlines, rewards, sail-time context."""
    if not board.active:
        return Panel("[dim]No active contracts. Accept offers from the contract board.[/dim]",
                     title="[bold]Obligations[/bold]", border_style="magenta")

    table = Table(show_header=True, header_style="bold")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="bold")
    table.add_column("Good")
    table.add_column("Progress", justify="center")
    table.add_column("Reward", justify="right")
    table.add_column("Deadline", justify="right")
    table.add_column("Source")

    for contract in board.active:
        good = GOODS.get(contract.good_id)
        good_name = good.name if good else contract.good_id
        days_left = contract.deadline_day - day
        deadline_style = "red" if days_left < 5 else "yellow" if days_left < 10 else "green"

        # Progress bar
        pct = contract.delivered_quantity / max(contract.required_quantity, 1)
        filled = int(pct * 10)
        bar = f"[cyan]{'#' * filled}{'-' * (10 - filled)}[/cyan] {contract.delivered_quantity}/{contract.required_quantity}"

        reward_str = f"{contract.reward_silver}"
        if contract.bonus_reward > 0:
            reward_str += f" [green](+{contract.bonus_reward})[/green]"

        source = ""
        if contract.source_region:
            source = f"from {contract.source_region}"
        if contract.source_port:
            source = f"from {contract.source_port}"

        # Deadline with sail-time context
        deadline_str = f"[{deadline_style}]{days_left}d left[/{deadline_style}]"
        sail_days = _estimate_sail_days(world, contract.destination_port_id)
        if sail_days is not None:
            dest = world.ports.get(contract.destination_port_id) if world else None
            dest_name = dest.name if dest else contract.destination_port_id
            deadline_str += f" [dim](~{sail_days}d sail to {dest_name})[/dim]"

        table.add_row(
            contract.offer_id[:8],
            contract.title,
            good_name,
            bar,
            reward_str,
            deadline_str,
            source if source else "[dim]-[/dim]",
        )

    # Completed summary
    if board.completed:
        recent = board.completed[-3:]
        footer_lines = ["\n[bold]Recent outcomes:[/bold]"]
        for outcome in recent:
            icon = "[green]+[/green]" if outcome.silver_delta > 0 else "[red]-[/red]"
            footer_lines.append(f"  {icon} {outcome.summary}")
        footer = "\n".join(footer_lines)
    else:
        footer = ""

    return Panel(Group(table, Text.from_markup(footer) if footer else Text("")),
                 title="[bold]Obligations[/bold]", border_style="magenta")


# ---------------------------------------------------------------------------
# Warehouse view - storage and staging
# ---------------------------------------------------------------------------

def warehouse_view(
    infra: "InfrastructureState",
    port_id: str | None,
    port_name: str | None = None,
) -> Panel:
    """Warehouse status: current port warehouse + all active warehouses summary."""
    from portlight.engine.infrastructure import warehouse_summary

    active_warehouses = warehouse_summary(infra)

    if not active_warehouses:
        return Panel(
            "[dim]No warehouses leased. Use [bold]portlight warehouse lease <tier>[/bold] to open one.[/dim]",
            title="[bold]Warehouses[/bold]", border_style="yellow",
        )

    lines: list[str] = []

    # Current port warehouse detail
    current = None
    if port_id:
        current = next((w for w in active_warehouses if w.port_id == port_id), None)

    if current:
        label = port_name or current.port_id
        lines.append(f"[bold]{label}[/bold] — {current.tier.value.title()} ({current.used_capacity}/{current.capacity})")
        if current.inventory:
            table = Table(show_header=True, header_style="bold", padding=(0, 1))
            table.add_column("Good", style="bold")
            table.add_column("Qty", justify="right")
            table.add_column("Source Port")
            table.add_column("Source Region")

            for lot in current.inventory:
                good = GOODS.get(lot.good_id)
                good_name = good.name if good else lot.good_id
                table.add_row(good_name, str(lot.quantity), lot.acquired_port, lot.acquired_region)

            # We'll return a compound view with the table
            capacity_bar = _warehouse_bar(current.used_capacity, current.capacity)
            lines.append(f"Capacity: {capacity_bar}")
            lines.append(f"Upkeep: {current.upkeep_per_day}/day")
            lines.append("")

            # Summary of other warehouses
            others = [w for w in active_warehouses if w.port_id != port_id]
            if others:
                lines.append("[bold]Other warehouses:[/bold]")
                for w in others:
                    lines.append(f"  {w.port_id}: {w.tier.value.title()} ({w.used_capacity}/{w.capacity})")

            return Panel(
                Group(Text.from_markup("\n".join(lines)), table),
                title="[bold]Warehouses[/bold]", border_style="yellow",
            )
        else:
            lines.append("[dim]  Empty[/dim]")
            lines.append(f"  Capacity: {current.capacity} | Upkeep: {current.upkeep_per_day}/day")

    # All warehouses summary
    if not current or len(active_warehouses) > 1:
        if current:
            lines.append("")
            lines.append("[bold]Other warehouses:[/bold]")
        for w in active_warehouses:
            if w.port_id == port_id and current:
                continue
            goods_str = ", ".join(
                f"{lot.quantity}x {lot.good_id}" for lot in w.inventory
            ) if w.inventory else "empty"
            lines.append(f"  {w.port_id}: {w.tier.value.title()} ({w.used_capacity}/{w.capacity}) — {goods_str}")

    return Panel("\n".join(lines), title="[bold]Warehouses[/bold]", border_style="yellow")


def warehouse_lease_options(port_id: str) -> Panel:
    """Show available warehouse tiers at a port."""
    from portlight.content.infrastructure import available_tiers

    tiers = available_tiers(port_id)
    if not tiers:
        return Panel("[dim]No warehouse facilities at this port.[/dim]",
                     title="[bold]Warehouse Leasing[/bold]", border_style="yellow")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Tier", style="bold")
    table.add_column("Name")
    table.add_column("Capacity", justify="right")
    table.add_column("Lease Cost", justify="right")
    table.add_column("Upkeep/day", justify="right")
    table.add_column("Description")

    for spec in tiers:
        table.add_row(
            spec.tier.value,
            spec.name,
            str(spec.capacity),
            fmt.silver(spec.lease_cost),
            fmt.silver(spec.upkeep_per_day),
            spec.description,
        )

    return Panel(table, title="[bold]Warehouse Leasing[/bold]", border_style="yellow")


def _warehouse_bar(used: int, capacity: int) -> str:
    pct = int(used / max(capacity, 1) * 10)
    filled = min(10, pct)
    return f"[cyan]{'#' * filled}{'-' * (10 - filled)}[/cyan] {used}/{capacity}"


# ---------------------------------------------------------------------------
# Broker offices
# ---------------------------------------------------------------------------

def offices_view(infra: "InfrastructureState") -> Panel:
    """Show all broker offices and their status."""
    from portlight.engine.infrastructure import BrokerTier
    from portlight.content.infrastructure import get_broker_spec

    active_brokers = [b for b in infra.brokers if b.active and b.tier != BrokerTier.NONE]

    if not active_brokers:
        return Panel(
            "[dim]No broker offices established.\n"
            "Use [bold]portlight office open <region>[/bold] to open one.[/dim]",
            title="[bold]Broker Offices[/bold]",
            border_style="blue",
        )

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Region")
    table.add_column("Tier")
    table.add_column("Upkeep")
    table.add_column("Board Quality")
    table.add_column("Market Signal")
    table.add_column("Trade Terms")

    for broker in sorted(active_brokers, key=lambda b: b.region):
        spec = get_broker_spec(broker.region, broker.tier)
        if not spec:
            continue
        quality_str = f"+{int((spec.board_quality_bonus - 1) * 100)}%"
        signal_str = f"+{int(spec.market_signal_bonus * 100)}%"
        terms_str = f"-{int((1 - spec.trade_term_modifier) * 100)}% spread"
        table.add_row(
            broker.region,
            f"[cyan]{spec.name}[/cyan]",
            f"{fmt.silver(spec.upkeep_per_day)}/day",
            f"[green]{quality_str}[/green]",
            f"[green]{signal_str}[/green]",
            f"[green]{terms_str}[/green]",
        )

    return Panel(table, title="[bold]Broker Offices[/bold]", border_style="blue")


def office_options_view(region: str, current_tier: str) -> Panel:
    """Show broker office tiers available in a region."""
    from portlight.content.infrastructure import available_broker_tiers

    tiers = available_broker_tiers(region)

    if not tiers:
        return Panel(
            f"[dim]No broker offices available in {region}.[/dim]",
            title="[bold]Broker Offices[/bold]",
            border_style="blue",
        )

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Tier")
    table.add_column("Cost")
    table.add_column("Upkeep")
    table.add_column("Board Quality")
    table.add_column("Description")

    for spec in tiers:
        is_current = spec.tier.value == current_tier
        marker = " [green](current)[/green]" if is_current else ""
        quality_str = f"+{int((spec.board_quality_bonus - 1) * 100)}%"
        table.add_row(
            f"[cyan]{spec.tier.value}[/cyan]{marker}",
            fmt.silver(spec.purchase_cost),
            f"{fmt.silver(spec.upkeep_per_day)}/day",
            f"[green]{quality_str}[/green]",
            spec.description,
        )

    return Panel(table, title=f"[bold]Broker Offices — {region}[/bold]", border_style="blue")


# ---------------------------------------------------------------------------
# Licenses
# ---------------------------------------------------------------------------

def licenses_view(infra: "InfrastructureState", rep: "ReputationState") -> Panel:
    """Show all licenses — owned and available."""
    from portlight.content.infrastructure import LICENSE_CATALOG
    from portlight.engine.infrastructure import check_license_eligibility, has_license

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("License")
    table.add_column("Region")
    table.add_column("Cost")
    table.add_column("Upkeep")
    table.add_column("Status")
    table.add_column("Effects")

    for spec in sorted(LICENSE_CATALOG.values(), key=lambda s: s.purchase_cost):
        owned = has_license(infra, spec.id)
        if owned:
            status = "[bold green]ACTIVE[/bold green]"
        else:
            err = check_license_eligibility(infra, spec, rep)
            if err:
                status = f"[red]{err}[/red]"
            else:
                status = "[yellow]Available[/yellow]"

        region = spec.region_scope or "Global"
        effects_parts = []
        for key, val in spec.effects.items():
            if key == "luxury_access":
                effects_parts.append("Luxury access")
            elif key == "customs_mult":
                effects_parts.append(f"Customs -{int((1 - val) * 100)}%")
            elif key == "lawful_board_mult":
                effects_parts.append(f"Lawful +{int((val - 1) * 100)}%")
            elif key == "premium_offer_mult":
                effects_parts.append(f"Premium +{int((val - 1) * 100)}%")
        effects_str = ", ".join(effects_parts) if effects_parts else "-"

        table.add_row(
            f"[cyan]{spec.name}[/cyan]",
            region,
            fmt.silver(spec.purchase_cost),
            f"{fmt.silver(spec.upkeep_per_day)}/day",
            status,
            effects_str,
        )

    return Panel(table, title="[bold]Licenses & Charters[/bold]", border_style="magenta")


# ---------------------------------------------------------------------------
# Insurance
# ---------------------------------------------------------------------------

def insurance_view(infra: "InfrastructureState", heat: int = 0) -> Panel:
    """Show available policies, active policies, and recent claims."""
    from portlight.content.infrastructure import available_policies
    from portlight.engine.infrastructure import get_active_policies

    parts = []

    # Active policies
    active = get_active_policies(infra)
    if active:
        active_table = Table(show_header=True, header_style="bold", expand=True)
        active_table.add_column("Policy")
        active_table.add_column("Coverage")
        active_table.add_column("Cap")
        active_table.add_column("Paid Out")
        active_table.add_column("Scope")

        for p in active:
            from portlight.content.infrastructure import get_policy_spec
            spec = get_policy_spec(p.spec_id)
            name = spec.name if spec else p.spec_id
            scope_desc = p.scope.value
            if p.target_id:
                scope_desc += f" ({p.target_id[:8]})"
            elif p.voyage_destination:
                scope_desc += f" -> {p.voyage_destination}"
            remaining = p.coverage_cap - p.total_paid_out
            active_table.add_row(
                f"[green]{name}[/green]",
                f"{int(p.coverage_pct * 100)}%",
                f"{fmt.silver(remaining)} left",
                fmt.silver(p.total_paid_out),
                scope_desc,
            )
        parts.append(active_table)
    else:
        parts.append(Text.from_markup("[dim]No active policies.[/dim]\n"))

    # Available policies
    avail_table = Table(show_header=True, header_style="bold", expand=True)
    avail_table.add_column("ID")
    avail_table.add_column("Policy")
    avail_table.add_column("Premium")
    avail_table.add_column("Coverage")
    avail_table.add_column("Cap")
    avail_table.add_column("Scope")
    avail_table.add_column("Exclusions")

    for spec in available_policies():
        # Compute heat-adjusted premium
        heat_surcharge = max(0, heat) * spec.heat_premium_mult
        adj_premium = int(spec.premium * (1.0 + heat_surcharge))
        premium_str = fmt.silver(adj_premium)
        if adj_premium > spec.premium:
            premium_str += f" [dim]({fmt.silver(spec.premium)} base)[/dim]"

        blocked = spec.heat_max is not None and heat > spec.heat_max
        if blocked:
            premium_str = "[red]Blocked (heat)[/red]"

        excl = ", ".join(spec.exclusions) if spec.exclusions else "-"
        avail_table.add_row(
            f"[dim]{spec.id}[/dim]",
            f"[cyan]{spec.name}[/cyan]",
            premium_str,
            f"{int(spec.coverage_pct * 100)}%",
            fmt.silver(spec.coverage_cap),
            spec.scope.value,
            excl,
        )
    parts.append(avail_table)

    # Recent claims
    recent_claims = infra.claims[-5:] if infra.claims else []
    if recent_claims:
        claims_table = Table(show_header=True, header_style="bold", expand=True)
        claims_table.add_column("Day")
        claims_table.add_column("Incident")
        claims_table.add_column("Loss")
        claims_table.add_column("Payout")
        claims_table.add_column("Status")

        for c in reversed(recent_claims):
            if c.denied:
                status = f"[red]Denied: {c.denial_reason}[/red]"
            elif c.payout > 0:
                status = "[green]Paid[/green]"
            else:
                status = "[dim]No payout[/dim]"
            claims_table.add_row(
                str(c.day),
                c.incident_type,
                fmt.silver(c.loss_value),
                fmt.silver(c.payout),
                status,
            )
        parts.append(Text.from_markup("\n[bold]Recent Claims[/bold]"))
        parts.append(claims_table)

    return Panel(Group(*parts), title="[bold]Insurance[/bold]", border_style="green")


# ---------------------------------------------------------------------------
# Credit
# ---------------------------------------------------------------------------

def credit_view(infra: "InfrastructureState", rep: "ReputationState") -> Panel:
    """Show credit line status and available tiers."""
    from portlight.engine.infrastructure import _ensure_credit
    from portlight.content.infrastructure import CREDIT_TIERS, get_credit_spec
    from portlight.engine.infrastructure import check_credit_eligibility

    credit = _ensure_credit(infra)
    parts = []

    if credit.active:
        spec = get_credit_spec(credit.tier)
        tier_name = spec.name if spec else credit.tier.value

        status_table = Table(show_header=False, expand=True, box=None)
        status_table.add_column("Label", style="bold")
        status_table.add_column("Value")

        available = credit.credit_limit - credit.outstanding
        total_owed = credit.outstanding + credit.interest_accrued

        status_table.add_row("Credit Line", f"[cyan]{tier_name}[/cyan]")
        status_table.add_row("Limit", fmt.silver(credit.credit_limit))
        status_table.add_row("Available", f"[green]{fmt.silver(available)}[/green]")
        status_table.add_row("Outstanding", fmt.silver(credit.outstanding) if credit.outstanding > 0 else "[dim]0[/dim]")
        if credit.interest_accrued > 0:
            status_table.add_row("Interest Owed", f"[yellow]{fmt.silver(credit.interest_accrued)}[/yellow]")
        status_table.add_row("Total Owed", f"[bold]{fmt.silver(total_owed)}[/bold]" if total_owed > 0 else "[dim]0[/dim]")
        if credit.next_due_day > 0 and total_owed > 0:
            status_table.add_row("Next Due", f"Day {credit.next_due_day}")
        if spec:
            status_table.add_row("Interest Rate", f"{int(spec.interest_rate * 100)}% per {spec.interest_period} days")
        if credit.defaults > 0:
            status_table.add_row("Defaults", f"[red]{credit.defaults}[/red]")
        status_table.add_row("Lifetime Borrowed", fmt.silver(credit.total_borrowed))
        status_table.add_row("Lifetime Repaid", fmt.silver(credit.total_repaid))

        parts.append(status_table)
    else:
        if credit.defaults >= 3:
            parts.append(Text.from_markup("[red]Credit line frozen -- too many defaults.[/red]\n"))
        else:
            parts.append(Text.from_markup("[dim]No credit line established.[/dim]\n"))

    # Available tiers
    tier_table = Table(show_header=True, header_style="bold", expand=True)
    tier_table.add_column("Tier")
    tier_table.add_column("Limit")
    tier_table.add_column("Rate")
    tier_table.add_column("Status")
    tier_table.add_column("Description")

    for spec in sorted(CREDIT_TIERS.values(), key=lambda s: s.credit_limit):
        is_current = credit.active and credit.tier == spec.tier
        if is_current:
            status = "[bold green]ACTIVE[/bold green]"
        else:
            err = check_credit_eligibility(infra, spec, rep)
            if err:
                status = f"[red]{err}[/red]"
            else:
                status = "[yellow]Available[/yellow]"

        rate_str = f"{int(spec.interest_rate * 100)}% / {spec.interest_period}d"
        tier_table.add_row(
            f"[cyan]{spec.name}[/cyan]",
            fmt.silver(spec.credit_limit),
            rate_str,
            status,
            spec.description[:60] + "..." if len(spec.description) > 60 else spec.description,
        )

    parts.append(Text("\n"))
    parts.append(tier_table)

    return Panel(Group(*parts), title="[bold]Credit[/bold]", border_style="yellow")


# ---------------------------------------------------------------------------
# Campaign milestones
# ---------------------------------------------------------------------------

def milestones_view(
    campaign: "CampaignState",
    snap: "SessionSnapshot",
) -> Panel:
    """Show completed milestones, career profile, and victory progress."""
    from portlight.engine.campaign import (
        MilestoneFamily,
        compute_career_profile,
        compute_victory_progress,
    )
    from portlight.content.campaign import MILESTONE_SPECS

    parts = []

    # --- Completed milestones by family ---
    completed_ids = {c.milestone_id for c in campaign.completed}
    completion_map = {c.milestone_id: c for c in campaign.completed}

    families_with_completions = {}
    for spec in MILESTONE_SPECS:
        if spec.id in completed_ids:
            families_with_completions.setdefault(spec.family, []).append(spec)

    if families_with_completions:
        ms_table = Table(show_header=True, header_style="bold", expand=True)
        ms_table.add_column("Family")
        ms_table.add_column("Milestone")
        ms_table.add_column("Day")
        ms_table.add_column("Evidence")

        for family in MilestoneFamily:
            specs = families_with_completions.get(family, [])
            for spec in specs:
                comp = completion_map.get(spec.id)
                family_label = family.value.replace("_", " ").title()
                ms_table.add_row(
                    f"[dim]{family_label}[/dim]",
                    f"[green]{spec.name}[/green]",
                    str(comp.completed_day) if comp else "",
                    comp.evidence if comp else "",
                )

        parts.append(ms_table)
        parts.append(Text.from_markup(f"\n[bold]{len(completed_ids)}[/bold] of {len(MILESTONE_SPECS)} milestones completed.\n"))
    else:
        parts.append(Text.from_markup("[dim]No milestones completed yet.[/dim]\n"))

    # --- In-progress milestones (not yet completed) ---
    pending = [s for s in MILESTONE_SPECS if s.id not in completed_ids]
    if pending and len(pending) < len(MILESTONE_SPECS):  # only show if some progress
        parts.append(Text.from_markup("[bold]Next milestones:[/bold]"))
        # Show up to 5 from different families
        shown_families: set[str] = set()
        shown = 0
        for spec in pending:
            if shown >= 5:
                break
            if spec.family.value in shown_families:
                continue
            shown_families.add(spec.family.value)
            family_label = spec.family.value.replace("_", " ").title()
            parts.append(Text.from_markup(f"  [dim]{family_label}:[/dim] {spec.name} -- {spec.description}"))
            shown += 1
        parts.append(Text(""))

    # --- Career profile ---
    profile = compute_career_profile(snap)
    if profile.primary and profile.primary.combined_score > 0:
        parts.append(Text.from_markup("[bold]Career Profile[/bold]"))

        # Primary identity
        p = profile.primary
        bar_len = min(int(p.combined_score / 4), 20)
        bar = "#" * bar_len
        ev = ", ".join(p.evidence[:3]) if p.evidence else ""
        parts.append(Text.from_markup(f"  [bold cyan]{p.tag}[/bold cyan] {bar} {p.combined_score:.0f}  \\[{p.confidence.value}]"))
        if ev:
            parts.append(Text(f"    Primary: {ev}"))

        # Secondary traits (up to 2)
        for s in profile.secondaries:
            bar_len = min(int(s.combined_score / 4), 20)
            bar = "#" * bar_len
            ev = ", ".join(s.evidence[:2]) if s.evidence else ""
            parts.append(Text.from_markup(f"  [dim]{s.tag}[/dim] {bar} {s.combined_score:.0f}  \\[{s.confidence.value}]"))
            if ev:
                parts.append(Text(f"    Secondary: {ev}"))

        # Emerging direction
        if profile.emerging:
            e = profile.emerging
            ev = ", ".join(e.evidence[:2]) if e.evidence else ""
            parts.append(Text.from_markup(f"  [italic yellow]{e.tag}[/italic yellow] ^ {e.recent_score:.0f} recent  \\[{e.confidence.value}]"))
            if ev:
                parts.append(Text(f"    Emerging: {ev}"))

        parts.append(Text(""))

    # --- Victory progress ---
    victory = compute_victory_progress(snap)
    parts.append(Text.from_markup("[bold]Victory Paths[/bold]"))

    for i, path in enumerate(victory):
        if path.is_complete:
            label = "[bold green]VICTORY[/bold green]"
            style = "green"
        elif path.is_active_candidate:
            label = f"[yellow]{path.met_count}/{path.total_count}[/yellow]"
            style = "yellow"
        elif path.met_count > 0:
            label = f"[dim]{path.met_count}/{path.total_count}[/dim]"
            style = "dim"
        else:
            label = f"[dim]0/{path.total_count}[/dim]"
            style = "dim"

        rank = "Strongest" if i == 0 and path.candidate_strength > 0 else (
            "Secondary" if i == 1 and path.is_active_candidate else ""
        )
        rank_text = f"  ({rank})" if rank else ""
        parts.append(Text.from_markup(f"  [{style}]{path.name}[/{style}] -- {label}  strength {path.candidate_strength:.0f}{rank_text}"))

        # Completion summary
        if path.is_complete and path.completion_summary:
            day_text = f" (day {path.completion_day})" if path.completion_day > 0 else ""
            parts.append(Text.from_markup(f"    [green italic]{path.completion_summary}[/green italic]{day_text}"))

        # Show met requirements briefly
        met = path.requirements_met
        if met and not path.is_complete:
            met_names = ", ".join(r.description for r in met[:3])
            if len(met) > 3:
                met_names += f" +{len(met) - 3} more"
            parts.append(Text.from_markup(f"    [green]Met:[/green] {met_names}"))

        # Show blockers prominently
        blocked = path.requirements_blocked
        for req in blocked:
            detail = f" ({req.detail})" if req.detail else ""
            action = f" -> {req.action}" if req.action else ""
            parts.append(Text.from_markup(f"    [bold red]Blocked:[/bold red] {req.description}{detail}{action}"))

        # Show missing requirements with actions
        missing = path.requirements_missing
        for req in missing[:3]:
            action = f" -> {req.action}" if req.action else ""
            detail = f" ({req.detail})" if req.detail else ""
            parts.append(Text.from_markup(f"    [red]Missing:[/red] {req.description}{detail}{action}"))
        if len(missing) > 3:
            parts.append(Text.from_markup(f"    [dim]+{len(missing) - 3} more requirements[/dim]"))

    return Panel(Group(*parts), title="[bold]Merchant Career Ledger[/bold]", border_style="bright_blue")


# ---------------------------------------------------------------------------
# Captain selection views — interactive character creation
# ---------------------------------------------------------------------------

_SHIP_SILHOUETTES: dict[str, str] = {
    "sloop": "   __|__\n__|     |__\n|___________|",
    "cutter": "  ___|___\n_|       |_\n|___________|~",
}


def _port_name(port_id: str) -> str:
    """Convert port_id to display name, using real port data when available."""
    from portlight.content.ports import PORTS
    port = PORTS.get(port_id)
    if port:
        return port.name
    return port_id.replace("_", " ").title()


def captain_roster_view(
    templates: "dict",
    order: list,
    quotes: dict,
    colors: dict,
    console_width: int = 80,
) -> Group:
    """3x3 grid of compact captain cards for the selection screen."""

    cards: list[Panel] = []
    for idx, ct in enumerate(order):
        tmpl: CaptainTemplate = templates[ct]
        num = idx + 1
        quote = quotes.get(ct, "")
        color = colors.get(ct, "white")
        diff = fmt.difficulty_tag(tmpl.starting_silver)
        ship_tmpl = SHIPS.get(tmpl.starting_ship_id)
        ship_name = ship_tmpl.name if ship_tmpl else tmpl.starting_ship_id

        # Card body
        lines = []
        lines.append(f"[dim]{tmpl.title}[/dim]")
        lines.append(f"{_port_name(tmpl.home_port_id)} - [yellow]{tmpl.starting_silver}s[/yellow]")
        lines.append(f"{ship_name} - {diff}")
        lines.append("")
        # Signature strength (first, truncated for card)
        if tmpl.strengths:
            lines.append(f"[green]+[/green] {tmpl.strengths[0]}")
        # Signature weakness (first, truncated for card)
        if tmpl.weaknesses:
            lines.append(f"[red]-[/red] {tmpl.weaknesses[0]}")
        lines.append("")
        # Quote
        if quote:
            lines.append(f'[italic dim]"{quote}"[/italic dim]')

        card = Panel(
            "\n".join(lines),
            title=f"[bold {color}]{num} - {tmpl.name}[/bold {color}]",
            border_style=color,
            width=28,
            padding=(0, 1),
        )
        cards.append(card)

    # Determine column count based on terminal width
    if console_width >= 88:
        col_count = 3
    elif console_width >= 60:
        col_count = 2
    else:
        col_count = 1

    # Build rows manually for clean alignment
    rows = []
    for i in range(0, len(cards), col_count):
        row_cards = cards[i:i + col_count]
        rows.append(Columns(row_cards, equal=True, expand=False))

    header = Text.from_markup(
        "\n"
        "  [bold]===================================================[/bold]\n"
        "  [bold]      Choose Your Captain[/bold]\n"
        "  [dim]      Who will you become on the open sea?[/dim]\n"
        "  [bold]===================================================[/bold]\n"
    )

    footer = Text.from_markup(
        "\n  [dim]Enter a number[/dim] [bold](1-9)[/bold] [dim]to learn more,"
        " or[/dim] [bold]0[/bold] [dim]for Custom Captain[/dim]\n"
    )

    return Group(header, *rows, footer)


def captain_spotlight_view(
    template: "CaptainTemplate",
    index: int,
    total: int,
    color: str = "blue",
) -> Panel:
    """Full detail view for a single captain during selection."""
    ship_tmpl = SHIPS.get(template.starting_ship_id)
    ship_name = ship_tmpl.name if ship_tmpl else template.starting_ship_id
    diff = fmt.difficulty_tag(template.starting_silver)

    lines: list[str] = []

    # Backstory + ship silhouette
    lines.append(f"[italic]{template.backstory}[/italic]")
    lines.append("")

    # Ship silhouette
    ship_class = template.starting_ship_id.split("_")[0] if "_" in template.starting_ship_id else "sloop"
    # Map ship IDs to silhouette keys
    if "cutter" in template.starting_ship_id:
        ship_class = "cutter"
    else:
        ship_class = "sloop"
    silhouette = _SHIP_SILHOUETTES.get(ship_class, "")
    if silhouette:
        lines.append(f"[dim]{silhouette}[/dim]")
        lines.append("")

    # Starting position
    lines.append("[bold]Starting Position[/bold]")
    lines.append(f"  Silver:     [yellow]{template.starting_silver:,}[/yellow]     Difficulty: {diff}")
    lines.append(f"  Ship:       {ship_name} (cargo {ship_tmpl.cargo_capacity}, speed {ship_tmpl.speed})" if ship_tmpl else f"  Ship:       {ship_name}")
    lines.append(f"  Home:       {_port_name(template.home_port_id)}, {template.home_region}")
    lines.append(f"  Provisions: {template.starting_provisions} days")
    lines.append("")

    # Trade profile
    p = template.pricing
    lines.append("[bold]Trade Profile[/bold]")
    lines.append(f"  Buy prices:    {fmt.modifier_str(p.buy_price_mult, invert=True)}")
    lines.append(f"  Sell prices:   {fmt.modifier_str(p.sell_price_mult)}")
    if p.luxury_sell_bonus > 0:
        lines.append(f"  Luxury bonus:  [green]+{int(p.luxury_sell_bonus * 100)}% on silk/spice/porcelain[/green]")
    lines.append(f"  Port fees:     {fmt.modifier_str(p.port_fee_mult, invert=True)}")
    lines.append("")

    # Voyage profile
    v = template.voyage
    lines.append("[bold]Voyage Profile[/bold]")
    lines.append(f"  Provision burn:  {fmt.modifier_str(v.provision_burn, invert=True)}")
    if v.speed_bonus > 0:
        lines.append(f"  Speed bonus:     [green]+{v.speed_bonus}[/green]")
    else:
        lines.append("  Speed bonus:     [dim]--[/dim]")
    if v.storm_resist_bonus > 0:
        lines.append(f"  Storm resist:    [green]+{int(v.storm_resist_bonus * 100)}%[/green]")
    lines.append(f"  Cargo damage:    {fmt.modifier_str(v.cargo_damage_mult, invert=True)}")
    lines.append("")

    # Inspection profile
    i = template.inspection
    lines.append("[bold]Inspection Profile[/bold]")
    lines.append(f"  Frequency:  {fmt.modifier_str(i.inspection_chance_mult, invert=True)}")
    if i.seizure_risk > 0:
        lines.append(f"  Seizure:    [red]{int(i.seizure_risk * 100)}% per inspection[/red]")
    else:
        lines.append("  Seizure:    [green]None[/green]")
    lines.append(f"  Fines:      {fmt.modifier_str(i.fine_mult, invert=True)}")
    lines.append("")

    # Reputation seed
    rs = template.reputation_seed
    lines.append("[bold]Starting Reputation[/bold]")
    lines.append(f"  Trust: {fmt.trust_tag(rs.commercial_trust)}     Heat: {fmt.heat_tag(rs.customs_heat)}")
    regions = []
    for region, val in [
        ("Mediterranean", rs.mediterranean),
        ("North Atlantic", rs.north_atlantic),
        ("West Africa", rs.west_africa),
        ("East Indies", rs.east_indies),
        ("South Seas", rs.south_seas),
    ]:
        if val != 0:
            color_r = "green" if val > 0 else "red"
            regions.append(f"{region}: [{color_r}]{val:+d}[/{color_r}]")
    if regions:
        lines.append(f"  Standing:   {', '.join(regions)}")
    if template.faction_alignment:
        factions = []
        for fac, val in template.faction_alignment.items():
            fc = "green" if val > 0 else "red"
            factions.append(f"{fac.replace('_', ' ').title()}: [{fc}]{val:+d}[/{fc}]")
        lines.append(f"  Factions:   {', '.join(factions)}")
    lines.append("")

    # Strengths / weaknesses
    lines.append("[bold green]Strengths[/bold green]")
    for s in template.strengths:
        lines.append(f"  [green]+[/green] {s}")
    lines.append("[bold red]Weaknesses[/bold red]")
    for w in template.weaknesses:
        lines.append(f"  [red]-[/red] {w}")

    title = f"[bold]{template.name}[/bold] — {template.title}  [{index}/{total}]"
    return Panel("\n".join(lines), title=title, border_style=color, padding=(1, 2))


def captain_confirm_view(
    name: str,
    template: "CaptainTemplate",
    color: str = "green",
) -> Panel:
    """Compact confirmation panel before starting the game."""
    ship_tmpl = SHIPS.get(template.starting_ship_id)
    ship_name = ship_tmpl.name if ship_tmpl else template.starting_ship_id

    lines = [
        "",
        f"  [bold]{name}[/bold] - {template.name}",
        f"  [dim]{template.title} of {_port_name(template.home_port_id)}[/dim]",
        "",
        f"  [yellow]{template.starting_silver}[/yellow] silver - {ship_name} - {template.home_region}",
        "",
    ]
    return Panel("\n".join(lines), title="[bold]Set Sail?[/bold]", border_style=color)


# ---------------------------------------------------------------------------
# World map - ASCII chart of ports, routes, regions
# ---------------------------------------------------------------------------

# Region display colors (Rich markup)
_REGION_COLORS: dict[str, str] = {
    "Mediterranean": "blue",
    "North Atlantic": "cyan",
    "West Africa": "yellow",
    "East Indies": "red",
    "South Seas": "green",
}

# Feature icons
_FEATURE_ICON: dict[str, str] = {
    "shipyard": "[S]",
    "black_market": "[B]",
    "safe_harbor": "[H]",
}

# Ship class -> route style
_ROUTE_STYLES: dict[str, tuple[str, str]] = {
    "sloop":       ("dim",    "."),
    "brigantine":  ("white",  "-"),
    "galleon":     ("yellow", "="),
    "man_of_war":  ("red",    "#"),
}


def _bresenham(x0: int, y0: int, x1: int, y1: int) -> list[tuple[int, int]]:
    """Integer Bresenham line between two points (excludes endpoints)."""
    points: list[tuple[int, int]] = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cx, cy = x0, y0
    while True:
        if (cx, cy) != (x0, y0) and (cx, cy) != (x1, y1):
            points.append((cx, cy))
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy
    return points


def world_map_view(
    world: "WorldState",
    player_port_id: str | None = None,
    show_routes: bool = False,
    region_filter: str | None = None,
) -> Panel:
    """Render the full world map as ASCII art.

    Grid: 100 columns x 36 rows (2x horizontal stretch for terminal aspect).
    Ports shown as colored markers with name labels.
    Routes drawn as lines between connected ports when show_routes=True.
    """
    from portlight.content.ports import PORTS
    from portlight.content.routes import ROUTES

    # --- Grid setup (adaptive to terminal width) ---
    import shutil
    term_w = shutil.get_terminal_size((120, 36)).columns
    MAP_W = max(60, min(100, term_w - 6))  # leave room for panel borders
    MAP_H = 36
    GAME_W = 50
    GAME_H = 36

    # Character grid: (char, style) per cell
    grid: list[list[tuple[str, str]]] = [
        [(".", "dim blue")] * MAP_W for _ in range(MAP_H)
    ]

    # Ocean texture - vary the fill slightly
    for y in range(MAP_H):
        for x in range(MAP_W):
            if (x + y) % 7 == 0:
                grid[y][x] = ("~", "dim blue")
            elif (x + y) % 11 == 0:
                grid[y][x] = (".", "dim blue")

    def game_to_grid(gx: int, gy: int) -> tuple[int, int]:
        """Convert game coords (50x36) to grid coords (100x36)."""
        mx = int(gx * (MAP_W - 2) / GAME_W) + 1
        my = int(gy * (MAP_H - 2) / GAME_H) + 1
        return (max(0, min(MAP_W - 1, mx)), max(0, min(MAP_H - 1, my)))

    # Filter ports by region if requested
    region_map: dict[str, str] = {
        "med": "Mediterranean", "mediterranean": "Mediterranean",
        "atl": "North Atlantic", "north_atlantic": "North Atlantic", "atlantic": "North Atlantic",
        "afr": "West Africa", "west_africa": "West Africa", "africa": "West Africa",
        "ind": "East Indies", "east_indies": "East Indies", "indies": "East Indies",
        "sea": "South Seas", "south_seas": "South Seas", "seas": "South Seas",
    }
    active_region = region_map.get(region_filter.lower(), region_filter) if region_filter else None

    ports_to_show = {
        pid: p for pid, p in PORTS.items()
        if active_region is None or p.region == active_region
    }

    # --- Draw routes ---
    port_grid_coords: dict[str, tuple[int, int]] = {}
    for pid, port in ports_to_show.items():
        port_grid_coords[pid] = game_to_grid(port.map_x, port.map_y)

    if show_routes:
        for route in ROUTES:
            if route.port_a not in ports_to_show or route.port_b not in ports_to_show:
                continue
            ax, ay = port_grid_coords[route.port_a]
            bx, by = port_grid_coords[route.port_b]
            style_color, style_char = _ROUTE_STYLES.get(
                route.min_ship_class, ("dim", "\u00b7"))
            for px, py in _bresenham(ax, ay, bx, by):
                if 0 <= px < MAP_W and 0 <= py < MAP_H:
                    grid[py][px] = (style_char, style_color)

    # --- Draw ports (two passes: labels first, then markers on top) ---
    # Reserve all marker positions first so labels avoid them
    occupied: set[tuple[int, int]] = set()
    marker_data: list[tuple[int, int, str, str]] = []  # (x, y, char, style)

    sorted_ports = sorted(ports_to_show.items(), key=lambda kv: kv[1].map_x)

    for pid, port in sorted_ports:
        mx, my = port_grid_coords[pid]
        color = _REGION_COLORS.get(port.region, "white")
        is_current = pid == player_port_id

        if is_current:
            marker = "*"
            marker_style = f"bold {color}"
        else:
            icon = "o"
            for feat in port.features:
                if feat.value in _FEATURE_ICON:
                    icon = _FEATURE_ICON[feat.value]
                    break
            marker = icon
            marker_style = f"bold {color}"

        if 0 <= mx < MAP_W and 0 <= my < MAP_H:
            occupied.add((mx, my))
            marker_data.append((mx, my, marker, marker_style))

    # Pass 1: place labels (avoiding marker positions and each other)
    for pid, port in sorted_ports:
        mx, my = port_grid_coords[pid]
        color = _REGION_COLORS.get(port.region, "white")
        is_current = pid == player_port_id

        label = port.name
        if is_current:
            label = f"> {label}"
        label_style = f"bold {color}" if is_current else color

        placed = False
        for dy in (0, -1, 1, -2, 2, -3, 3):
            ly = my + dy
            if ly < 0 or ly >= MAP_H:
                continue
            for try_x in (mx + 2, mx - len(label) - 1):
                cells = [(try_x + i, ly) for i in range(len(label))]
                if all(0 <= cx < MAP_W and (cx, ly) not in occupied for cx, _ in cells):
                    for i, ch in enumerate(label):
                        lx = try_x + i
                        grid[ly][lx] = (ch, label_style)
                        occupied.add((lx, ly))
                    placed = True
                    break
            if placed:
                break

        if not placed:
            label_x = mx + 2
            if label_x + len(label) >= MAP_W:
                label_x = mx - len(label) - 1
            for i, ch in enumerate(label):
                lx = label_x + i
                if 0 <= lx < MAP_W and 0 <= my < MAP_H:
                    grid[my][lx] = (ch, label_style)

    # Pass 2: stamp markers on top (they always win)
    for mx, my, marker, marker_style in marker_data:
        grid[my][mx] = (marker, marker_style)

    # --- Build Rich Text output ---
    output_lines: list[str] = []
    for row in grid:
        line_parts: list[str] = []
        for ch, style in row:
            line_parts.append(f"[{style}]{ch}[/{style}]")
        output_lines.append("".join(line_parts))

    map_text = "\n".join(output_lines)

    # --- Legend ---
    _REGION_ABBR: dict[str, str] = {
        "Mediterranean": "MED",
        "North Atlantic": "ATL",
        "West Africa": "AFR",
        "East Indies": "IND",
        "South Seas": "SEA",
    }
    legend_parts = ["[bold]Legend:[/bold]  "]
    for region, color in _REGION_COLORS.items():
        if active_region and region != active_region:
            continue
        abbr = _REGION_ABBR.get(region, region[:3].upper())
        legend_parts.append(f"[{color}]o {abbr}[/{color}]  ")
    legend_parts.append("  ")
    legend_parts.append("[S] Shipyard  [B] Black Market  [H] Safe Harbor")
    if player_port_id:
        legend_parts.append("  [bold]* You[/bold]")

    if show_routes:
        legend_parts.append("\n[bold]Routes:[/bold]  ")
        legend_parts.append("[dim]\u00b7 Sloop[/dim]  ")
        legend_parts.append("[white]- Brigantine[/white]  ")
        legend_parts.append("[yellow]= Galleon[/yellow]  ")
        legend_parts.append("[red]# Man-of-War[/red]")

    legend = "".join(legend_parts)

    title = "[bold cyan]The Known World[/bold cyan]"
    if active_region:
        title = f"[bold cyan]{active_region}[/bold cyan]"
    if player_port_id and player_port_id in PORTS:
        port_name = PORTS[player_port_id].name
        title += f"  [dim]|[/dim]  [bold]Docked: {port_name}[/bold]"

    content = f"{map_text}\n\n{legend}"
    return Panel(content, title=title, border_style="cyan", padding=(0, 1))
