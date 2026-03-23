"""Rich views - combat screens that answer player questions during encounters.

Each view is a function that returns a Rich renderable (Panel, Table, Group).
Views never mutate game state. They read and present.

Encounter screen answers: who is this pirate, how dangerous, what are my options.
Naval status answers: hull state, crew, boarding progress, what can I do.
Combat status answers: HP, stamina, injuries, ammo, fighting style, what can I do.
Training screen answers: who teaches here, what styles, can I afford it.
Injuries screen answers: what hurts, how bad, is it healing.
Armory screen answers: what weapons, what I carry, ammo count.
Fight result answers: did I win, what did it cost, what did I gain.

All functions accept plain dicts/primitives — no engine imports.
The session layer converts dataclasses to dicts before calling these views.
"""

from __future__ import annotations

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


# ---------------------------------------------------------------------------
# Formatting helpers (local to combat views, no engine dependency)
# ---------------------------------------------------------------------------

def _hp_bar(current: int, maximum: int, width: int = 20) -> str:
    """Visual HP/hull bar with color thresholds."""
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    color = "green" if ratio > 0.6 else "yellow" if ratio > 0.3 else "red"
    bar = f"[{color}]{'#' * filled}{'-' * empty}[/{color}]"
    return f"{bar} {current}/{maximum}"


def _stamina_bar(current: int, maximum: int, width: int = 15) -> str:
    """Visual stamina bar."""
    ratio = current / maximum if maximum > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    color = "cyan" if ratio > 0.5 else "yellow" if ratio > 0.25 else "red"
    bar = f"[{color}]{'#' * filled}{'-' * empty}[/{color}]"
    return f"{bar} {current}/{maximum}"


def _boarding_bar(progress: int, threshold: int, width: int = 15) -> str:
    """Visual boarding progress bar."""
    ratio = progress / threshold if threshold > 0 else 0
    filled = int(ratio * width)
    empty = width - filled
    color = "magenta" if ratio < 0.5 else "yellow" if ratio < 0.8 else "bold green"
    bar = f"[{color}]{'#' * filled}{'-' * empty}[/{color}]"
    return f"{bar} [{progress}/{threshold}]"


def _strength_indicator(strength: int) -> str:
    """Sword icons and label for pirate strength 1-10."""
    swords = "X" * min(strength, 10)
    if strength <= 3:
        return f"[green]{swords} Weak[/green]"
    elif strength <= 6:
        return f"[yellow]{swords} Moderate[/yellow]"
    elif strength <= 8:
        return f"[red]{swords} Dangerous[/red]"
    return f"[bold red]{swords} Deadly[/bold red]"


def _severity_color(severity: str) -> str:
    """Map injury severity to Rich color tag."""
    severity_lower = severity.lower()
    if severity_lower == "minor":
        return "yellow"
    elif severity_lower == "major":
        return "dark_orange"
    elif severity_lower in ("crippling", "permanent"):
        return "red"
    return "dim"


def _delta_str(value: int) -> str:
    """Format a +/- number with color."""
    if value > 0:
        return f"[green]+{value}[/green]"
    elif value < 0:
        return f"[red]{value}[/red]"
    return "[dim]0[/dim]"


def _silver(amount: int) -> str:
    """Format silver amount."""
    return f"[yellow]{amount:,}[/yellow] silver"


# ---------------------------------------------------------------------------
# Encounter view - pirate encounter presentation
# ---------------------------------------------------------------------------

def encounter_view(
    captain_name: str,
    faction_name: str,
    personality: str,
    strength: int,
    ship_name: str,
    encounter_flavor: str,
) -> Panel:
    """Pirate encounter screen: who they are, how dangerous, your options."""
    lines: list[str] = []

    lines.append("[bold red]Sails on the horizon![/bold red]")
    lines.append("")
    lines.append(f"  Captain:   [bold]{captain_name}[/bold]")
    lines.append(f"  Faction:   {faction_name}")
    lines.append(f"  Ship:      {ship_name}")
    lines.append(f"  Demeanor:  [italic]{personality}[/italic]")
    lines.append(f"  Strength:  {_strength_indicator(strength)}")
    lines.append("")
    lines.append(f"[italic]{encounter_flavor}[/italic]")
    lines.append("")
    lines.append("[bold]What will you do?[/bold]")
    lines.append("  [cyan][negotiate][/cyan]  [yellow][flee][/yellow]  [red][fight][/red]")

    return Panel(
        "\n".join(lines),
        title="[bold red]Pirate Encounter[/bold red]",
        border_style="red",
    )


# ---------------------------------------------------------------------------
# Naval status view - ship-to-ship combat dashboard
# ---------------------------------------------------------------------------

def naval_status_view(
    player_hull: int,
    player_hull_max: int,
    player_crew: int,
    player_cannons: int,
    enemy_hull: int,
    enemy_hull_max: int,
    enemy_crew: int,
    enemy_cannons: int,
    boarding_progress: int,
    boarding_threshold: int,
    turn: int,
) -> Panel:
    """Naval combat dashboard: two-column ship comparison with boarding progress."""
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("", style="dim", width=10)
    table.add_column("Your Ship", justify="left")
    table.add_column("Enemy Ship", justify="left")

    table.add_row("Hull", _hp_bar(player_hull, player_hull_max), _hp_bar(enemy_hull, enemy_hull_max))
    table.add_row("Crew", f"[bold]{player_crew}[/bold]", f"[bold]{enemy_crew}[/bold]")
    table.add_row("Cannons", f"[bold]{player_cannons}[/bold]", f"[bold]{enemy_cannons}[/bold]")

    lines: list[str] = []
    lines.append("")
    lines.append(f"  Boarding: {_boarding_bar(boarding_progress, boarding_threshold)}")
    lines.append("")
    lines.append("[bold]Actions:[/bold]  [cyan][broadside][/cyan]  [yellow][chain shot][/yellow]  [red][board][/red]  [green][repair][/green]  [dim][disengage][/dim]")

    return Panel(
        Group(table, Text.from_markup("\n".join(lines))),
        title=f"[bold]Naval Combat — Turn {turn}[/bold]",
        border_style="blue",
    )


# ---------------------------------------------------------------------------
# Naval round view - what just happened in naval combat
# ---------------------------------------------------------------------------

def naval_round_view(round_data: dict) -> Panel:
    """Naval combat round recap: actions, damage, crew changes, flavor."""
    turn = round_data.get("turn", "?")
    player_action = round_data.get("player_action", "unknown")
    enemy_action = round_data.get("enemy_action", "unknown")
    damage_dealt = round_data.get("damage_dealt", 0)
    damage_received = round_data.get("damage_received", 0)
    crew_lost = round_data.get("crew_lost", 0)
    enemy_crew_lost = round_data.get("enemy_crew_lost", 0)
    flavor = round_data.get("flavor", "")

    lines: list[str] = []
    lines.append(f"[bold]Turn {turn}[/bold]")
    lines.append("")
    lines.append(f"  You:    [cyan]{player_action}[/cyan]")
    lines.append(f"  Enemy:  [red]{enemy_action}[/red]")
    lines.append("")

    if damage_dealt > 0:
        lines.append(f"  Damage dealt:     [green]{damage_dealt}[/green]")
    if damage_received > 0:
        lines.append(f"  Damage received:  [red]{damage_received}[/red]")
    if crew_lost > 0:
        lines.append(f"  Crew lost:        [red]-{crew_lost}[/red]")
    if enemy_crew_lost > 0:
        lines.append(f"  Enemy crew lost:  [green]-{enemy_crew_lost}[/green]")

    if flavor:
        lines.append("")
        lines.append(f"[italic]{flavor}[/italic]")

    return Panel(
        "\n".join(lines),
        title=f"[bold]Round {turn} Result[/bold]",
        border_style="dim",
    )


# ---------------------------------------------------------------------------
# Combat status view - personal combat dashboard
# ---------------------------------------------------------------------------

def combat_status_view(
    player_hp: int,
    player_hp_max: int,
    player_stamina: int,
    player_stamina_max: int,
    opponent_hp: int,
    opponent_hp_max: int,
    opponent_name: str,
    ammo: int,
    throwing: int,
    active_style: str,
    injuries: list[dict],
    available_actions: list[str],
    turn: int,
) -> Panel:
    """Personal combat dashboard: HP, stamina, injuries, ammo, style, actions."""
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("", style="dim", width=10)
    table.add_column("You", justify="left")
    table.add_column(opponent_name, justify="left")

    table.add_row("HP", _hp_bar(player_hp, player_hp_max), _hp_bar(opponent_hp, opponent_hp_max))
    table.add_row(
        "Stamina",
        _stamina_bar(player_stamina, player_stamina_max),
        "",
    )

    lines: list[str] = []
    lines.append("")
    lines.append(f"  Style:     [bold cyan]{active_style}[/bold cyan]")
    lines.append(f"  Ammo:      [bold]{ammo}[/bold]")
    lines.append(f"  Throwing:  [bold]{throwing}[/bold]")

    if injuries:
        lines.append("")
        lines.append("[bold]Active Injuries:[/bold]")
        for inj in injuries:
            name = inj.get("name", "wound")
            severity = inj.get("severity", "minor")
            color = _severity_color(severity)
            effect = inj.get("effect", "")
            lines.append(f"  [{color}]* {name} ({severity})[/{color}] {effect}")

    lines.append("")
    actions_str = "  ".join(f"[cyan][{a}][/cyan]" for a in available_actions)
    lines.append(f"[bold]Actions:[/bold]  {actions_str}")

    return Panel(
        Group(table, Text.from_markup("\n".join(lines))),
        title=f"[bold]Combat — Turn {turn}[/bold]",
        border_style="red",
    )


# ---------------------------------------------------------------------------
# Combat round view - what just happened in personal combat
# ---------------------------------------------------------------------------

def combat_round_view(round_data: dict) -> Panel:
    """Personal combat round recap: actions, damage, stamina, injuries, style."""
    turn = round_data.get("turn", "?")
    player_action = round_data.get("player_action", "unknown")
    opponent_action = round_data.get("opponent_action", "unknown")
    damage_dealt = round_data.get("damage_dealt", 0)
    damage_received = round_data.get("damage_received", 0)
    stamina_spent = round_data.get("stamina_spent", 0)
    stamina_recovered = round_data.get("stamina_recovered", 0)
    injury_inflicted = round_data.get("injury_inflicted", "")
    style_effect = round_data.get("style_effect", "")
    flavor = round_data.get("flavor", "")

    lines: list[str] = []
    lines.append(f"[bold]Turn {turn}[/bold]")
    lines.append("")
    lines.append(f"  You:       [cyan]{player_action}[/cyan]")
    lines.append(f"  Opponent:  [red]{opponent_action}[/red]")
    lines.append("")

    if damage_dealt > 0:
        lines.append(f"  Damage dealt:     [green]{damage_dealt}[/green]")
    if damage_received > 0:
        lines.append(f"  Damage received:  [red]{damage_received}[/red]")
    if stamina_spent > 0:
        lines.append(f"  Stamina spent:    [yellow]-{stamina_spent}[/yellow]")
    if stamina_recovered > 0:
        lines.append(f"  Stamina recovered:[green]+{stamina_recovered}[/green]")

    if injury_inflicted:
        lines.append("")
        lines.append(f"  [bold red]Injury inflicted: {injury_inflicted}[/bold red]")

    if style_effect:
        lines.append(f"  [italic cyan]{style_effect}[/italic cyan]")

    if flavor:
        lines.append("")
        lines.append(f"[italic]{flavor}[/italic]")

    return Panel(
        "\n".join(lines),
        title=f"[bold]Round {turn} Result[/bold]",
        border_style="dim",
    )


# ---------------------------------------------------------------------------
# Training view - martial training at port
# ---------------------------------------------------------------------------

def training_view(
    port_name: str,
    masters: list[dict],
    captain_styles: list[str],
    captain_silver: int,
) -> Panel:
    """Training screen: available masters, costs, prerequisites, known styles."""
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Master", style="bold")
    table.add_column("Style")
    table.add_column("Region", style="dim")
    table.add_column("Cost", justify="right")
    table.add_column("Days", justify="center")
    table.add_column("Requires")
    table.add_column("", width=3)

    for m in masters:
        style_name = m.get("style", "unknown")
        known = style_name.lower() in [s.lower() for s in captain_styles]
        cost = m.get("cost", 0)
        can_afford = captain_silver >= cost

        cost_str = _silver(cost)
        if not can_afford and not known:
            cost_str = f"[red]{cost:,}[/red] silver"

        prereqs = m.get("prerequisites", "none")
        status = "[green]Y[/green]" if known else ""

        table.add_row(
            m.get("name", "?"),
            f"[bold]{style_name}[/bold]" if not known else f"[dim]{style_name}[/dim]",
            m.get("region", ""),
            cost_str,
            str(m.get("days", "?")),
            prereqs if not known else "[dim]—[/dim]",
            status,
        )

    lines: list[str] = []
    lines.append("")
    lines.append(f"  Your silver: {_silver(captain_silver)}")

    # Show dialog from first master if available
    for m in masters:
        dialog = m.get("dialog", "")
        if dialog:
            lines.append("")
            lines.append(f'  [italic]"{dialog}"[/italic] — {m.get("name", "a master")}')
            break

    return Panel(
        Group(table, Text.from_markup("\n".join(lines))),
        title=f"[bold]Training Grounds — {port_name}[/bold]",
        border_style="cyan",
    )


# ---------------------------------------------------------------------------
# Injuries view - current wounds and healing
# ---------------------------------------------------------------------------

def injuries_view(injuries_list: list[dict]) -> Panel:
    """Injuries screen: wounds, severity, healing progress, treatment status."""
    if not injuries_list:
        return Panel(
            "[dim]No active injuries. You're in good health.[/dim]",
            title="[bold]Injuries[/bold]",
            border_style="green",
        )

    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Injury", style="bold")
    table.add_column("Severity")
    table.add_column("Body Part")
    table.add_column("Effect")
    table.add_column("Healing", justify="center")
    table.add_column("Treated", justify="center")

    for inj in injuries_list:
        severity = inj.get("severity", "minor")
        color = _severity_color(severity)
        is_permanent = severity.lower() == "permanent"

        name = inj.get("name", "wound")
        name_str = f"[{color}]{name}[/{color}]"
        if is_permanent:
            name_str = f"[bold {color}]! {name}[/bold {color}]"

        severity_str = f"[{color}]{severity}[/{color}]"

        healing_progress = inj.get("healing_progress", 0)
        healing_max = inj.get("healing_max", 1)
        if is_permanent:
            healing_str = "[dim]—[/dim]"
        else:
            healing_str = _hp_bar(healing_progress, healing_max, width=8)

        treated = inj.get("treated", False)
        treated_str = "[green]Y[/green]" if treated else "[red]N[/red]"
        if is_permanent:
            treated_str = "[dim]—[/dim]"

        table.add_row(
            name_str,
            severity_str,
            inj.get("body_part", "?"),
            inj.get("effect", ""),
            healing_str,
            treated_str,
        )

    return Panel(table, title="[bold]Injuries[/bold]", border_style="yellow")


# ---------------------------------------------------------------------------
# Armory view - weapons and gear
# ---------------------------------------------------------------------------

def armory_view(
    weapons_available: list[dict],
    current_gear: dict,
) -> Panel:
    """Armory screen: available weapons, current loadout, ammo inventory."""
    # Weapons table
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Weapon", style="bold")
    table.add_column("Type")
    table.add_column("Damage", justify="center")
    table.add_column("Range", justify="center")
    table.add_column("Cost", justify="right")
    table.add_column("Region", style="dim")

    for w in weapons_available:
        cost = w.get("cost", 0)
        table.add_row(
            w.get("name", "?"),
            w.get("type", "?"),
            str(w.get("damage", "?")),
            w.get("range", "melee"),
            _silver(cost),
            w.get("region", ""),
        )

    # Current loadout
    lines: list[str] = []
    lines.append("")
    lines.append("[bold]Current Loadout[/bold]")

    melee = current_gear.get("melee", "fists")
    ranged = current_gear.get("ranged", "none")
    lines.append(f"  Melee:   [bold]{melee}[/bold]")
    lines.append(f"  Ranged:  [bold]{ranged}[/bold]")
    lines.append("")

    lines.append("[bold]Ammo Inventory[/bold]")
    ammo = current_gear.get("ammo", 0)
    throwing_raw = current_gear.get("throwing", 0)
    throwing = sum(throwing_raw.values()) if isinstance(throwing_raw, dict) else throwing_raw
    lines.append(f"  Shot/powder:  [bold]{ammo}[/bold]")
    lines.append(f"  Throwing:     [bold]{throwing}[/bold]")

    return Panel(
        Group(table, Text.from_markup("\n".join(lines))),
        title="[bold]Armory[/bold]",
        border_style="cyan",
    )


# ---------------------------------------------------------------------------
# Fight result view - outcome of a personal or naval combat
# ---------------------------------------------------------------------------

def fight_result_view(result_data: dict) -> Panel:
    """Fight outcome screen: victory/defeat banner, rewards, costs, summary."""
    outcome = result_data.get("outcome", "draw")
    silver_change = result_data.get("silver_change", 0)
    standing_change = result_data.get("standing_change", 0)
    injuries_sustained = result_data.get("injuries_sustained", [])
    rounds_fought = result_data.get("rounds_fought", 0)
    ammo_spent = result_data.get("ammo_spent", 0)

    # Banner
    if outcome == "victory":
        banner = "[bold green]=== VICTORY ===[/bold green]"
        border = "green"
    elif outcome == "defeat":
        banner = "[bold red]=== DEFEAT ===[/bold red]"
        border = "red"
    else:
        banner = "[bold yellow]=== DRAW ===[/bold yellow]"
        border = "yellow"

    lines: list[str] = []
    lines.append(banner)
    lines.append("")

    # Rewards / costs
    if silver_change != 0:
        lines.append(f"  Silver:   {_delta_str(silver_change)}")
    if standing_change != 0:
        lines.append(f"  Standing: {_delta_str(standing_change)}")

    # Injuries
    if injuries_sustained:
        lines.append("")
        lines.append("[bold]Injuries Sustained:[/bold]")
        for inj in injuries_sustained:
            if isinstance(inj, dict):
                name = inj.get("name", "wound")
                severity = inj.get("severity", "minor")
                color = _severity_color(severity)
                lines.append(f"  [{color}]* {name} ({severity})[/{color}]")
            else:
                lines.append(f"  [yellow]* {inj}[/yellow]")

    # Summary stats
    lines.append("")
    lines.append("[bold]Summary[/bold]")
    lines.append(f"  Rounds fought:  {rounds_fought}")
    if ammo_spent > 0:
        lines.append(f"  Ammo spent:     {ammo_spent}")

    return Panel(
        "\n".join(lines),
        title="[bold]Combat Result[/bold]",
        border_style=border,
    )


# ---------------------------------------------------------------------------
# Inventory view - unified personal gear display
# ---------------------------------------------------------------------------

def inventory_view(gear_data: dict) -> Panel:
    """Unified inventory: worn gear, ranged, ship upgrades, injuries, cargo summary.

    gear_data keys:
      armor_name, armor_dr, armor_type,
      melee_name, melee_bonus,
      active_style, style_special,
      firearm_name, firearm_ammo,
      mechanical_name, mechanical_ammo,
      throwing_summary (list of {name, count}),
      injuries (list of {name, severity, healing}),
      ship_upgrades (list of str),
      cargo_used, cargo_capacity,
      silver
    """
    sections: list[str] = []

    # --- Worn equipment ---
    sections.append("[bold cyan]Worn Equipment[/bold cyan]")
    armor = gear_data.get("armor_name", "None")
    armor_dr = gear_data.get("armor_dr", 0)
    armor_type = gear_data.get("armor_type", "")
    if armor != "None":
        sections.append(f"  Armor:    [bold]{armor}[/bold] ({armor_type}, DR {armor_dr})")
    else:
        sections.append("  Armor:    [dim]None[/dim]")

    melee = gear_data.get("melee_name", "Fists")
    melee_bonus = gear_data.get("melee_bonus", "")
    if melee != "Fists":
        sections.append(f"  Weapon:   [bold]{melee}[/bold] ({melee_bonus})")
    else:
        sections.append("  Weapon:   [dim]Fists (unarmed)[/dim]")

    style = gear_data.get("active_style", "None")
    style_special = gear_data.get("style_special", "")
    if style != "None":
        sections.append(f"  Style:    [bold]{style}[/bold] — {style_special}")
    else:
        sections.append("  Style:    [dim]None[/dim]")

    sections.append("")

    # --- Ranged gear ---
    sections.append("[bold cyan]Ranged Gear[/bold cyan]")
    firearm = gear_data.get("firearm_name", "None")
    firearm_ammo = gear_data.get("firearm_ammo", 0)
    if firearm != "None":
        sections.append(f"  Firearm:    [bold]{firearm}[/bold] ({firearm_ammo} rounds)")
    else:
        sections.append("  Firearm:    [dim]None[/dim]")

    mechanical = gear_data.get("mechanical_name", "None")
    mechanical_ammo = gear_data.get("mechanical_ammo", 0)
    if mechanical != "None":
        sections.append(f"  Mechanical: [bold]{mechanical}[/bold] ({mechanical_ammo} bolts)")
    else:
        sections.append("  Mechanical: [dim]None[/dim]")

    throwing = gear_data.get("throwing_summary", [])
    if throwing:
        for t in throwing:
            sections.append(f"  Thrown:     [bold]{t['name']}[/bold] x{t['count']}")
    else:
        sections.append("  Thrown:     [dim]None[/dim]")

    sections.append("")

    # --- Injuries ---
    injuries = gear_data.get("injuries", [])
    if injuries:
        sections.append("[bold yellow]Injuries[/bold yellow]")
        for inj in injuries:
            healing = inj.get("healing", "")
            severity = inj.get("severity", "")
            color = "red" if severity in ("crippling", "permanent") else "yellow"
            sections.append(f"  [{color}]{inj['name']}[/{color}] — {healing}")
    else:
        sections.append("[bold green]No Injuries[/bold green]")

    sections.append("")

    # --- Ship upgrades ---
    upgrades = gear_data.get("ship_upgrades", [])
    if upgrades:
        sections.append("[bold cyan]Ship Upgrades[/bold cyan]")
        for u in upgrades:
            sections.append(f"  [bold]{u}[/bold]")
    else:
        sections.append("[bold cyan]Ship Upgrades[/bold cyan]")
        sections.append("  [dim]None installed[/dim]")

    sections.append("")

    # --- Cargo summary ---
    cargo_used = gear_data.get("cargo_used", 0)
    cargo_cap = gear_data.get("cargo_capacity", 0)
    silver = gear_data.get("silver", 0)
    ratio = cargo_used / cargo_cap if cargo_cap > 0 else 0
    filled = int(ratio * 10)
    empty = 10 - filled
    color = "green" if ratio < 0.7 else "yellow" if ratio < 0.9 else "red"
    bar = f"[{color}]{'#' * filled}{'-' * empty}[/{color}]"
    sections.append(f"[bold]Cargo:[/bold] {bar} {int(cargo_used)}/{cargo_cap}")
    sections.append(f"[bold]Silver:[/bold] [yellow]{silver:,}[/yellow]")

    return Panel(
        "\n".join(sections),
        title="[bold]Inventory[/bold]",
        border_style="cyan",
    )


# ---------------------------------------------------------------------------
# Merchant view - NPC shop display
# ---------------------------------------------------------------------------

def merchant_list_view(merchants: list[dict], port_name: str) -> Panel:
    """List merchants at a port with name, title, personality."""
    if not merchants:
        return Panel(
            f"[dim]No merchants at {port_name}.[/dim]",
            title="[bold]Merchants[/bold]",
            border_style="dim",
        )

    lines: list[str] = []
    for m in merchants:
        lines.append(f"  [bold]{m['name']}[/bold] — {m['title']}")
        lines.append(f"    [italic]{m['greeting']}[/italic]")
        lines.append(f"    Sells: {', '.join(m['inventory_types'])}  |  Markup: +{int((m['markup'] - 1) * 100)}%")
        lines.append(f"    [dim]portlight merchant {m['id']}[/dim]")
        lines.append("")

    return Panel(
        "\n".join(lines),
        title=f"[bold]Merchants — {port_name}[/bold]",
        border_style="cyan",
    )


def merchant_shop_view(
    merchant_name: str,
    merchant_greeting: str,
    inventory: list[dict],
    captain_silver: int,
) -> Panel:
    """A merchant's shop inventory with prices."""
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Item", style="bold")
    table.add_column("Type")
    table.add_column("Info")
    table.add_column("Cost", justify="right")
    table.add_column("", width=3)

    for item in inventory:
        cost = item.get("silver_cost", 0)
        can_afford = captain_silver >= cost
        afford_mark = "[green]Y[/green]" if can_afford else "[red]N[/red]"
        table.add_row(
            item.get("name", "?"),
            item.get("item_type", "?"),
            item.get("description", ""),
            _silver(cost),
            afford_mark,
        )

    greeting = f'[italic]"{merchant_greeting}"[/italic]'

    return Panel(
        Group(Text.from_markup(greeting + "\n"), table),
        title=f"[bold]{merchant_name}'s Shop[/bold]",
        border_style="cyan",
    )


# ---------------------------------------------------------------------------
# Loot view - drops after combat victory
# ---------------------------------------------------------------------------

def loot_view(loot_messages: list[str]) -> Panel:
    """Display loot drops after a combat victory."""
    if not loot_messages:
        return Panel(
            "[dim]No loot found.[/dim]",
            title="[bold]Spoils[/bold]",
            border_style="dim",
        )

    lines = ["[bold]You search the defeated pirate's belongings...[/bold]", ""]
    for msg in loot_messages:
        lines.append(f"  {msg}")

    return Panel(
        "\n".join(lines),
        title="[bold]Spoils of Victory[/bold]",
        border_style="green",
    )
