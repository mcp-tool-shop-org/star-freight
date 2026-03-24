"""Star Freight TUI CSS theme — deep void palette.

Colors:
  Void black (#0a0e1a) for backgrounds
  Star white (#e8e8e8) for primary text
  Shield blue (#4090e0) for accents
  Credit gold (#f0c040) for currency/wealth
  Alert red (#e05050) for danger
  Hull gray (#1a1e2a) for panels

Civilization colors:
  Keth amber (#d0a040)
  Veshan crimson (#c04040)
  Orryn teal (#40b0b0)
  Reach purple (#9060c0)
  Compact blue (#4090e0)
"""

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
    """Compact bar for header use."""
    return render_bar(current, maximum, width)


def credits_display(amount: int) -> str:
    """Stylized credits amount with \u20a1 symbol."""
    if amount >= 1000:
        return f"[bold #f0c040]{amount:,}\u20a1[/bold #f0c040]"
    elif amount >= 100:
        return f"[#f0c040]{amount:,}\u20a1[/#f0c040]"
    elif amount > 0:
        return f"[dim #f0c040]{amount}\u20a1[/dim #f0c040]"
    return "[bold red]0\u20a1[/bold red]"


# Keep old name as alias for any remaining internal references
silver_display = credits_display


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


# Legacy stubs — still imported by old Portlight screens (encounter, routes)
# These will be removed when the old screens are fully retired.
REGION_BADGES: dict[str, str] = {}
SHIP_ART = ""
SHIP_ART_SMALL = ""
WAVE_FRAMES = ["", ""]


APP_CSS = """
Screen {
    background: #0a0e1a;
    color: #e8e8e8;
}

/* Captain pressure bar — top header */
#captain-bar {
    width: 100%;
    height: auto;
    dock: top;
    padding: 0 1;
    background: #12162a;
    border-bottom: tall #1a1e2a;
}

/* Content area */
#content-area {
    height: 1fr;
    padding: 0 1;
}

/* Tab bar — shield blue accent */
#tab-bar {
    dock: bottom;
    height: 1;
    background: #12162a;
    color: #e8e8e8;
    padding: 0 1;
    border-top: tall #1a1e2a;
}

/* Footer keybinding bar */
Footer {
    background: #12162a;
    color: #606060;
}

/* View panels */
.view-panel {
    height: 1fr;
    overflow-y: auto;
}

/* Market DataTable */
DataTable {
    height: 1fr;
    background: #0a0e1a;
}

/* Combat panels */
#combat-you {
    width: 1fr;
    height: auto;
    border: tall #4090e0;
    padding: 1;
    background: #12162a;
}

#combat-enemy {
    width: 1fr;
    height: auto;
    border: tall #e05050;
    padding: 1;
    background: #1a0a0a;
}

#combat-log {
    height: 1fr;
    overflow-y: auto;
    padding: 0 1;
    border-top: tall #1a1e2a;
    background: #0a0e1a;
}

/* Modal dialogs */
#input-area {
    width: 60;
    height: auto;
    margin: 4;
    padding: 2;
    background: #12162a;
    border: tall #4090e0;
}

/* Splash screen */
#splash-art {
    text-align: center;
    margin: 2;
}

/* Route list */
#route-list {
    height: 1fr;
}

/* Contract board */
.contract-urgent {
    color: #e05050;
    text-style: bold;
}

.contract-normal {
    color: #e8e8e8;
}

.contract-done {
    color: #40c060;
}

/* Help panel */
#help-panel {
    padding: 2;
    background: #12162a;
    border: tall #1a1e2a;
}

/* Encounter screen */
.hidden {
    display: none;
}

#encounter-header {
    height: auto;
    padding: 1;
    border: tall #e05050;
    background: #1a0a0a;
}

#ship-panels {
    height: auto;
}

#ship-player {
    width: 1fr;
    height: auto;
    border: tall #4090e0;
    padding: 1;
    background: #12162a;
}

#ship-enemy {
    width: 1fr;
    height: auto;
    border: tall #e05050;
    padding: 1;
    background: #1a0a0a;
}

#combatant-panels {
    height: auto;
}

#combatant-player {
    width: 1fr;
    height: auto;
    border: tall #4090e0;
    padding: 1;
    background: #12162a;
}

#combatant-enemy {
    width: 1fr;
    height: auto;
    border: tall #e05050;
    padding: 1;
    background: #1a0a0a;
}

#encounter-log {
    height: 1fr;
    overflow-y: auto;
    padding: 0 1;
    border-top: tall #1a1e2a;
    background: #0a0e1a;
}

#encounter-actions {
    dock: bottom;
    height: 1;
    background: #12162a;
    padding: 0 1;
}
"""
