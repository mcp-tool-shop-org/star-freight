"""Star Freight view layer — product surfaces for the four system truths.

Every screen answers:
1. Where am I?
2. What matters right now?
3. What can I do?
4. What will it cost?
5. What changed last?

This replaces Portlight's maritime views with Star Freight's
campaign-aware surfaces. Pure rendering — reads state, returns Rich renderables.
"""

from __future__ import annotations

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box

from portlight.engine.sf_campaign import (
    CampaignState,
    get_campaign_summary,
)
from portlight.engine.crew import (
    CrewMember,
    CrewRosterState,
    CrewRole,
    CrewStatus,
    Civilization,
    LoyaltyTier,
    active_crew,
    fit_crew,
    crew_by_civ,
    get_ship_abilities,
    get_combat_abilities,
    get_narrative_hooks,
    calculate_crew_pay,
    cultural_knowledge_level,
    crew_impact_report,
    MAX_CREW,
    DEPARTURE_THRESHOLD,
)
from portlight.engine.grid_combat import (
    CombatState,
    CombatPhase,
    CombatResult,
    Combatant,
    CombatAbility,
    Team,
    Pos,
    TileType,
    GRID_WIDTH,
    GRID_HEIGHT,
    get_valid_targets,
    get_valid_moves,
    get_available_abilities,
)
from portlight.engine.investigation import (
    InvestigationState,
    InvestigationThread,
    ThreadState,
    Fragment,
    EvidenceGrade,
    get_journal_view,
    check_delay_consequences,
)
from portlight.content.star_freight import (
    SLICE_STATIONS,
    SLICE_LANES,
    SLICE_GOODS,
)


# ---------------------------------------------------------------------------
# Color palette (space theme)
# ---------------------------------------------------------------------------

C_GOLD = "bold #f0c040"
C_RED = "bold #e05050"
C_GREEN = "bold #40c060"
C_BLUE = "#4090e0"
C_DIM = "dim"
C_KETH = "#d0a040"
C_VESHAN = "#c04040"
C_ORRYN = "#40b0b0"
C_REACH = "#9060c0"
C_COMPACT = "#4090e0"

CIV_COLORS = {
    "compact": C_COMPACT,
    "keth": C_KETH,
    "veshan": C_VESHAN,
    "orryn": C_ORRYN,
    "reach": C_REACH,
}


def _bar(current: int, maximum: int, width: int = 10) -> Text:
    """Render a health/fuel/morale bar."""
    if maximum <= 0:
        return Text("░" * width, style=C_DIM)
    frac = max(0.0, min(1.0, current / maximum))
    filled = int(frac * width)
    if frac > 0.6:
        color = "green"
    elif frac > 0.3:
        color = "yellow"
    else:
        color = "red"
    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * (width - filled), style=C_DIM)
    return bar


def _civ_style(civ: str) -> str:
    return CIV_COLORS.get(civ, "white")


# ---------------------------------------------------------------------------
# 1. Captain's View (persistent bar)
# ---------------------------------------------------------------------------

def captains_view(state: CampaignState) -> Panel:
    """The persistent pressure bar. Ship instrumentation, not debug output.

    Always answers: credits, hull, fuel, crew fitness, day, pressure, location.
    """
    crew_active = active_crew(state.crew)
    crew_fit_count = len(fit_crew(state.crew))
    crew_total = len(crew_active)
    monthly = calculate_crew_pay(state.crew)

    # Line 1: Hard numbers
    line1 = Text()
    line1.append(f" {state.credits}₡", style=C_GOLD)
    line1.append("  │  Hull ")
    line1.append_text(_bar(state.ship_hull, state.ship_hull_max, 8))
    line1.append(f" {state.ship_hull}/{state.ship_hull_max}")
    line1.append("  │  Fuel ")
    fuel_style = C_RED if state.ship_fuel <= 2 else "yellow" if state.ship_fuel <= 4 else "green"
    line1.append(f"{state.ship_fuel}d", style=fuel_style)
    line1.append(f"  │  Crew {crew_fit_count}/{crew_total} fit")
    line1.append(f"  │  Day {state.day}")

    # Line 2: Pressure context
    line2 = Text()

    # Top reputation
    rep_sorted = sorted(state.reputation.items(), key=lambda x: abs(x[1]), reverse=True)
    for faction, val in rep_sorted[:2]:
        arrow = "▲" if val > 0 else "▼" if val < 0 else "─"
        style = C_GREEN if val > 0 else C_RED if val < 0 else C_DIM
        line2.append(f" {arrow}{faction}", style=style)

    # Crew alerts
    for m in crew_active:
        if m.status == CrewStatus.INJURED:
            line2.append(f"  │  {m.name} injured", style=C_RED)
        elif m.morale < DEPARTURE_THRESHOLD:
            line2.append(f"  │  {m.name} ⚠ morale", style="yellow")

    # Pay pressure
    days_since_pay = state.day - state.last_pay_day
    days_to_pay = 30 - days_since_pay
    if days_to_pay <= 5 and monthly > 0:
        pay_style = C_RED if days_to_pay <= 2 else "yellow"
        line2.append(f"  │  Pay due {days_to_pay}d", style=pay_style)

    # Location
    if state.current_station:
        station = SLICE_STATIONS.get(state.current_station)
        name = station.name if station else state.current_station
        line2.append(f"  │  {name}", style="bold")

    return Panel(
        Group(line1, line2),
        title="[bold]Star Freight[/bold]",
        border_style="blue",
        box=box.HEAVY,
        padding=(0, 1),
    )


# ---------------------------------------------------------------------------
# 2. Crew Screen (thesis surface)
# ---------------------------------------------------------------------------

def crew_screen(state: CampaignState) -> Panel:
    """The most important screen in the product.

    Each crew member shows all four contributions.
    Absence must hurt at a glance.
    """
    parts = []

    for member in state.crew.members:
        if member.status == CrewStatus.DEPARTED:
            continue
        parts.append(_crew_card(member, state))

    # Roster summary
    active = active_crew(state.crew)
    fit = fit_crew(state.crew)
    monthly = calculate_crew_pay(state.crew)

    summary = Text()
    summary.append(f"\n[{len(active)}/{MAX_CREW} crew slots]", style="bold")
    summary.append(f"  │  {len(fit)} fit for duty")
    summary.append(f"  │  Monthly cost: {monthly}₡", style=C_GOLD)

    # Gaps
    report = crew_impact_report(state.crew, state.cultural_knowledge)
    if report["missing_cultural_access"]:
        missing = ", ".join(c.title() for c in report["missing_cultural_access"])
        summary.append(f"\n  No cultural access: {missing}", style=C_DIM)

    parts.append(summary)

    return Panel(
        Group(*parts),
        title="[bold]Crew[/bold]",
        border_style="cyan",
        box=box.ROUNDED,
    )


def _crew_card(member: CrewMember, state: CampaignState) -> Panel:
    """Render one crew member with all four contributions visible."""
    lines = []

    # Header: Name, Role, Civilization
    header = Text()
    header.append(f"  {member.name}", style="bold")
    header.append(f"  [{member.role.value.upper()}]", style=C_DIM)
    header.append(f"  {member.civilization.value.title()}", style=_civ_style(member.civilization.value))

    # Status line
    status = Text("  ")
    if member.status == CrewStatus.ACTIVE:
        status.append("ACTIVE", style=C_GREEN)
    elif member.status == CrewStatus.INJURED:
        status.append(f"INJURED ({member.injury_days_remaining}d)", style=C_RED)
    elif member.status == CrewStatus.RECOVERING:
        status.append(f"RECOVERING ({member.injury_days_remaining}d)", style="yellow")
    status.append(f"  HP: {member.hp}/{member.hp_max}")
    status.append("  Morale: ")
    status.append_text(_bar(member.morale, 100, 6))
    status.append(f" {member.morale}")
    status.append(f"  {member.loyalty_tier.value.title()}", style=C_DIM)
    if member.morale < DEPARTURE_THRESHOLD:
        status.append("  ⚠ DEPARTURE RISK", style=C_RED)

    # Ship ability
    ship_line = Text("  Ship:    ")
    if member.ship_skill:
        if member.status == CrewStatus.ACTIVE:
            ship_line.append(f"{member.ship_skill.replace('_', ' ').title()}", style=C_GREEN)
            ship_line.append(" (active)")
        elif member.status in (CrewStatus.INJURED, CrewStatus.RECOVERING):
            ship_line.append(f"{member.ship_skill.replace('_', ' ').title()}", style="yellow")
            ship_line.append(" (DEGRADED — injured)", style=C_RED)
    else:
        ship_line.append("none", style=C_DIM)

    # Combat abilities
    combat_line = Text("  Combat:  ")
    for i, ab in enumerate(member.abilities):
        if i >= 2:
            # Third ability — loyalty gated
            if member.loyalty_tier == LoyaltyTier.STRANGER:
                combat_line.append(f"  [{ab}]", style=C_DIM)
                combat_line.append(" locked:trusted", style=C_DIM)
            else:
                combat_line.append(f"  {ab}", style=C_GREEN)
        else:
            if member.status == CrewStatus.ACTIVE:
                combat_line.append(f"  {ab}", style="white")
            else:
                combat_line.append(f"  {ab}", style=C_RED)
                combat_line.append(" (unavailable)", style=C_DIM)

    # Cultural contribution
    culture_line = Text("  Culture: ")
    civ = member.civilization
    level = cultural_knowledge_level(state.crew, civ, state.cultural_knowledge)
    culture_line.append(f"{civ.value.title()} access level {level}", style=_civ_style(civ.value))

    # Narrative
    narrative_line = Text("  Plot:    ")
    if member.narrative_hooks:
        narrative_line.append(", ".join(member.narrative_hooks), style="italic")
    else:
        narrative_line.append("none", style=C_DIM)
    if member.personal_quest_available:
        narrative_line.append("  ★ quest available", style=C_GOLD)

    # Pay
    pay_line = Text(f"  Pay: {member.pay_rate}₡/month", style=C_DIM)

    border = "red" if member.status == CrewStatus.INJURED else "cyan" if member.status == CrewStatus.ACTIVE else "yellow"

    return Panel(
        Group(header, status, ship_line, combat_line, culture_line, narrative_line, pay_line),
        border_style=border,
        box=box.SIMPLE,
        padding=(0, 0),
    )


# ---------------------------------------------------------------------------
# 3. After-Action Summary
# ---------------------------------------------------------------------------

def after_action_summary(result: CombatResult, state: CampaignState) -> Panel:
    """Make campaign writeback emotionally real.

    Shows every state delta explicitly. No hidden changes.
    """
    lines = []

    # Outcome header
    outcome_style = {
        CombatPhase.VICTORY: C_GREEN,
        CombatPhase.DEFEAT: C_RED,
        CombatPhase.RETREAT: "yellow",
    }.get(result.outcome, "white")

    header = Text()
    header.append(f"  {result.outcome.value.upper()}", style=outcome_style)
    header.append(f"  — {result.turns_taken} turns")
    lines.append(header)
    lines.append(Text())

    # Credits
    if result.credits_gained > 0:
        lines.append(Text(f"  Credits:     +{result.credits_gained}₡ (salvage)", style=C_GOLD))
    elif result.credits_gained < 0:
        lines.append(Text(f"  Credits:     {result.credits_gained}₡", style=C_RED))

    # Hull damage
    if result.hull_damage_taken > 0:
        lines.append(Text(
            f"  Hull damage: -{result.hull_damage_taken} "
            f"({result.player_hull_remaining}/{result.player_hull_max} remaining)",
            style=C_RED,
        ))

    # Shield
    if result.shield_damage_taken > 0:
        lines.append(Text(
            f"  Shield:      -{result.shield_damage_taken} "
            f"({result.player_shield_remaining} remaining)",
            style=C_BLUE,
        ))

    # Cargo lost
    if result.cargo_lost:
        lost_names = []
        for gid in result.cargo_lost:
            good = SLICE_GOODS.get(gid)
            lost_names.append(good.name if good else gid)
        lines.append(Text(f"  Cargo lost:  {', '.join(lost_names)}", style=C_RED))

    # Reputation changes
    if result.reputation_delta:
        for faction, delta in result.reputation_delta.items():
            sign = "+" if delta > 0 else ""
            style = C_GREEN if delta > 0 else C_RED
            lines.append(Text(f"  Reputation:  {faction} {sign}{delta}", style=style))

    # Crew injuries
    if result.crew_injuries:
        for crew_id in result.crew_injuries:
            for m in state.crew.members:
                if m.id == crew_id:
                    lines.append(Text(f"  Crew:        {m.name} INJURED", style=C_RED))
                    if m.ship_skill:
                        lines.append(Text(
                            f"               → {m.ship_skill.replace('_', ' ').title()} DEGRADED",
                            style="yellow",
                        ))
                    lines.append(Text(
                        f"               → Combat abilities UNAVAILABLE",
                        style=C_DIM,
                    ))

    # Consequence tags
    if result.consequence_tags:
        tags = ", ".join(result.consequence_tags)
        lines.append(Text(f"  Consequence: {tags}", style=C_DIM))

    lines.append(Text())
    lines.append(Text("  Press any key to continue...", style=C_DIM))

    return Panel(
        Group(*lines),
        title="[bold]AFTERMATH[/bold]",
        border_style=outcome_style.replace("bold ", "") if "bold" in outcome_style else outcome_style,
        box=box.DOUBLE,
        padding=(1, 2),
    )


# ---------------------------------------------------------------------------
# 4. Grid Combat Screen
# ---------------------------------------------------------------------------

def combat_screen(combat: CombatState) -> Panel:
    """Tactical grid with crew abilities visible."""
    parts = []

    # Turn info
    current = combat.current_actor
    turn_info = Text()
    turn_info.append(f"  Turn {combat.turn}", style="bold")
    if current:
        side = "YOUR TURN" if current.team == Team.PLAYER else "ENEMY TURN"
        style = C_GREEN if current.team == Team.PLAYER else C_RED
        turn_info.append(f"  │  {side}: {current.name}", style=style)
        turn_info.append(f"  │  Actions: {current.actions_remaining}/{current.actions_per_turn}")
    parts.append(turn_info)

    # Grid
    grid_text = _render_grid(combat)
    parts.append(grid_text)

    # Combatant status
    for c in combat.combatants.values():
        if not c.alive:
            continue
        status = Text()
        style = C_GREEN if c.team == Team.PLAYER else C_RED
        status.append(f"  {c.name}", style=style)
        status.append("  HP: ")
        status.append_text(_bar(c.hp, c.hp_max, 8))
        status.append(f" {c.hp}/{c.hp_max}")
        if c.shield_max > 0:
            status.append("  Shield: ")
            status.append_text(_bar(c.shield, c.shield_max, 5))
            status.append(f" {c.shield}")
        if c.retreating:
            status.append(f"  RETREATING ({c.retreat_progress}/2)", style="yellow")
        parts.append(status)

    # Available actions (for current player actor)
    if current and current.team == Team.PLAYER and current.actions_remaining > 0:
        parts.append(Text())
        parts.append(Text("  Actions:", style="bold"))

        targets = get_valid_targets(combat, current.id)
        if targets:
            parts.append(Text(f"  [T] Attack ({current.base_attack_damage} dmg, range {current.base_attack_range})", style="white"))

        abilities = get_available_abilities(combat, current.id)
        for ab in abilities:
            ab_text = Text(f"  [A] {ab.name}")
            if ab.crew_source:
                ab_text.append(f" — {ab.crew_source}", style=C_DIM)
            if ab.degraded:
                ab_text.append(" (DEGRADED)", style="yellow")
            ab_text.append(f" ({ab.effect_type}, cd:{ab.cooldown})", style=C_DIM)
            parts.append(ab_text)

        # Show locked/unavailable abilities
        for ab in current.abilities:
            if ab.id not in [a.id for a in abilities]:
                reason = "cooldown" if combat.combatants[current.id].ability_cooldowns.get(ab.id, 0) > 0 else "cost"
                parts.append(Text(f"  [-] {ab.name} — {reason}", style=C_DIM))

        parts.append(Text("  [V] Defend (+evasion this turn)", style="white"))
        parts.append(Text("  [X] Retreat (cargo at risk)", style="yellow"))

        moves = get_valid_moves(combat, current.id)
        if moves:
            parts.append(Text(f"  [M] Move ({current.speed} tiles, {len(moves)} options)", style="white"))

    # Legend
    parts.append(Text())
    parts.append(Text("  # asteroid  ~ debris(cover)  ≈ nebula(hide)  N you  E enemy", style=C_DIM))

    return Panel(
        Group(*parts),
        title="[bold red]COMBAT[/bold red]",
        border_style="red",
        box=box.DOUBLE,
    )


def _render_grid(combat: CombatState) -> Text:
    """Render the 8x6 combat grid as text."""
    grid = Text()
    grid.append("  ")
    for x in range(GRID_WIDTH):
        grid.append(f" {x}", style=C_DIM)
    grid.append("\n")

    for y in range(GRID_HEIGHT):
        grid.append(f"  {y}", style=C_DIM)
        for x in range(GRID_WIDTH):
            pos = Pos(x, y)
            tile = combat.grid[y][x]

            # Check for combatant
            occupant = None
            for c in combat.combatants.values():
                if c.alive and c.pos == pos:
                    occupant = c
                    break

            if occupant:
                if occupant.team == Team.PLAYER:
                    grid.append(" N", style=C_GREEN)
                else:
                    grid.append(" E", style=C_RED)
            elif tile.tile_type == TileType.ASTEROID:
                grid.append(" #", style="white")
            elif tile.tile_type == TileType.DEBRIS:
                grid.append(" ~", style="yellow")
            elif tile.tile_type == TileType.NEBULA:
                grid.append(" ≈", style=C_REACH)
            else:
                grid.append(" .", style=C_DIM)
        grid.append("\n")

    return grid


# ---------------------------------------------------------------------------
# 5. Journal Screen
# ---------------------------------------------------------------------------

def journal_screen(state: CampaignState) -> Panel:
    """Investigation fragments. Not a task list."""
    journal = get_journal_view(state.investigation)
    parts = []

    if not journal:
        parts.append(Text("  No active investigations.", style=C_DIM))
        parts.append(Text("  Leads emerge from trade, combat, crew, and station life.", style=C_DIM))
    else:
        for entry in journal:
            thread_style = {
                "active": "yellow",
                "advanced": C_GOLD,
                "critical": C_RED,
                "resolved": C_GREEN,
            }.get(entry["state"], "white")

            header = Text()
            header.append(f"  {entry['title']}", style="bold")
            header.append(f" — {entry['state'].upper()}", style=thread_style)
            parts.append(header)

            premise = Text(f"  {entry['premise']}", style=C_DIM)
            parts.append(premise)
            parts.append(Text())

            # Fragments
            grade_icons = {
                "rumor": "○",
                "clue": "●",
                "corroborated": "◆",
                "actionable": "★",
                "locked": "✦",
            }

            for frag in entry["fragments"]:
                icon = grade_icons.get(frag["grade"], "?")
                frag_text = Text()
                frag_text.append(f"  {icon} [{frag['grade'].upper()}]", style=thread_style)
                frag_text.append(f" {frag['content'][:80]}...")
                parts.append(frag_text)

                source_text = Text(f"    Source: {frag['source']}", style=C_DIM)
                if frag.get("interpreter"):
                    source_text.append(f"  │  Interpreted by: {frag['interpreter']}", style="italic")
                source_text.append(f"  │  Day {frag['day']}")
                parts.append(source_text)

            parts.append(Text())

    # Delay warnings
    delays = check_delay_consequences(state.investigation, state.day)
    for delay in delays:
        parts.append(Text(f"  ⚠ {delay['warning']}", style=C_RED))

    return Panel(
        Group(*parts),
        title="[bold]Journal[/bold]",
        border_style="yellow",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# 6. Dashboard
# ---------------------------------------------------------------------------

def dashboard(state: CampaignState) -> Panel:
    """Captain summary. Pressure overview. All four truths visible."""
    parts = []

    # Pressure panel
    monthly = calculate_crew_pay(state.crew)
    runway = state.credits / max(1, monthly) if monthly > 0 else 999
    days_to_pay = 30 - (state.day - state.last_pay_day)

    pressure = Text()
    pressure.append("  Credits: ", style="bold")
    pressure.append(f"{state.credits}₡", style=C_GOLD)
    pressure.append(f"  │  Monthly cost: {monthly}₡")
    pressure.append(f"  │  Runway: ~{runway:.1f} months")
    if days_to_pay <= 7 and monthly > 0:
        pay_style = C_RED if days_to_pay <= 3 else "yellow"
        pressure.append(f"  │  Pay due: {days_to_pay}d", style=pay_style)
    pressure.append(f"\n  Fuel: {state.ship_fuel}d")
    pressure.append(f"  │  Hull: {state.ship_hull}/{state.ship_hull_max}")
    pressure.append(f"  │  Cargo: {len(state.ship_cargo)}/{state.ship_cargo_capacity}")
    parts.append(Panel(pressure, title="Pressure", box=box.SIMPLE))

    # Crew summary
    crew_text = Text()
    for m in active_crew(state.crew):
        name_style = C_RED if m.status == CrewStatus.INJURED else "bold"
        crew_text.append(f"  {m.name}", style=name_style)
        crew_text.append(f" [{m.role.value[:3].upper()}]", style=C_DIM)
        crew_text.append(f" {m.civilization.value.title()}", style=_civ_style(m.civilization.value))
        crew_text.append("  ")
        crew_text.append_text(_bar(m.morale, 100, 4))
        if m.status == CrewStatus.INJURED:
            crew_text.append(f" injured({m.injury_days_remaining}d)", style=C_RED)
        crew_text.append("\n")

    ship_abs = get_ship_abilities(state.crew)
    crew_text.append(f"  Ship abilities: {len([a for a in ship_abs if not a['degraded']])}/{len(ship_abs)} active")
    parts.append(Panel(crew_text, title="Crew", box=box.SIMPLE))

    # Investigation
    active_threads = [t for t in state.investigation.threads.values()
                     if t.state != ThreadState.DORMANT]
    inv_text = Text()
    if active_threads:
        for t in active_threads:
            inv_text.append(f"  {t.title} — {t.state.value.upper()}", style="yellow")
            inv_text.append(f" ({len(t.fragments)} fragments)\n")
    else:
        inv_text.append("  No active investigations", style=C_DIM)
    parts.append(Panel(inv_text, title="Investigation", box=box.SIMPLE))

    return Panel(
        Group(*parts),
        title="[bold]Dashboard[/bold]",
        border_style="blue",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# 7. Station Screen
# ---------------------------------------------------------------------------

def station_screen(state: CampaignState) -> Panel:
    """Current station with cultural rules and identity."""
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return Panel(Text("  In transit.", style=C_DIM), title="Station")

    parts = []

    # Identity
    header = Text()
    header.append(f"  {station.name}", style="bold")
    header.append(f"  │  {station.civilization.title()}", style=_civ_style(station.civilization))
    parts.append(header)
    parts.append(Text(f"  {station.description[:120]}...", style=C_DIM))
    parts.append(Text())

    # Cultural greeting
    parts.append(Text(f"  {station.cultural_greeting}", style="italic"))
    parts.append(Text())

    # Services
    services = Text("  Services: ")
    services.append(", ".join(station.services))
    parts.append(services)
    parts.append(Text(f"  Docking fee: {station.docking_fee}₡  │  Repair: {station.repair_cost_per_point}₡/pt  │  Fuel: {station.fuel_cost_per_day}₡/day"))
    parts.append(Text())

    # Cultural rules
    if station.cultural_restriction:
        parts.append(Text(f"  ⚠ {station.cultural_restriction}", style="yellow"))
    if station.cultural_opportunity:
        parts.append(Text(f"  ★ {station.cultural_opportunity}", style=C_GREEN))

    # Crew relevance
    civ = station.civilization
    relevant_crew = [m for m in active_crew(state.crew) if m.civilization.value == civ]
    if relevant_crew:
        names = ", ".join(m.name for m in relevant_crew)
        parts.append(Text(f"  Crew: {names} provides cultural access here", style="italic"))

    return Panel(
        Group(*parts),
        title="[bold]Station[/bold]",
        border_style=_civ_style(station.civilization).replace("bold ", "") if "bold" in _civ_style(station.civilization) else _civ_style(station.civilization),
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# 8. Routes Screen
# ---------------------------------------------------------------------------

def routes_screen(state: CampaignState) -> Panel:
    """Lane selection with pressure visible."""
    current = state.current_station
    parts = []

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("#", width=3)
    table.add_column("Destination", min_width=18)
    table.add_column("Civ", width=8)
    table.add_column("Days", width=5, justify="right")
    table.add_column("Danger", width=8)
    table.add_column("Inspect", width=8)
    table.add_column("Terrain", width=12)
    table.add_column("Control", width=10)

    idx = 1
    for lane in SLICE_LANES.values():
        dest = None
        if lane.station_a == current:
            dest = lane.station_b
        elif lane.station_b == current:
            dest = lane.station_a
        if dest is None:
            continue

        dest_station = SLICE_STATIONS.get(dest)
        dest_name = dest_station.name if dest_station else dest
        dest_civ = dest_station.civilization if dest_station else "?"

        # Danger visualization
        if lane.danger >= 0.20:
            danger_text = Text("☠☠☠", style=C_RED)
        elif lane.danger >= 0.10:
            danger_text = Text("☠☠", style="yellow")
        elif lane.danger >= 0.05:
            danger_text = Text("☠", style=C_DIM)
        else:
            danger_text = Text("✓", style=C_GREEN)

        # Inspection risk
        if lane.contraband_risk >= 0.20:
            inspect_text = Text("HIGH", style=C_RED)
        elif lane.contraband_risk >= 0.10:
            inspect_text = Text("med", style="yellow")
        elif lane.contraband_risk > 0:
            inspect_text = Text("low", style=C_DIM)
        else:
            inspect_text = Text("—", style=C_DIM)

        # Fuel check
        fuel_ok = state.ship_fuel >= lane.distance_days
        days_style = "white" if fuel_ok else C_RED

        table.add_row(
            str(idx),
            dest_name,
            Text(dest_civ, style=_civ_style(dest_civ)),
            Text(str(lane.distance_days), style=days_style),
            danger_text,
            inspect_text,
            lane.terrain,
            lane.controlled_by,
        )
        idx += 1

    parts.append(table)
    parts.append(Text(f"\n  Fuel: {state.ship_fuel} days remaining", style="bold"))
    parts.append(Text("  [G] Travel to destination  │  [D] Dashboard", style=C_DIM))

    return Panel(
        Group(*parts),
        title="[bold]Routes[/bold]",
        border_style="cyan",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# 9. Market Screen
# ---------------------------------------------------------------------------

def market_screen(state: CampaignState) -> Panel:
    """Trade with cultural and risk context visible."""
    station = SLICE_STATIONS.get(state.current_station)
    if station is None:
        return Panel(Text("  Not at a station.", style=C_DIM), title="Market")

    parts = []

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Good", min_width=20)
    table.add_column("Price", width=8, justify="right")
    table.add_column("Supply", width=8)
    table.add_column("Held", width=5, justify="right")
    table.add_column("Access", min_width=20)

    for good_id, good in SLICE_GOODS.items():
        price = good.base_price
        supply = ""
        if good_id in station.produces:
            price = int(price * 0.8)
            supply = "local"
        elif good_id in station.demands:
            price = int(price * 1.3)
            supply = "demand"

        held = state.ship_cargo.count(good_id)

        # Access
        access = Text()
        if good.cultural_restriction:
            civ = Civilization(station.civilization) if station.civilization in [c.value for c in Civilization] else None
            if civ and station.knowledge_required_for_restricted > 0:
                level = cultural_knowledge_level(state.crew, civ, state.cultural_knowledge)
                if level >= station.knowledge_required_for_restricted:
                    crew_src = [m.name for m in active_crew(state.crew) if m.civilization == civ]
                    if crew_src:
                        access.append(f"✓ {crew_src[0]}", style=C_GREEN)
                    else:
                        access.append("✓ knowledge", style=C_GREEN)
                else:
                    access.append(f"✗ need lvl {station.knowledge_required_for_restricted}", style=C_RED)
            else:
                access.append("—")
        elif good_id in station.contraband:
            access.append("CONTRABAND", style=C_RED)
        else:
            access.append("open", style=C_DIM)

        name_style = "bold" if supply else "white"
        table.add_row(
            Text(good.name, style=name_style),
            Text(f"{price}₡", style=C_GOLD),
            Text(supply, style=C_GREEN if supply == "local" else "yellow" if supply == "demand" else C_DIM),
            str(held) if held > 0 else "—",
            access,
        )

    parts.append(table)
    parts.append(Text(f"\n  Credits: {state.credits}₡  │  Cargo: {len(state.ship_cargo)}/{state.ship_cargo_capacity}", style="bold"))
    parts.append(Text("  [B] Buy  │  [L] Sell  │  [D] Dashboard", style=C_DIM))

    return Panel(
        Group(*parts),
        title="[bold]Market[/bold]",
        border_style="green",
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# 10. Faction Screen
# ---------------------------------------------------------------------------

def faction_screen(state: CampaignState) -> Panel:
    """Reputation with practical meaning."""
    parts = []

    breakpoints = [
        (-75, "Hostile", C_RED),
        (-50, "Unwelcome", C_RED),
        (-25, "Cold", "yellow"),
        (0, "Neutral", C_DIM),
        (25, "Respected", C_GREEN),
        (50, "Trusted", C_GREEN),
        (75, "Allied", C_GOLD),
    ]

    def get_label(val: int) -> tuple[str, str]:
        label, style = "Neutral", C_DIM
        for threshold, l, s in breakpoints:
            if val >= threshold:
                label, style = l, s
        return label, style

    for faction, standing in sorted(state.reputation.items()):
        label, style = get_label(standing)
        line = Text()
        line.append(f"  {faction:<20}", style="bold")
        line.append_text(_bar(standing + 100, 200, 10))  # map -100..100 to 0..200
        line.append(f" {standing:+d}", style=style)
        line.append(f"  {label}", style=style)
        parts.append(line)

    return Panel(
        Group(*parts),
        title="[bold]Faction Standing[/bold]",
        border_style="magenta",
        box=box.ROUNDED,
    )
