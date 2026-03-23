"""Portlight TUI CSS theme — dark maritime palette.

Colors:
  Deep ocean (#0a1628) for backgrounds
  Sea foam (#2a9d8f) for primary accents
  Gold (#e9c46a) for silver/wealth
  Coral red (#e76f51) for danger
  Storm gray (#264653) for panels
"""

# ASCII ship art for the sidebar header
SHIP_ART = """\
[dim]     ~  ~[/dim]
[bold cyan]   |\\[/bold cyan]
[bold cyan]   | \\[/bold cyan]
[bold cyan]   |  \\[/bold cyan]
[dim cyan]  _|___\\__[/dim cyan]
[dim cyan] /________\\[/dim cyan]
[dim blue]~~~~~~~~~~~~~[/dim blue]"""

SHIP_ART_SMALL = "[dim blue]~[/dim blue][bold cyan]|\\[/bold cyan][dim blue]~~[/dim blue]"

# Compass rose for routes view
COMPASS_ROSE = """\
[bold cyan]        N[/bold cyan]
[dim]        |[/dim]
[bold cyan]   NW[/bold cyan] [dim]--+--[/dim] [bold cyan]NE[/bold cyan]
[dim]        |[/dim]
[bold cyan] W[/bold cyan] [dim]----+----[/dim] [bold cyan]E[/bold cyan]
[dim]        |[/dim]
[bold cyan]   SW[/bold cyan] [dim]--+--[/dim] [bold cyan]SE[/bold cyan]
[dim]        |[/dim]
[bold cyan]        S[/bold cyan]"""

# Region banners
REGION_BADGES = {
    "mediterranean": "[on dark_blue] [bold]MED[/bold] [/on dark_blue]",
    "north_atlantic": "[on #264653] [bold]ATL[/bold] [/on #264653]",
    "west_africa": "[on #6b4226] [bold]AFR[/bold] [/on #6b4226]",
    "east_indies": "[on #8b0000] [bold]IND[/bold] [/on #8b0000]",
    "south_seas": "[on #006d6f] [bold]SEA[/bold] [/on #006d6f]",
}

# Wave frames for animation
WAVE_FRAMES = [
    "[dim blue]~-~-~-~-~-~-~-~-~-~-~[/dim blue]",
    "[dim blue]-~-~-~-~-~-~-~-~-~-~-[/dim blue]",
    "[dim blue]~-~-~-~-~-~-~-~-~-~-~[/dim blue]",
    "[dim blue]-~-~-~-~-~-~-~-~-~-~-[/dim blue]",
]

# Visual bar characters
BAR_FULL = "[bold green]\u2588[/bold green]"
BAR_MED = "[yellow]\u2588[/yellow]"
BAR_LOW = "[red]\u2588[/red]"
BAR_EMPTY = "[dim]\u2591[/dim]"


def render_bar(current: int, maximum: int, width: int = 12) -> str:
    """Render a visual bar with colored blocks."""
    if maximum <= 0:
        return BAR_EMPTY * width
    ratio = current / maximum
    filled = int(ratio * width)
    empty = width - filled

    if ratio > 0.6:
        char = BAR_FULL
    elif ratio > 0.3:
        char = BAR_MED
    else:
        char = BAR_LOW

    return char * filled + BAR_EMPTY * empty


def render_mini_bar(current: int, maximum: int, width: int = 8) -> str:
    """Compact bar for sidebar use."""
    return render_bar(current, maximum, width)


def silver_display(amount: int) -> str:
    """Stylized silver amount."""
    if amount >= 1000:
        return f"[bold yellow]{amount:,}[/bold yellow]"
    elif amount >= 100:
        return f"[yellow]{amount:,}[/yellow]"
    elif amount > 0:
        return f"[dim yellow]{amount}[/dim yellow]"
    return "[bold red]0[/bold red]"


def danger_indicator(danger: float) -> str:
    """Visual danger level with skulls."""
    if danger >= 0.20:
        return "[bold red]\u2620\u2620\u2620[/bold red]"
    elif danger >= 0.16:
        return "[red]\u2620\u2620[/red]"
    elif danger >= 0.12:
        return "[yellow]\u2620[/yellow]"
    elif danger >= 0.08:
        return "[dim]\u00b7[/dim]"
    return "[green]\u2713[/green]"


APP_CSS = """
Screen {
    background: #0a1628;
    color: #c8d6e5;
}

/* Sidebar — deep ocean panel */
#status-sidebar {
    width: 30;
    height: 100%;
    dock: left;
    border-right: thick #2a9d8f;
    padding: 1;
    background: #0d1f3c;
}

#sidebar-ship-art {
    height: auto;
    text-align: center;
    margin-bottom: 1;
}

#sidebar-captain {
    height: auto;
}

#sidebar-ship {
    height: auto;
    margin-top: 1;
}

#sidebar-location {
    height: auto;
    margin-top: 1;
    border-top: dashed #264653;
    padding-top: 1;
}

#sidebar-wave {
    dock: bottom;
    height: 1;
    text-align: center;
}

/* Content area */
#content-area {
    height: 1fr;
    padding: 0 1;
}

/* Tab bar — sea foam accent */
#tab-bar {
    dock: bottom;
    height: 1;
    background: #0d1f3c;
    color: #c8d6e5;
    padding: 0 1;
    border-top: tall #264653;
}

/* Footer keybinding bar */
Footer {
    background: #0d1f3c;
    color: #576574;
}

/* View panels */
.view-panel {
    height: 1fr;
    overflow-y: auto;
}

/* Market DataTable */
DataTable {
    height: 1fr;
    background: #0a1628;
}

/* Combat panels */
#combat-you {
    width: 1fr;
    height: auto;
    border: tall #2a9d8f;
    padding: 1;
    background: #0d1f3c;
}

#combat-enemy {
    width: 1fr;
    height: auto;
    border: tall #e76f51;
    padding: 1;
    background: #1a0a0a;
}

#combat-log {
    height: 1fr;
    overflow-y: auto;
    padding: 0 1;
    border-top: tall #264653;
    background: #0a1628;
}

/* Modal dialogs */
#input-area {
    width: 60;
    height: auto;
    margin: 4;
    padding: 2;
    background: #0d1f3c;
    border: tall #2a9d8f;
}

/* Splash screen */
#splash-art {
    text-align: center;
    margin: 2;
}

/* Voyage progress */
#voyage-bar {
    height: auto;
    margin: 1 0;
}

#voyage-log {
    height: 1fr;
    overflow-y: auto;
    padding: 0 1;
    background: #0d1f3c;
    border: tall #264653;
}

/* Route list */
#route-list {
    height: 1fr;
}

/* Contract board */
.contract-urgent {
    color: #e76f51;
    text-style: bold;
}

.contract-normal {
    color: #c8d6e5;
}

.contract-done {
    color: #2a9d8f;
}

/* Help panel */
#help-panel {
    padding: 2;
    background: #0d1f3c;
    border: tall #264653;
}

/* Encounter screen */
.hidden {
    display: none;
}

#encounter-header {
    height: auto;
    padding: 1;
    border: tall #e76f51;
    background: #1a0a0a;
}

#ship-panels {
    height: auto;
}

#ship-player {
    width: 1fr;
    height: auto;
    border: tall #2a9d8f;
    padding: 1;
    background: #0d1f3c;
}

#ship-enemy {
    width: 1fr;
    height: auto;
    border: tall #e76f51;
    padding: 1;
    background: #1a0a0a;
}

#combatant-panels {
    height: auto;
}

#combatant-player {
    width: 1fr;
    height: auto;
    border: tall #2a9d8f;
    padding: 1;
    background: #0d1f3c;
}

#combatant-enemy {
    width: 1fr;
    height: auto;
    border: tall #e76f51;
    padding: 1;
    background: #1a0a0a;
}

#encounter-log {
    height: 1fr;
    overflow-y: auto;
    padding: 0 1;
    border-top: tall #264653;
    background: #0a1628;
}

#encounter-actions {
    dock: bottom;
    height: 1;
    background: #0d1f3c;
    padding: 0 1;
}
"""
